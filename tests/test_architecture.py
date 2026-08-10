from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_architecture_surfaces_cover_requested_paths() -> None:
    from paradev.sdk import get_architecture_spec

    spec = get_architecture_spec()
    identifiers = {surface.identifier for surface in spec.surfaces}

    assert {
        "sdk",
        "mcp",
        "cli",
        "rest",
        "openapi",
        "bundle",
        "frontend",
        "desktop",
        "lsp",
        "vscode",
    } <= identifiers
    assert spec.surface("sdk").runtime == "python"
    assert spec.surface("bundle").runtime == "python-wheel-loopback"
    assert spec.surface("desktop").runtime == "python-loopback-system-webview"
    assert [
        "python-backend",
        "sdk-api",
        "rest-api",
        "openapi-contract",
        "python-wheel-loopback-host",
        "typescript-frontend",
        "system-webview",
        "desktop-app",
    ] in spec.path_chains()
    assert all(path[1] == "sdk-api" for path in spec.path_chains())


def test_architecture_api_table_lists_public_graph_surface() -> None:
    from typing_extensions import is_typeddict

    from paradev.sdk import (
        ARCHITECTURE_API_TABLE_ROWS,
        ARCHITECTURE_API_TABLE_SCHEMA,
        ArchitectureApiRow,
        ArchitectureApiTable,
        get_architecture_api_table,
        render_architecture_api_reference_markdown,
    )

    table = get_architecture_api_table()
    rows = table["rows"]
    symbols = [row["symbol"] for row in rows]
    reference = render_architecture_api_reference_markdown()

    assert is_typeddict(ArchitectureApiRow)
    assert is_typeddict(ArchitectureApiTable)
    assert table["schema"] == ARCHITECTURE_API_TABLE_SCHEMA
    assert table["row_count"] == len(ARCHITECTURE_API_TABLE_ROWS) == len(rows)
    assert tuple(rows) == ARCHITECTURE_API_TABLE_ROWS
    assert set(ArchitectureApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "inputs",
        "returns",
        "raises",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(ArchitectureApiTable.__annotations__) == {
        "schema",
        "row_count",
        "surface_index",
        "rows",
    }
    assert symbols[:3] == ["SurfaceSpec", "SurfaceSpec.to_dict", "ArchitectureSpec"]
    assert "get_architecture_spec" in table["surface_index"]["sdk"]
    assert "get_architecture_api_table" in table["surface_index"]["sdk"]
    assert "paradev architecture --api-table" in table["surface_index"]["cli"]
    assert "GET /architecture" in table["surface_index"]["rest"]
    assert table["surface_index"]["mcp"] == [
        "list_surfaces",
        "describe_architecture",
        "architecture_api",
    ]
    assert rows[0]["doc_page"] == "docs/architecture/interfaces.md"
    assert rows[-1]["registry_seam"] == "MCP tool registry"
    assert reference.startswith("# Architecture API Reference\n")
    assert "Generated from `paradev.sdk.get_architecture_api_table()`." in reference
    assert "| `sdk` | 10 | `SurfaceSpec`, `SurfaceSpec.to_dict`, `ArchitectureSpec`," in reference
    assert "| `paradev architecture --api-table` | `command projection` | `cli` | `cli` | `--json` | `ArchitectureApiTable` |" in reference
    manual = Path("docs/user-manual/architecture-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_architecture_api_table()["rows"][0]["symbol"] == "SurfaceSpec"


def test_sdk_api_table_lists_facade_exports() -> None:
    from typing_extensions import is_typeddict

    import paradev.sdk as sdk
    from paradev.sdk import (
        PROJECT_API_TABLE_SCHEMA,
        SDK_API_TABLE_SCHEMA,
        ProjectApiRow,
        ProjectApiTable,
        SdkApiRow,
        SdkApiTable,
        get_project_api_table,
        get_sdk_api_table,
        render_project_api_reference_markdown,
        render_sdk_api_reference_markdown,
    )

    table = get_sdk_api_table()
    rows = table["rows"]
    symbols = [row["symbol"] for row in rows]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_sdk_api_reference_markdown()

    assert is_typeddict(SdkApiRow)
    assert is_typeddict(SdkApiTable)
    assert table["schema"] == SDK_API_TABLE_SCHEMA
    assert table["row_count"] == len(sdk.__all__) == len(rows) == 138
    assert symbols == list(sdk.__all__)
    assert len(symbols) == len(set(symbols))
    assert set(SdkApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(SdkApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert {module: len(symbols) for module, symbols in table["module_index"].items()} == {
        "architecture": 10,
        "project": 40,
        "frontend_api": 39,
        "games.hoi4.keywords": 2,
        "lsp": 19,
        "project_api": 6,
        "pdx": 12,
        "api": 6,
        "desktop.local": 4,
    }
    assert table["feature_index"]["ai-chat"] == [
        "desktop_chat",
        "desktop_chat_profiles",
        "desktop_reset_chat_profile",
        "desktop_write_chat_profile",
    ]
    assert table["feature_index"]["api-table"] == [
        "SDK_API_TABLE_SCHEMA",
        "SdkApiRow",
        "SdkApiTable",
        "get_sdk_api_selection",
        "get_sdk_api_table",
        "render_sdk_api_reference_markdown",
    ]
    assert table["feature_index"]["project-api"] == [
        "PROJECT_API_TABLE_SCHEMA",
        "ProjectApiRow",
        "ProjectApiTable",
        "get_project_api_selection",
        "get_project_api_table",
        "render_project_api_reference_markdown",
    ]
    assert table["feature_index"]["inspections"] == [
        "PROJECT_INSPECTION_INDEX_CATALOG",
        "PROJECT_INSPECTIONS_SCHEMA",
        "ProjectInspectionContract",
        "ProjectInspectionIndex",
        "ProjectInspectionIndexCatalogRow",
        "ProjectInspectionProjectContract",
        "ProjectInspectionRow",
        "get_project_inspection_filter_kinds",
        "get_project_inspection_contract",
        "get_project_inspection_index_catalog",
        "get_project_inspection_kinds",
        "get_project_inspection_row",
        "get_project_inspection_selection",
        "render_project_inspection_reference_markdown",
    ]
    assert len(table["kind_index"]["function"]) == 68
    assert len(table["kind_index"]["schema constant"]) == 43
    assert len(table["kind_index"]["TypedDict"]) == 15
    assert row_by_symbol["Project"]["module"] == "project"
    assert row_by_symbol["Project"]["feature"] == "projects"
    assert row_by_symbol["project_source_mutation_lock"]["module"] == "project"
    assert row_by_symbol["project_source_mutation_lock"]["feature"] == "projects"
    assert row_by_symbol["project_source_mutation_lock"]["returns"] == "Iterator[None]"
    assert row_by_symbol["PROJECT_API_TABLE_SCHEMA"]["value"] == PROJECT_API_TABLE_SCHEMA
    assert row_by_symbol["PROJECT_API_TABLE_SCHEMA"]["module"] == "project_api"
    assert row_by_symbol["MODULE_BATCH_EDIT_REQUEST_SCHEMA"]["value"] == "paradev.module.batch_edit_request.v1"
    assert row_by_symbol["MODULE_BATCH_EDIT_REQUEST_SCHEMA"]["feature"] == "modules"
    assert row_by_symbol["MODULE_BATCH_EDIT_SCHEMA"]["value"] == "paradev.module.batch_edit.v1"
    assert row_by_symbol["MODULE_BATCH_EDIT_SCHEMA"]["feature"] == "modules"
    assert row_by_symbol["MODULE_ASSET_SCHEMA"]["value"] == ("paradev.module.asset.v1")
    assert row_by_symbol["MODULE_ASSET_SCHEMA"]["feature"] == "modules"
    assert row_by_symbol["PROJECT_SOURCE_BINARY_SCHEMA"]["value"] == ("paradev.project.source-binary.v1")
    assert row_by_symbol["PROJECT_SOURCE_BINARY_SCHEMA"]["feature"] == "projects"
    assert row_by_symbol["ProjectApiRow"]["returns"] == "TypedDict schema"
    assert row_by_symbol["ProjectApiTable"]["doc_page"] == "docs/user-manual/project-api-reference.md"
    assert row_by_symbol["get_project_api_table"]["returns"] == "ProjectApiTable"
    assert row_by_symbol["render_project_api_reference_markdown"]["returns"] == "str"
    assert row_by_symbol["ProjectInspectionContract"]["feature"] == "inspections"
    assert row_by_symbol["get_project_inspection_selection"]["returns"] == "ProjectInspectionProjectContract | ProjectInspectionRow | list[str]"
    assert row_by_symbol["get_frontend_api_contract"]["registry_seam"] == "frontend API operation registry"
    assert row_by_symbol["get_frontend_api_selection"]["returns"] == "dict[str, object] | list[str]"
    assert row_by_symbol["SDK_API_TABLE_SCHEMA"]["value"] == SDK_API_TABLE_SCHEMA
    assert row_by_symbol["get_sdk_api_table"]["returns"] == "SdkApiTable"
    assert row_by_symbol["desktop_chat"]["module"] == "desktop.local"
    assert row_by_symbol["desktop_chat"]["feature"] == "ai-chat"
    assert row_by_symbol["desktop_chat"]["registry_seam"] == "HeavenBase desktop AI chat"
    assert row_by_symbol["desktop_chat"]["doc_page"] == "docs/user-manual/desktop-api-reference.md"
    assert row_by_symbol["desktop_chat_profiles"]["returns"] == "dict[str, object]"
    assert row_by_symbol["desktop_reset_chat_profile"]["returns"] == "dict[str, object]"
    assert row_by_symbol["desktop_write_chat_profile"]["returns"] == "dict[str, object]"
    assert row_by_symbol["hoi4_keyword_dataset"]["module"] == "games.hoi4.keywords"
    assert reference.startswith("# SDK API Reference\n")
    assert "Generated from `paradev.sdk.get_sdk_api_table()`." in reference
    assert (
        "| `api` | 6 | `SDK_API_TABLE_SCHEMA`, `SdkApiRow`, `SdkApiTable`, "
        "`get_sdk_api_selection`, `get_sdk_api_table`, `render_sdk_api_reference_markdown` |"
    ) in reference
    assert (
        "| `project_api` | 6 | `PROJECT_API_TABLE_SCHEMA`, `ProjectApiRow`, `ProjectApiTable`, "
        "`get_project_api_selection`, `get_project_api_table`, `render_project_api_reference_markdown` |" in reference
    )
    desktop_local_reference_line = (
        "| `desktop.local` | 4 | `desktop_chat`, `desktop_chat_profiles`, " "`desktop_reset_chat_profile`, `desktop_write_chat_profile` |"
    )
    ai_chat_reference_line = "| `ai-chat` | 4 | `desktop_chat`, `desktop_chat_profiles`, " "`desktop_reset_chat_profile`, `desktop_write_chat_profile` |"
    assert desktop_local_reference_line in reference
    assert ai_chat_reference_line in reference
    assert "| `function` | 68 | `build_frontend_api_rest_index_key`, `complete_pdx_lsp_text`," in reference
    assert (
        "| `get_sdk_api_table` | `function` | `sdk` | `api` | `api-table` | `paradev.sdk.get_sdk_api_table` | "
        "`SdkApiTable` |  | `none` | `sdk` | `docs/user-manual/sdk-api-reference.md` |"
    ) in reference
    manual = Path("docs/user-manual/sdk-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_sdk_api_table()["rows"][0]["symbol"] == "ArchitectureSpec"
    table["module_index"]["api"].append("Project")
    assert get_sdk_api_table()["module_index"]["api"] == [
        "SDK_API_TABLE_SCHEMA",
        "SdkApiRow",
        "SdkApiTable",
        "get_sdk_api_selection",
        "get_sdk_api_table",
        "render_sdk_api_reference_markdown",
    ]
    assert is_typeddict(ProjectApiRow)
    assert is_typeddict(ProjectApiTable)
    assert get_project_api_table()["schema"] == PROJECT_API_TABLE_SCHEMA
    assert render_project_api_reference_markdown().startswith("# Project API Reference\n")


def test_ai_frontend_sdk_bindings_resolve_to_public_sdk_facade() -> None:
    import paradev.sdk as sdk
    from paradev.sdk import get_frontend_api_contract, get_sdk_api_table

    contract_rows = {str(row["id"]): row for row in get_frontend_api_contract()["operations"]}
    sdk_rows = {row["symbol"]: row for row in get_sdk_api_table()["rows"]}

    for operation_id in (
        "ai.profiles",
        "ai.profile.write",
        "ai.profile.reset",
        "ai.chat",
    ):
        sdk_symbol = str(contract_rows[operation_id]["sdk"])
        assert sdk_symbol in sdk.__all__
        assert getattr(sdk, sdk_symbol) is not None
        assert sdk_rows[sdk_symbol]["feature"] == "ai-chat"
        assert sdk_rows[sdk_symbol]["import_path"] == f"paradev.sdk.{sdk_symbol}"


def test_project_api_table_lists_project_object_surface() -> None:
    from typing_extensions import is_typeddict

    from paradev.sdk import (
        PROJECT_API_TABLE_SCHEMA,
        ProjectApiRow,
        ProjectApiTable,
        get_project_api_table,
        render_project_api_reference_markdown,
    )

    table = get_project_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_project_api_reference_markdown()

    assert is_typeddict(ProjectApiRow)
    assert is_typeddict(ProjectApiTable)
    assert table["schema"] == PROJECT_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == 81
    assert set(ProjectApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "feature",
        "inputs",
        "returns",
        "raises",
        "cli_commands",
        "frontend_operation_ids",
        "inspection_kinds",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(ProjectApiTable.__annotations__) == {
        "schema",
        "row_count",
        "feature_index",
        "kind_index",
        "cli_command_index",
        "frontend_operation_index",
        "inspection_kind_index",
        "rows",
    }
    assert {feature: len(symbols) for feature, symbols in table["feature_index"].items()} == {
        "project-state": 15,
        "projects": 14,
        "modules": 15,
        "collections": 8,
        "authoring": 9,
        "build": 15,
        "inspections": 2,
        "catalog": 3,
    }
    assert {kind: len(symbols) for kind, symbols in table["kind_index"].items()} == {
        "field": 15,
        "classmethod": 3,
        "method": 63,
    }
    assert len(table["cli_command_index"]) == 50
    assert len(table["frontend_operation_index"]) == 61
    assert len(table["inspection_kind_index"]) == 19
    assert table["cli_command_index"]["paradev new"] == ["Project.create"]
    assert table["cli_command_index"]["paradev build"] == ["Project.build"]
    assert table["cli_command_index"]["paradev module-batch-edit"] == ["Project.write_module_files"]
    assert table["cli_command_index"]["paradev module-batch-request"] == ["Project.module_batch_edit_request"]
    assert table["cli_command_index"]["paradev module-batch-create"] == ["Project.create_modules"]
    assert table["cli_command_index"]["paradev module-duplicate"] == ["Project.duplicate_module"]
    assert table["cli_command_index"]["paradev module-collection-set"] == ["Project.set_module_collection"]
    assert table["cli_command_index"]["paradev module-activity-set"] == ["Project.set_module_active"]
    assert table["cli_command_index"]["paradev module-metadata-clean"] == ["Project.clean_module_metadata"]
    assert table["cli_command_index"]["paradev module-diagram"] == ["Project.module_diagram"]
    assert table["cli_command_index"]["paradev module-diagram-edit"] == ["Project.edit_module_diagram"]
    assert table["frontend_operation_index"]["project.create"] == ["Project.create"]
    assert table["frontend_operation_index"]["project.source_text"] == ["Project.read_source_text"]
    assert table["frontend_operation_index"]["project.source_form"] == ["Project.source_form"]
    assert table["frontend_operation_index"]["localization.workspace"] == ["Project.localization_workspace"]
    assert table["frontend_operation_index"]["localization.plan"] == ["Project.plan_localization_update"]
    assert table["frontend_operation_index"]["project.draft_apply"] == ["Project.apply_source_draft"]
    assert table["frontend_operation_index"]["project.language"] == ["Project.set_preferred_language"]
    assert table["frontend_operation_index"]["build.emit"] == ["Project.build"]
    assert table["frontend_operation_index"]["collection.scaffold"] == ["Project.scaffold_collection"]
    assert table["inspection_kind_index"]["summary"] == [
        "Project.summary",
        "Project.inspect",
    ]
    assert row_by_symbol["Project.root"]["kind"] == "field"
    assert row_by_symbol["Project.root"]["inputs"] == "constructor"
    assert row_by_symbol["Project.root"]["returns"] == "Path"
    assert row_by_symbol["Project.preferred_language"]["returns"] == "str"
    assert row_by_symbol["Project.create"]["kind"] == "classmethod"
    assert row_by_symbol["Project.create"]["raises"] == "ProjectCreateError"
    assert row_by_symbol["Project.create"]["cli_commands"] == ["paradev new"]
    assert row_by_symbol["Project.create"]["frontend_operation_ids"] == ["project.create"]
    assert row_by_symbol["Project.load"]["raises"] == "ProjectManifestError"
    assert row_by_symbol["Project.build"]["registry_seam"] == "project build registry"
    assert row_by_symbol["Project.build"]["frontend_operation_ids"] == [
        "build.plan",
        "build.emit",
    ]
    assert row_by_symbol["Project.catalog_status"]["feature"] == "catalog"
    assert row_by_symbol["Project.catalog_status"]["returns"] == "dict[str, object]"
    assert row_by_symbol["Project.inspect"]["feature"] == "inspections"
    assert row_by_symbol["Project.inspect"]["doc_page"] == "docs/user-manual/project-inspection-reference.md"
    assert len(row_by_symbol["Project.inspect"]["inspection_kinds"]) == 19
    assert "summary" in row_by_symbol["Project.inspect"]["inspection_kinds"]
    assert row_by_symbol["Project.create_collection"]["doc_page"] == "docs/user-manual/modules-and-collections.md"
    assert row_by_symbol["Project.scaffold_collection"]["feature"] == ("collections")
    assert row_by_symbol["Project.scaffold_collection"]["returns"] == ("dict[str, object]")
    assert row_by_symbol["Project.write_module_files"]["feature"] == "modules"
    assert row_by_symbol["Project.write_module_files"]["cli_commands"] == ["paradev module-batch-edit"]
    assert row_by_symbol["Project.write_module_files"]["returns"] == "dict[str, object]"
    assert row_by_symbol["Project.module_batch_edit_request"]["feature"] == "modules"
    assert row_by_symbol["Project.module_batch_edit_request"]["cli_commands"] == ["paradev module-batch-request"]
    assert row_by_symbol["Project.module_batch_edit_request"]["returns"] == "dict[str, object]"
    assert row_by_symbol["Project.create_modules"]["feature"] == "authoring"
    assert row_by_symbol["Project.create_modules"]["cli_commands"] == ["paradev module-batch-create"]
    assert row_by_symbol["Project.create_modules"]["returns"] == "dict[str, object]"
    assert row_by_symbol["Project.duplicate_module"]["feature"] == "modules"
    assert row_by_symbol["Project.duplicate_module"]["cli_commands"] == ["paradev module-duplicate"]
    assert row_by_symbol["Project.duplicate_module"]["frontend_operation_ids"] == ["module.duplicate"]
    assert row_by_symbol["Project.set_module_collection"]["feature"] == "modules"
    assert row_by_symbol["Project.set_module_collection"]["cli_commands"] == ["paradev module-collection-set"]
    assert row_by_symbol["Project.set_module_collection"]["frontend_operation_ids"] == ["module.collection.set"]
    assert row_by_symbol["Project.set_module_active"]["feature"] == "modules"
    assert row_by_symbol["Project.set_module_active"]["cli_commands"] == ["paradev module-activity-set"]
    assert row_by_symbol["Project.set_module_active"]["frontend_operation_ids"] == ["module.activity.set"]
    assert row_by_symbol["Project.clean_module_metadata"]["feature"] == "modules"
    assert row_by_symbol["Project.clean_module_metadata"]["cli_commands"] == ["paradev module-metadata-clean"]
    assert row_by_symbol["Project.clean_module_metadata"]["frontend_operation_ids"] == ["module.metadata.clean"]
    assert row_by_symbol["Project.module_diagram"]["frontend_operation_ids"] == ["module.diagram"]
    assert row_by_symbol["Project.edit_module_diagram"]["frontend_operation_ids"] == ["module.diagram.edit"]
    assert row_by_symbol["Project.read_module_asset"]["feature"] == "modules"
    assert row_by_symbol["Project.read_module_asset"]["registry_seam"] == ("project build registry")
    assert row_by_symbol["Project.read_source_text"]["feature"] == "projects"
    assert row_by_symbol["Project.read_source_text"]["frontend_operation_ids"] == ["project.source_text"]
    assert row_by_symbol["Project.read_source_binary"]["feature"] == "projects"
    assert row_by_symbol["Project.read_source_binary"]["returns"] == ("dict[str, object]")
    assert row_by_symbol["Project.source_form"]["feature"] == "projects"
    assert row_by_symbol["Project.source_form"]["frontend_operation_ids"] == ["project.source_form"]
    assert row_by_symbol["Project.plan_source_form_update"]["feature"] == "projects"
    assert row_by_symbol["Project.plan_source_form_update"]["frontend_operation_ids"] == []
    assert row_by_symbol["Project.plan_source_form_updates"]["feature"] == "projects"
    assert row_by_symbol["Project.plan_source_form_updates"]["frontend_operation_ids"] == []
    assert row_by_symbol["Project.localization_workspace"]["feature"] == "authoring"
    assert row_by_symbol["Project.localization_workspace"]["registry_seam"] == "project build registry"
    assert row_by_symbol["Project.localization_workspace"]["frontend_operation_ids"] == ["localization.workspace"]
    assert row_by_symbol["Project.plan_localization_update"]["feature"] == "authoring"
    assert row_by_symbol["Project.plan_localization_update"]["returns"] == "dict[str, object]"
    assert row_by_symbol["Project.plan_localization_update"]["frontend_operation_ids"] == ["localization.plan"]
    assert row_by_symbol["Project.apply_source_draft"]["feature"] == "projects"
    assert row_by_symbol["Project.apply_source_draft"]["cli_commands"] == ["paradev draft-apply"]
    assert row_by_symbol["Project.apply_source_draft"]["frontend_operation_ids"] == ["project.draft_apply"]
    assert row_by_symbol["Project.scaffold_module"]["frontend_operation_ids"] == ["module.create"]
    assert row_by_symbol["Project.create_module_draft"]["feature"] == "authoring"
    assert row_by_symbol["Project.create_module_draft"]["frontend_operation_ids"] == ["module.draft"]
    assert reference.startswith("# Project API Reference\n")
    assert "Generated from `paradev.sdk.get_project_api_table()`." in reference
    assert "| `project-state` | 15 | `Project.root`, `Project.manifest_path`," in reference
    assert "| `projects` | 14 | `Project.find`, `Project.create`, `Project.load`," in reference
    assert "| `authoring` | 9 | `Project.localization_workspace`, `Project.plan_localization_update`, `Project.templates`," in reference
    assert "| `field` | 15 | `Project.root`, `Project.manifest_path`," in reference
    assert "| `paradev build` | 1 | `Project.build` |" in reference
    assert "| `paradev draft-apply` | 1 | `Project.apply_source_draft` |" in reference
    assert "| `build.emit` | 1 | `Project.build` |" in reference
    assert "| `Project.create` | `classmethod` | `sdk` | `projects` |" in reference
    manual = Path("docs/user-manual/project-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_project_api_table()["rows"][0]["symbol"] == "Project.root"
    table["inspection_kind_index"]["summary"].append("Project.root")
    assert get_project_api_table()["inspection_kind_index"]["summary"] == [
        "Project.summary",
        "Project.inspect",
    ]


def test_templates_api_table_lists_authoring_template_contract() -> None:
    from typing_extensions import is_typeddict

    import paradev.sdk.templates as templates
    from paradev.sdk.templates import (
        COLLECTION_SCAFFOLD_SCHEMA,
        MODULE_SCAFFOLD_SCHEMA,
        TEMPLATES_API_TABLE_SCHEMA,
        TEMPLATES_SCHEMA,
        TemplatesApiRow,
        TemplatesApiTable,
        get_templates_api_table,
        render_templates_api_reference_markdown,
    )

    table = get_templates_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_templates_api_reference_markdown()

    assert is_typeddict(TemplatesApiRow)
    assert is_typeddict(TemplatesApiTable)
    assert table["schema"] == TEMPLATES_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == len(templates.__all__) == 18
    assert [row["symbol"] for row in rows] == list(templates.__all__)
    assert set(TemplatesApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(TemplatesApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "sdk.templates": [
            "TEMPLATES_SCHEMA",
            "MODULE_SCAFFOLD_SCHEMA",
            "COLLECTION_SCAFFOLD_SCHEMA",
            "ProjectTemplateSpecError",
            "TemplateArg",
            "TemplateFile",
            "ModuleTemplate",
            "builtin_module_templates",
            "project_module_templates",
            "template_index",
            "module_scaffold_plan",
            "collection_scaffold_plan",
            "TEMPLATES_API_TABLE_SCHEMA",
            "TemplatesApiRow",
            "TemplatesApiTable",
            "get_templates_api_selection",
            "get_templates_api_table",
            "render_templates_api_reference_markdown",
        ]
    }
    assert table["feature_index"] == {
        "schemas": [
            "TEMPLATES_SCHEMA",
            "MODULE_SCAFFOLD_SCHEMA",
            "COLLECTION_SCAFFOLD_SCHEMA",
        ],
        "errors": ["ProjectTemplateSpecError"],
        "models": ["TemplateArg", "TemplateFile", "ModuleTemplate"],
        "registry": [
            "builtin_module_templates",
            "project_module_templates",
            "template_index",
        ],
        "scaffold": [
            "module_scaffold_plan",
            "collection_scaffold_plan",
        ],
        "templates-api": [
            "TEMPLATES_API_TABLE_SCHEMA",
            "TemplatesApiRow",
            "TemplatesApiTable",
            "get_templates_api_selection",
            "get_templates_api_table",
            "render_templates_api_reference_markdown",
        ],
    }
    assert table["kind_index"] == {
        "schema constant": [
            "TEMPLATES_SCHEMA",
            "MODULE_SCAFFOLD_SCHEMA",
            "COLLECTION_SCAFFOLD_SCHEMA",
            "TEMPLATES_API_TABLE_SCHEMA",
        ],
        "exception": ["ProjectTemplateSpecError"],
        "dataclass": ["TemplateArg", "TemplateFile", "ModuleTemplate"],
        "function": [
            "builtin_module_templates",
            "project_module_templates",
            "template_index",
            "module_scaffold_plan",
            "collection_scaffold_plan",
            "get_templates_api_selection",
            "get_templates_api_table",
            "render_templates_api_reference_markdown",
        ],
        "TypedDict": ["TemplatesApiRow", "TemplatesApiTable"],
    }
    assert row_by_symbol["TEMPLATES_SCHEMA"]["value"] == TEMPLATES_SCHEMA
    assert row_by_symbol["MODULE_SCAFFOLD_SCHEMA"]["value"] == MODULE_SCAFFOLD_SCHEMA
    assert row_by_symbol["COLLECTION_SCAFFOLD_SCHEMA"]["value"] == (COLLECTION_SCAFFOLD_SCHEMA)
    assert row_by_symbol["ProjectTemplateSpecError"]["returns"] == "ProjectTemplateSpecError exception"
    assert row_by_symbol["TemplateArg"]["returns"] == "TemplateArg dataclass"
    assert row_by_symbol["ModuleTemplate"]["registry_seam"] == "authoring template model registry"
    assert row_by_symbol["builtin_module_templates"]["returns"] == "tuple[ModuleTemplate, ...]"
    assert row_by_symbol["module_scaffold_plan"]["returns"] == "dict[str, object]"
    assert row_by_symbol["module_scaffold_plan"]["registry_seam"] == ("resource scaffold planner")
    assert row_by_symbol["collection_scaffold_plan"]["returns"] == ("dict[str, object]")
    assert row_by_symbol["TEMPLATES_API_TABLE_SCHEMA"]["value"] == TEMPLATES_API_TABLE_SCHEMA
    assert row_by_symbol["TemplatesApiRow"]["returns"] == "TypedDict schema"
    assert row_by_symbol["get_templates_api_table"]["returns"] == "TemplatesApiTable"
    assert row_by_symbol["render_templates_api_reference_markdown"]["returns"] == "str"
    assert reference.startswith("# Authoring Templates API Reference\n")
    assert "Generated from `paradev.sdk.templates.get_templates_api_table()`." in reference
    assert (
        "| `sdk.templates` | 18 | `TEMPLATES_SCHEMA`, `MODULE_SCAFFOLD_SCHEMA`, `COLLECTION_SCAFFOLD_SCHEMA`, `ProjectTemplateSpecError`, "
        "`TemplateArg`, `TemplateFile`, `ModuleTemplate`,"
    ) in reference
    assert "| `registry` | 3 | `builtin_module_templates`, `project_module_templates`, `template_index` |" in reference
    assert (
        "| `function` | 8 | `builtin_module_templates`, `project_module_templates`, `template_index`, "
        "`module_scaffold_plan`, `collection_scaffold_plan`, `get_templates_api_selection`, `get_templates_api_table`, `render_templates_api_reference_markdown` |"
    ) in reference
    assert (
        "| `module_scaffold_plan` | `function` | `sdk` | `sdk.templates` | `scaffold` | "
        "`paradev.sdk.templates.module_scaffold_plan` | `dict[str, object]` |  | `resource scaffold planner` |"
    ) in reference
    manual = Path("docs/user-manual/templates-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_templates_api_table()["rows"][0]["symbol"] == "TEMPLATES_SCHEMA"
    table["module_index"]["sdk.templates"].append("changed")
    assert get_templates_api_table()["module_index"]["sdk.templates"] == [
        "TEMPLATES_SCHEMA",
        "MODULE_SCAFFOLD_SCHEMA",
        "COLLECTION_SCAFFOLD_SCHEMA",
        "ProjectTemplateSpecError",
        "TemplateArg",
        "TemplateFile",
        "ModuleTemplate",
        "builtin_module_templates",
        "project_module_templates",
        "template_index",
        "module_scaffold_plan",
        "collection_scaffold_plan",
        "TEMPLATES_API_TABLE_SCHEMA",
        "TemplatesApiRow",
        "TemplatesApiTable",
        "get_templates_api_selection",
        "get_templates_api_table",
        "render_templates_api_reference_markdown",
    ]


def test_copy_roots_api_table_lists_copy_root_contract() -> None:
    from typing_extensions import is_typeddict

    import paradev.sdk.copy_roots as copy_roots
    from paradev.sdk.copy_roots import (
        ARTIFACT_TARGET_ROOTS,
        COPY_ROOTS_API_TABLE_SCHEMA,
        CopyRootsApiRow,
        CopyRootsApiTable,
        get_copy_roots_api_table,
        render_copy_roots_api_reference_markdown,
    )

    table = get_copy_roots_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_copy_roots_api_reference_markdown()

    assert is_typeddict(CopyRootsApiRow)
    assert is_typeddict(CopyRootsApiTable)
    assert table["schema"] == COPY_ROOTS_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == len(copy_roots.__all__) == 12
    assert [row["symbol"] for row in rows] == list(copy_roots.__all__)
    assert set(CopyRootsApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(CopyRootsApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "sdk.copy_roots": [
            "ARTIFACT_TARGET_ROOTS",
            "ProjectCopyRootSpecError",
            "CopyRootSpec",
            "project_copy_roots",
            "copy_root_artifacts",
            "merge_copy_root_artifacts",
            "COPY_ROOTS_API_TABLE_SCHEMA",
            "CopyRootsApiRow",
            "CopyRootsApiTable",
            "get_copy_roots_api_selection",
            "get_copy_roots_api_table",
            "render_copy_roots_api_reference_markdown",
        ]
    }
    assert table["feature_index"] == {
        "target-roots": ["ARTIFACT_TARGET_ROOTS"],
        "errors": ["ProjectCopyRootSpecError"],
        "models": ["CopyRootSpec"],
        "manifest": ["project_copy_roots"],
        "artifacts": ["copy_root_artifacts", "merge_copy_root_artifacts"],
        "copy-roots-api": [
            "COPY_ROOTS_API_TABLE_SCHEMA",
            "CopyRootsApiRow",
            "CopyRootsApiTable",
            "get_copy_roots_api_selection",
            "get_copy_roots_api_table",
            "render_copy_roots_api_reference_markdown",
        ],
    }
    assert table["kind_index"] == {
        "set constant": ["ARTIFACT_TARGET_ROOTS"],
        "exception": ["ProjectCopyRootSpecError"],
        "dataclass": ["CopyRootSpec"],
        "function": [
            "project_copy_roots",
            "copy_root_artifacts",
            "merge_copy_root_artifacts",
            "get_copy_roots_api_selection",
            "get_copy_roots_api_table",
            "render_copy_roots_api_reference_markdown",
        ],
        "schema constant": ["COPY_ROOTS_API_TABLE_SCHEMA"],
        "TypedDict": ["CopyRootsApiRow", "CopyRootsApiTable"],
    }
    assert row_by_symbol["ARTIFACT_TARGET_ROOTS"]["returns"] == f"set[{len(ARTIFACT_TARGET_ROOTS)}]"
    assert row_by_symbol["ARTIFACT_TARGET_ROOTS"]["value"] == "build, output"
    assert row_by_symbol["ProjectCopyRootSpecError"]["returns"] == "ProjectCopyRootSpecError exception"
    assert row_by_symbol["CopyRootSpec"]["returns"] == "CopyRootSpec dataclass"
    assert row_by_symbol["project_copy_roots"]["returns"] == "tuple[CopyRootSpec, ...]"
    assert row_by_symbol["copy_root_artifacts"]["returns"] == "tuple[tuple[Artifact, ...], tuple[Diagnostic, ...]]"
    assert row_by_symbol["merge_copy_root_artifacts"]["registry_seam"] == "copy-root artifact pipeline"
    assert row_by_symbol["COPY_ROOTS_API_TABLE_SCHEMA"]["value"] == COPY_ROOTS_API_TABLE_SCHEMA
    assert row_by_symbol["CopyRootsApiRow"]["returns"] == "TypedDict schema"
    assert row_by_symbol["get_copy_roots_api_table"]["returns"] == "CopyRootsApiTable"
    assert row_by_symbol["render_copy_roots_api_reference_markdown"]["returns"] == "str"
    assert reference.startswith("# Copy Roots API Reference\n")
    assert "Generated from `paradev.sdk.copy_roots.get_copy_roots_api_table()`." in reference
    assert ("| `sdk.copy_roots` | 12 | `ARTIFACT_TARGET_ROOTS`, `ProjectCopyRootSpecError`, " "`CopyRootSpec`, `project_copy_roots`,") in reference
    assert "| `artifacts` | 2 | `copy_root_artifacts`, `merge_copy_root_artifacts` |" in reference
    assert (
        "| `function` | 6 | `project_copy_roots`, `copy_root_artifacts`, `merge_copy_root_artifacts`, "
        "`get_copy_roots_api_selection`, `get_copy_roots_api_table`, `render_copy_roots_api_reference_markdown` |"
    ) in reference
    assert (
        "| `copy_root_artifacts` | `function` | `sdk` | `sdk.copy_roots` | `artifacts` | "
        "`paradev.sdk.copy_roots.copy_root_artifacts` | `tuple[tuple[Artifact, ...], tuple[Diagnostic, ...]]` |  | "
        "`copy-root artifact pipeline` |"
    ) in reference
    manual = Path("docs/user-manual/copy-roots-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_copy_roots_api_table()["rows"][0]["symbol"] == "ARTIFACT_TARGET_ROOTS"
    table["module_index"]["sdk.copy_roots"].append("changed")
    assert get_copy_roots_api_table()["module_index"]["sdk.copy_roots"] == [
        "ARTIFACT_TARGET_ROOTS",
        "ProjectCopyRootSpecError",
        "CopyRootSpec",
        "project_copy_roots",
        "copy_root_artifacts",
        "merge_copy_root_artifacts",
        "COPY_ROOTS_API_TABLE_SCHEMA",
        "CopyRootsApiRow",
        "CopyRootsApiTable",
        "get_copy_roots_api_selection",
        "get_copy_roots_api_table",
        "render_copy_roots_api_reference_markdown",
    ]


def test_build_api_table_lists_public_build_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev.build as build
    from paradev.build import (
        BUILD_API_TABLE_SCHEMA,
        BuildApiRow,
        BuildApiTable,
        get_build_api_table,
        render_build_api_reference_markdown,
    )

    table = get_build_api_table()
    rows = table["rows"]
    symbols = [row["symbol"] for row in rows]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_build_api_reference_markdown()

    assert is_typeddict(BuildApiRow)
    assert is_typeddict(BuildApiTable)
    assert table["schema"] == BUILD_API_TABLE_SCHEMA
    assert table["row_count"] == len(build.__all__) == len(rows) == 133
    assert symbols == list(build.__all__)
    assert len(symbols) == len(set(symbols))
    assert set(BuildApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(BuildApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert {module: len(symbols) for module, symbols in table["module_index"].items()} == {
        "records": 7,
        "views": 20,
        "api": 6,
        "manifest": 15,
        "plan": 4,
        "registry": 1,
        "discovery": 6,
        "authoring": 4,
        "loaders": 18,
        "families": 6,
        "explain": 2,
        "graph": 2,
        "artifacts": 8,
        "extensions": 9,
        "build": 5,
        "presentation": 3,
        "diagrams": 12,
        "source_slots": 2,
        "slots": 3,
    }
    assert {feature: len(symbols) for feature, symbols in table["feature_index"].items()} == {
        "records": 7,
        "views": 20,
        "api-table": 6,
        "manifests": 15,
        "planning": 4,
        "families": 20,
        "source-discovery": 11,
        "source-loading": 18,
        "graph": 4,
        "artifacts": 8,
        "build": 8,
        "diagrams": 12,
    }
    assert {kind: len(symbols) for kind, symbols in table["kind_index"].items()} == {
        "dataclass": 43,
        "schema constant": 8,
        "function": 59,
        "TypedDict": 2,
        "tuple constant": 2,
        "class": 9,
        "str": 5,
        "type alias": 4,
        "frozenset": 1,
    }
    assert table["module_index"]["api"] == [
        "BUILD_API_TABLE_SCHEMA",
        "BuildApiRow",
        "BuildApiTable",
        "get_build_api_selection",
        "get_build_api_table",
        "render_build_api_reference_markdown",
    ]
    assert row_by_symbol["BUILD_API_TABLE_SCHEMA"]["value"] == BUILD_API_TABLE_SCHEMA
    assert row_by_symbol["BuildApiRow"]["returns"] == "TypedDict schema"
    assert row_by_symbol["BuildRegistry"]["registry_seam"] == "BuildRegistry family registry"
    assert row_by_symbol["ModuleDiagramSelectionDefault"]["registry_seam"] == "BuildRegistry diagram provider registry"
    assert row_by_symbol["ModuleDiagramNodeAuthoring"]["registry_seam"] == "BuildRegistry diagram provider registry"
    assert row_by_symbol["ModuleDiagramNodeField"]["feature"] == "diagrams"
    assert row_by_symbol["ModuleDiagramNodePlanner"]["feature"] == "diagrams"
    assert row_by_symbol["BuildRegistry"]["doc_page"] == "docs/user-manual/modules-and-collections.md"
    assert row_by_symbol["SimpleSourceFamily"]["feature"] == "families"
    assert row_by_symbol["FamilyCompileResult"]["feature"] == "planning"
    assert row_by_symbol["ModuleIdentityRewriter"]["registry_seam"] == ("BuildRegistry family registry")
    assert row_by_symbol["DEFAULT_IDENTITY_REWRITER"]["returns"] == ("TokenIdentityRewriter")
    assert row_by_symbol["Module"]["feature"] == "records"
    assert row_by_symbol["BuildResult"]["registry_seam"] == "Project.build pipeline"
    assert row_by_symbol["Slot"]["feature"] == "source-discovery"
    assert row_by_symbol["DEFAULT_MODULE_SLOTS"]["returns"] == "tuple[5]"
    assert row_by_symbol["summary_view"]["returns"] == "dict[str, object]"
    assert row_by_symbol["write_artifacts"]["registry_seam"] == "BuildRegistry artifact writer registry"
    assert reference.startswith("# Build API Reference\n")
    assert "Generated from `paradev.build.get_build_api_table()`." in reference
    assert (
        "| `api` | 6 | `BUILD_API_TABLE_SCHEMA`, `BuildApiRow`, `BuildApiTable`, `get_build_api_selection`, `get_build_api_table`, `render_build_api_reference_markdown` |"
        in reference
    )
    assert "| `families` | 20 | `DEFAULT_IDENTITY_REWRITER`, `PROJECT_DIAGRAM_PROVIDER_KIND`," in reference
    assert "| `TypedDict` | 2 | `BuildApiRow`, `BuildApiTable` |" in reference
    assert (
        "| `BuildRegistry` | `dataclass` | `build` | `registry` | `families` | `paradev.build.BuildRegistry` | "
        "`class` |  | `BuildRegistry family registry` |"
    ) in reference
    manual = Path("docs/user-manual/build-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    first_symbol = rows[0]["symbol"]
    rows[0]["symbol"] = "changed"
    assert get_build_api_table()["rows"][0]["symbol"] == first_symbol
    table["module_index"]["api"].append("Artifact")
    assert get_build_api_table()["module_index"]["api"] == [
        "BUILD_API_TABLE_SCHEMA",
        "BuildApiRow",
        "BuildApiTable",
        "get_build_api_selection",
        "get_build_api_table",
        "render_build_api_reference_markdown",
    ]


def test_pdx_api_table_lists_parse_format_surfaces() -> None:
    from typing_extensions import is_typeddict

    from paradev.sdk import (
        PDX_API_TABLE_ROWS,
        PDX_API_TABLE_SCHEMA,
        PDX_FORMAT_SCHEMA,
        PDX_PARSE_SCHEMA,
        PdxApiRow,
        PdxApiTable,
        get_pdx_api_table,
        render_pdx_api_reference_markdown,
    )

    table = get_pdx_api_table()
    rows = table["rows"]
    symbols = [row["symbol"] for row in rows]
    reference = render_pdx_api_reference_markdown()

    assert is_typeddict(PdxApiRow)
    assert is_typeddict(PdxApiTable)
    assert table["schema"] == PDX_API_TABLE_SCHEMA
    assert table["row_count"] == len(PDX_API_TABLE_ROWS) == len(rows)
    assert tuple(rows) == PDX_API_TABLE_ROWS
    assert set(PdxApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "feature",
        "inputs",
        "returns",
        "raises",
        "registry_seam",
        "surface",
        "payload_schema",
        "doc_page",
        "test_anchor",
    }
    assert set(PdxApiTable.__annotations__) == {
        "schema",
        "row_count",
        "surface_index",
        "feature_index",
        "rows",
    }
    assert symbols[:3] == [
        "PDX_PARSE_SCHEMA",
        "PDX_FORMAT_SCHEMA",
        "PDX_API_TABLE_SCHEMA",
    ]
    assert "parse_pdx_file" in table["surface_index"]["sdk"]
    assert "format_pdx_text" in table["surface_index"]["sdk"]
    assert "paradev pdx-api --markdown" in table["surface_index"]["cli"]
    assert "GET /pdx/parse" in table["surface_index"]["rest"]
    assert "GET /pdx-api" in table["surface_index"]["rest"]
    assert table["surface_index"]["mcp"] == ["pdx_parse", "pdx_format", "pdx_api"]
    assert table["feature_index"]["parse"] == [
        "PDX_PARSE_SCHEMA",
        "parse_pdx_file",
        "paradev parse",
        "GET /pdx/parse",
        "pdx_parse",
    ]
    assert "format_pdx_file" in table["feature_index"]["format"]
    assert rows[0]["payload_schema"] == PDX_PARSE_SCHEMA
    assert rows[1]["payload_schema"] == PDX_FORMAT_SCHEMA
    assert reference.startswith("# PDX API Reference\n")
    assert "Generated from `paradev.sdk.get_pdx_api_table()`." in reference
    assert "| `api-table` | 11 | `PDX_API_TABLE_SCHEMA`, `PDX_API_TABLE_ROWS`, `PdxApiRow`," in reference
    assert "| `cli` | 4 | `paradev pdx-api`, `paradev pdx-api --markdown`, `paradev parse`, `paradev format` |" in reference
    assert (
        '| `format_pdx_file` | `function` | `sdk` | `format` | `sdk` | `path, indent="\\t", comments=True, write=False` | '
        "`PDX format payload` | `ValueError on non-string indent` |"
    ) in reference
    manual = Path("docs/user-manual/pdx-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_pdx_api_table()["rows"][0]["symbol"] == "PDX_PARSE_SCHEMA"


def test_pdx_core_api_table_lists_public_pdx_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev.pdx as pdx
    from paradev.pdx import (
        PDX_CORE_API_TABLE_SCHEMA,
        PdxCoreApiRow,
        PdxCoreApiTable,
        get_pdx_core_api_table,
        render_pdx_core_api_reference_markdown,
    )

    table = get_pdx_core_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_pdx_core_api_reference_markdown()

    assert is_typeddict(PdxCoreApiRow)
    assert is_typeddict(PdxCoreApiTable)
    assert table["schema"] == PDX_CORE_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == len(pdx.__all__) == 23
    assert [row["symbol"] for row in rows] == list(pdx.__all__)
    assert set(PdxCoreApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(PdxCoreApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "ast": [
            "PDXBlock",
            "PDXEntry",
            "PDXScalar",
            "SCALAR_BOOL",
            "SCALAR_COLOR",
            "SCALAR_ID",
            "SCALAR_NUM",
            "SCALAR_STR",
            "SCALAR_VAR",
        ],
        "api": [
            "PDX_CORE_API_TABLE_SCHEMA",
            "PdxCoreApiRow",
            "PdxCoreApiTable",
            "get_pdx_core_api_selection",
            "get_pdx_core_api_table",
            "render_pdx_core_api_reference_markdown",
        ],
        "diagnostics": ["PDXDiagnostic", "PDXParseError"],
        "parser": ["PDXParser", "parse_pdx"],
        "token": ["PDXTokenizer", "Token", "TokenType", "reconstruct"],
    }
    assert table["feature_index"]["pdx-core-api"] == table["module_index"]["api"]
    assert table["feature_index"]["scalars"] == [
        "SCALAR_BOOL",
        "SCALAR_COLOR",
        "SCALAR_ID",
        "SCALAR_NUM",
        "SCALAR_STR",
        "SCALAR_VAR",
    ]
    assert table["kind_index"]["dataclass"] == [
        "PDXBlock",
        "PDXDiagnostic",
        "PDXEntry",
        "PDXScalar",
        "Token",
    ]
    assert table["kind_index"]["function"] == [
        "get_pdx_core_api_selection",
        "get_pdx_core_api_table",
        "parse_pdx",
        "reconstruct",
        "render_pdx_core_api_reference_markdown",
    ]
    assert table["kind_index"]["scalar constant"] == table["feature_index"]["scalars"]
    assert row_by_symbol["PDX_CORE_API_TABLE_SCHEMA"]["value"] == PDX_CORE_API_TABLE_SCHEMA
    assert row_by_symbol["PDXBlock"]["registry_seam"] == "PDX AST contract"
    assert row_by_symbol["PDXParseError"]["kind"] == "exception"
    assert row_by_symbol["TokenType"]["kind"] == "enum"
    assert row_by_symbol["parse_pdx"]["returns"] == "PDXBlock"
    assert row_by_symbol["reconstruct"]["returns"] == "str"
    assert row_by_symbol["get_pdx_core_api_table"]["returns"] == "PdxCoreApiTable"
    assert reference.startswith("# PDX Core API Reference\n")
    assert "Generated from `paradev.pdx.get_pdx_core_api_table()`." in reference
    assert (
        "| `api` | 6 | `PDX_CORE_API_TABLE_SCHEMA`, `PdxCoreApiRow`, `PdxCoreApiTable`, "
        "`get_pdx_core_api_selection`, `get_pdx_core_api_table`, `render_pdx_core_api_reference_markdown` |"
    ) in reference
    assert "| `scalars` | 6 | `SCALAR_BOOL`, `SCALAR_COLOR`, `SCALAR_ID`, `SCALAR_NUM`, `SCALAR_STR`, `SCALAR_VAR` |" in reference
    assert ("| `parse_pdx` | `function` | `pdx` | `parser` | `parser` | `paradev.pdx.parse_pdx` | " "`PDXBlock` |  | `PDX parser contract` |") in reference
    manual = Path("docs/user-manual/pdx-core-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_pdx_core_api_table()["rows"][0]["symbol"] == "PDXBlock"
    table["module_index"]["api"].append("changed")
    assert get_pdx_core_api_table()["module_index"]["api"] == [
        "PDX_CORE_API_TABLE_SCHEMA",
        "PdxCoreApiRow",
        "PdxCoreApiTable",
        "get_pdx_core_api_selection",
        "get_pdx_core_api_table",
        "render_pdx_core_api_reference_markdown",
    ]


def test_lsp_api_table_lists_editor_surfaces() -> None:
    from typing_extensions import is_typeddict

    from paradev.sdk import (
        LSP_API_TABLE_ROWS,
        LSP_API_TABLE_SCHEMA,
        LSP_COMPLETION_SCHEMA,
        LSP_DIAGNOSTICS_SCHEMA,
        LspApiRow,
        LspApiTable,
        get_lsp_api_table,
        render_lsp_api_reference_markdown,
    )

    table = get_lsp_api_table()
    rows = table["rows"]
    symbols = [row["symbol"] for row in rows]
    reference = render_lsp_api_reference_markdown()

    assert is_typeddict(LspApiRow)
    assert is_typeddict(LspApiTable)
    assert table["schema"] == LSP_API_TABLE_SCHEMA
    assert table["row_count"] == len(LSP_API_TABLE_ROWS) == len(rows)
    assert tuple(rows) == LSP_API_TABLE_ROWS
    assert set(LspApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "feature",
        "inputs",
        "returns",
        "raises",
        "registry_seam",
        "surface",
        "payload_schema",
        "doc_page",
        "test_anchor",
    }
    assert set(LspApiTable.__annotations__) == {
        "schema",
        "row_count",
        "surface_index",
        "feature_index",
        "rows",
    }
    assert symbols[:3] == [
        "LSP_DIAGNOSTICS_SCHEMA",
        "LSP_SYMBOLS_SCHEMA",
        "LSP_HOVER_SCHEMA",
    ]
    assert "complete_pdx_lsp_text" in table["surface_index"]["sdk"]
    assert "paradev lsp-api --markdown" in table["surface_index"]["cli"]
    assert "POST /lsp/completion" in table["surface_index"]["rest"]
    assert "GET /lsp-api" in table["surface_index"]["rest"]
    assert table["surface_index"]["mcp"] == ["lsp_api"]
    assert table["surface_index"]["lsp"] == [
        "textDocument/publishDiagnostics",
        "textDocument/documentSymbol",
        "textDocument/hover",
        "textDocument/formatting",
        "textDocument/completion",
        "textDocument/semanticTokens/full",
    ]
    assert table["feature_index"]["diagnostics"] == [
        "LSP_DIAGNOSTICS_SCHEMA",
        "diagnose_pdx_lsp_text",
        "paradev lsp diagnostics",
        "POST /lsp/diagnostics",
        "textDocument/publishDiagnostics",
    ]
    assert "complete_pdx_lsp_text" in table["feature_index"]["completion"]
    assert rows[0]["payload_schema"] == LSP_DIAGNOSTICS_SCHEMA
    assert rows[4]["payload_schema"] == LSP_COMPLETION_SCHEMA
    assert reference.startswith("# LSP API Reference\n")
    assert "Generated from `paradev.sdk.get_lsp_api_table()`." in reference
    assert "| `api-table` | 11 | `LSP_API_TABLE_SCHEMA`, `LSP_API_TABLE_ROWS`, `LspApiRow`," in reference
    assert "| `rest` | 7 | `POST /lsp/diagnostics`, `POST /lsp/symbols`, `POST /lsp/hover`," in reference
    assert "| `mcp` | 1 | `lsp_api` |" in reference
    assert (
        '| `format_pdx_lsp_text` | `function` | `sdk` | `formatting` | `sdk` | `text, uri=None, path=None, indent="\\t", comments=True` | '
        "`LSP formatting payload` | `ValueError on unsupported text, uri, path, or indent` |"
    ) in reference
    manual = Path("docs/user-manual/lsp-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_lsp_api_table()["rows"][0]["symbol"] == "LSP_DIAGNOSTICS_SCHEMA"


def test_lsp_server_api_table_lists_public_lsp_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev.lsp as lsp
    from paradev.lsp import (
        LSP_SERVER_API_TABLE_SCHEMA,
        LspServerApiRow,
        LspServerApiTable,
        get_lsp_server_api_table,
        render_lsp_server_api_reference_markdown,
    )

    table = get_lsp_server_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_lsp_server_api_reference_markdown()

    assert is_typeddict(LspServerApiRow)
    assert is_typeddict(LspServerApiTable)
    assert table["schema"] == LSP_SERVER_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == 11
    assert [row["symbol"] for row in rows] == list(lsp.__all__)
    assert set(LspServerApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(LspServerApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "server": [
            "PdxDocument",
            "PdxLanguageServer",
            "read_lsp_message",
            "serve_pdx_lsp_stdio",
            "write_lsp_message",
        ],
        "api": [
            "LSP_SERVER_API_TABLE_SCHEMA",
            "LspServerApiRow",
            "LspServerApiTable",
            "get_lsp_server_api_selection",
            "get_lsp_server_api_table",
            "render_lsp_server_api_reference_markdown",
        ],
    }
    assert table["feature_index"] == {
        "documents": ["PdxDocument"],
        "server": ["PdxLanguageServer"],
        "framing": ["read_lsp_message", "write_lsp_message"],
        "stdio": ["serve_pdx_lsp_stdio"],
        "lsp-server-api": [
            "LSP_SERVER_API_TABLE_SCHEMA",
            "LspServerApiRow",
            "LspServerApiTable",
            "get_lsp_server_api_selection",
            "get_lsp_server_api_table",
            "render_lsp_server_api_reference_markdown",
        ],
    }
    assert table["kind_index"] == {
        "dataclass": ["PdxDocument"],
        "class": ["PdxLanguageServer"],
        "function": [
            "read_lsp_message",
            "serve_pdx_lsp_stdio",
            "write_lsp_message",
            "get_lsp_server_api_selection",
            "get_lsp_server_api_table",
            "render_lsp_server_api_reference_markdown",
        ],
        "schema constant": ["LSP_SERVER_API_TABLE_SCHEMA"],
        "TypedDict": ["LspServerApiRow", "LspServerApiTable"],
    }
    assert row_by_symbol["PdxDocument"]["registry_seam"] == "LSP document cache"
    assert row_by_symbol["PdxLanguageServer"]["registry_seam"] == "LSP JSON-RPC dispatcher"
    assert row_by_symbol["read_lsp_message"]["returns"] == "dict[str, object] | None"
    assert row_by_symbol["serve_pdx_lsp_stdio"]["registry_seam"] == "LSP stdio server"
    assert row_by_symbol["LSP_SERVER_API_TABLE_SCHEMA"]["value"] == LSP_SERVER_API_TABLE_SCHEMA
    assert row_by_symbol["get_lsp_server_api_table"]["returns"] == "LspServerApiTable"
    assert reference.startswith("# LSP Server API Reference\n")
    assert "Generated from `paradev.lsp.get_lsp_server_api_table()`." in reference
    assert "| `server` | 5 | `PdxDocument`, `PdxLanguageServer`, `read_lsp_message`, `serve_pdx_lsp_stdio`, `write_lsp_message` |" in reference
    assert (
        "| `lsp-server-api` | 6 | `LSP_SERVER_API_TABLE_SCHEMA`, `LspServerApiRow`, `LspServerApiTable`, "
        "`get_lsp_server_api_selection`, `get_lsp_server_api_table`, `render_lsp_server_api_reference_markdown` |"
    ) in reference
    assert (
        "| `function` | 6 | `read_lsp_message`, `serve_pdx_lsp_stdio`, `write_lsp_message`, "
        "`get_lsp_server_api_selection`, `get_lsp_server_api_table`, `render_lsp_server_api_reference_markdown` |"
    ) in reference
    assert (
        "| `PdxLanguageServer` | `class` | `lsp` | `server` | `server` | `paradev.lsp.PdxLanguageServer` | " "`class` |  | `LSP JSON-RPC dispatcher` |"
    ) in reference
    manual = Path("docs/user-manual/lsp-server-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_lsp_server_api_table()["rows"][0]["symbol"] == "PdxDocument"
    table["module_index"]["api"].append("changed")
    assert get_lsp_server_api_table()["module_index"]["api"] == [
        "LSP_SERVER_API_TABLE_SCHEMA",
        "LspServerApiRow",
        "LspServerApiTable",
        "get_lsp_server_api_selection",
        "get_lsp_server_api_table",
        "render_lsp_server_api_reference_markdown",
    ]


def test_catalog_api_table_lists_catalog_surfaces() -> None:
    from typing_extensions import is_typeddict

    from paradev.hb import (
        CATALOG_API_TABLE_ROWS,
        CATALOG_API_TABLE_SCHEMA,
        CATALOG_SCHEMA,
        QUERY_SCHEMA,
        STATUS_SCHEMA,
        CatalogApiRow,
        CatalogApiTable,
        get_catalog_api_table,
        render_catalog_api_reference_markdown,
    )

    table = get_catalog_api_table()
    rows = table["rows"]
    symbols = [row["symbol"] for row in rows]
    reference = render_catalog_api_reference_markdown()

    assert is_typeddict(CatalogApiRow)
    assert is_typeddict(CatalogApiTable)
    assert table["schema"] == CATALOG_API_TABLE_SCHEMA
    assert table["row_count"] == len(CATALOG_API_TABLE_ROWS) == len(rows)
    assert tuple(rows) == CATALOG_API_TABLE_ROWS
    assert set(CatalogApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "feature",
        "inputs",
        "returns",
        "raises",
        "registry_seam",
        "surface",
        "payload_schema",
        "doc_page",
        "test_anchor",
    }
    assert set(CatalogApiTable.__annotations__) == {
        "schema",
        "row_count",
        "surface_index",
        "feature_index",
        "rows",
    }
    assert symbols[:3] == ["CATALOG_SCHEMA", "SMOKE_SCHEMA", "WRITE_SCHEMA"]
    assert "catalog_preview" in table["surface_index"]["sdk"]
    assert "catalog_completion_items" in table["surface_index"]["sdk"]
    assert "paradev catalog-api --markdown" in table["surface_index"]["cli"]
    assert "paradev hb catalog-query" in table["surface_index"]["cli"]
    assert "GET /catalog-api" in table["surface_index"]["rest"]
    assert "GET /projects/inspect?kind=catalog-preview" in table["surface_index"]["rest"]
    assert table["surface_index"]["mcp"] == [
        "project_inspect kind=catalog-preview",
        "project_inspect kind=catalog-query",
        "catalog_api",
    ]
    assert table["feature_index"]["api-table"][-2:] == [
        "GET /catalog-api",
        "catalog_api",
    ]
    assert table["feature_index"]["preview"] == [
        "CATALOG_SCHEMA",
        "catalog_preview",
        "paradev hb catalog-preview",
        "GET /projects/inspect?kind=catalog-preview",
        "project_inspect kind=catalog-preview",
    ]
    assert "catalog_query" in table["feature_index"]["query"]
    assert table["feature_index"]["status"] == [
        "STATUS_SCHEMA",
        "catalog_status",
        "GET /projects/catalog",
    ]
    assert "GET /projects/catalog" in table["surface_index"]["rest"]
    assert rows[0]["payload_schema"] == CATALOG_SCHEMA
    assert rows[4]["payload_schema"] == QUERY_SCHEMA
    assert rows[5]["payload_schema"] == STATUS_SCHEMA
    assert reference.startswith("# Catalog API Reference\n")
    assert "Generated from `paradev.hb.get_catalog_api_table()`." in reference
    assert "| `api-table` | 11 | `CATALOG_API_TABLE_SCHEMA`, `CATALOG_API_TABLE_ROWS`, `CatalogApiRow`," in reference
    assert ("| `cli` | 7 | `paradev catalog-api`, `paradev catalog-api --markdown`, `paradev hb catalog-preview`,") in reference
    assert ("| `rest` | 6 | `GET /projects/inspect?kind=catalog-preview`, `GET /projects/inspect?kind=catalog-query`,") in reference
    assert "| `mcp` | 3 | `project_inspect kind=catalog-preview`, `project_inspect kind=catalog-query`, `catalog_api` |" in reference
    assert (
        "| `catalog_query` | `function` | `sdk` | `query` | `sdk` | "
        "`project, database=None, entity=None, target_id=None, name=None, tag=None, limit=None, offset=0, include_data=True` | "
        "`catalog query payload` | `FileNotFoundError on missing database; RuntimeError on stale database; "
        "ValueError on invalid paging arguments` |"
    ) in reference
    manual = Path("docs/user-manual/catalog-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_catalog_api_table()["rows"][0]["symbol"] == "CATALOG_SCHEMA"


def test_project_inspection_reference_lists_contract_indexes() -> None:
    from typing_extensions import is_typeddict

    from paradev.sdk import (
        PROJECT_INSPECTION_INDEX_CATALOG,
        PROJECT_INSPECTIONS_SCHEMA,
        ProjectInspectionContract,
        ProjectInspectionIndex,
        ProjectInspectionIndexCatalogRow,
        ProjectInspectionProjectContract,
        ProjectInspectionRow,
        get_project_inspection_contract,
        get_project_inspection_filter_kinds,
        get_project_inspection_index_catalog,
        get_project_inspection_kinds,
        get_project_inspection_row,
        get_project_inspection_selection,
        render_project_inspection_reference_markdown,
    )

    contract = get_project_inspection_contract()
    project_contract = get_project_inspection_contract(project_id="demo")
    index_catalog = get_project_inspection_index_catalog()
    rows = {row["kind"]: row for row in contract["inspections"]}
    reference = render_project_inspection_reference_markdown()

    assert is_typeddict(ProjectInspectionContract)
    assert is_typeddict(ProjectInspectionIndex)
    assert is_typeddict(ProjectInspectionIndexCatalogRow)
    assert is_typeddict(ProjectInspectionProjectContract)
    assert is_typeddict(ProjectInspectionRow)
    assert contract["schema"] == PROJECT_INSPECTIONS_SCHEMA
    assert project_contract["project_id"] == "demo"
    assert tuple(index_catalog) == PROJECT_INSPECTION_INDEX_CATALOG
    assert set(ProjectInspectionRow.__annotations__) == {
        "kind",
        "method",
        "cli_command",
        "filters",
    }
    assert set(ProjectInspectionIndex.__annotations__) == {"kind", "filter"}
    assert set(ProjectInspectionIndexCatalogRow.__annotations__) == {
        "id",
        "contract_path",
        "python_helper",
        "usage",
    }
    assert set(ProjectInspectionContract.__annotations__) == {
        "schema",
        "inspections",
        "index",
    }
    assert "project_id" in ProjectInspectionProjectContract.__annotations__
    assert get_project_inspection_kinds() == [row["kind"] for row in contract["inspections"]]
    assert get_project_inspection_kinds()[0] == "inspections"
    assert rows["modules"]["filters"] == [
        "profile",
        "family",
        "module_id",
        "collection_id",
        "source_slot",
    ]
    assert rows["catalog-query"]["cli_command"] == "hb catalog-query"
    assert get_project_inspection_row("source_slots") == rows["source-slots"]
    assert get_project_inspection_filter_kinds("module_id") == contract["index"]["filter"]["module_id"]
    assert get_project_inspection_selection() == contract
    assert get_project_inspection_selection(kind="source_slots") == rows["source-slots"]
    assert get_project_inspection_selection(index_name="kind", key="source-slots") == rows["source-slots"]
    assert get_project_inspection_selection(index_name="filter", key="module_id") == contract["index"]["filter"]["module_id"]
    assert "sources" in get_project_inspection_filter_kinds("owner_kind")
    assert "diagnostics" in get_project_inspection_filter_kinds("strict_metadata")
    assert [row["id"] for row in index_catalog] == ["kind", "filter"]
    assert index_catalog[0]["python_helper"] == "get_project_inspection_selection(kind=kind)"
    assert reference.startswith("# Project Inspection Reference\n")
    assert "Generated from `paradev.sdk.get_project_inspection_contract()`." in reference
    assert "## Filter Index / Filter 索引" in reference
    assert "| `modules` | `Project.modules` | `modules` | `profile`, `family`, `module_id`, `collection_id`, `source_slot` |" in reference
    assert "| `owner_kind` | 1 | `sources` |" in reference
    manual = Path("docs/user-manual/project-inspection-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    row = get_project_inspection_row("modules")
    row["kind"] = "changed"
    assert get_project_inspection_row("modules")["kind"] == "modules"
    kinds = get_project_inspection_filter_kinds("module_id")
    kinds.append("changed")
    assert get_project_inspection_filter_kinds("module_id") == contract["index"]["filter"]["module_id"]
    index_catalog[0]["id"] = "changed"
    assert get_project_inspection_index_catalog()[0]["id"] == "kind"

    with pytest.raises(ValueError, match="Unknown project inspection kind: missing"):
        get_project_inspection_row("missing")
    with pytest.raises(KeyError, match="unknown ParaDev project inspection filter 'missing'"):
        get_project_inspection_filter_kinds("missing")
    with pytest.raises(ValueError, match="Pass only one project inspection selector"):
        get_project_inspection_selection(kind="modules", index_name="filter", key="profile")
    with pytest.raises(ValueError, match="index_name requires key"):
        get_project_inspection_selection(index_name="filter")
    with pytest.raises(ValueError, match="Unsupported project inspection index"):
        get_project_inspection_selection(index_name="missing", key="profile")


def test_hb_api_table_lists_public_hb_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev.hb as hb
    from paradev.hb import (
        HB_API_TABLE_SCHEMA,
        HbApiRow,
        HbApiTable,
        get_hb_api_table,
        render_hb_api_reference_markdown,
    )

    table = get_hb_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_hb_api_reference_markdown()

    assert is_typeddict(HbApiRow)
    assert is_typeddict(HbApiTable)
    assert table["schema"] == HB_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == len(hb.__all__) == 27
    assert [row["symbol"] for row in rows] == list(hb.__all__)
    assert set(HbApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(HbApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "catalog": [
            "CATALOG_API_TABLE_ROWS",
            "CATALOG_API_TABLE_SCHEMA",
            "CATALOG_SCHEMA",
            "CatalogApiRow",
            "CatalogApiTable",
            "ENTITY_TYPES",
            "QUERY_SCHEMA",
            "REFRESH_SCHEMA",
            "SMOKE_SCHEMA",
            "STATUS_SCHEMA",
            "WRITE_SCHEMA",
            "catalog_completion_items",
            "catalog_preview",
            "catalog_query",
            "catalog_refresh",
            "catalog_smoke",
            "catalog_status",
            "catalog_write",
            "get_catalog_api_selection",
            "get_catalog_api_table",
            "render_catalog_api_reference_markdown",
        ],
        "api": [
            "HB_API_TABLE_SCHEMA",
            "HbApiRow",
            "HbApiTable",
            "get_hb_api_selection",
            "get_hb_api_table",
            "render_hb_api_reference_markdown",
        ],
    }
    assert table["feature_index"]["hb-api"] == table["module_index"]["api"]
    assert table["feature_index"]["catalog-api"] == [
        "CATALOG_API_TABLE_ROWS",
        "CATALOG_API_TABLE_SCHEMA",
        "CatalogApiRow",
        "CatalogApiTable",
        "get_catalog_api_table",
        "render_catalog_api_reference_markdown",
    ]
    assert table["feature_index"]["preview"] == ["CATALOG_SCHEMA", "catalog_preview"]
    assert table["feature_index"]["write"] == ["WRITE_SCHEMA", "catalog_write"]
    assert table["feature_index"]["status"] == ["STATUS_SCHEMA", "catalog_status"]
    assert table["feature_index"]["completion"] == ["catalog_completion_items"]
    assert table["kind_index"]["schema constant"] == [
        "CATALOG_API_TABLE_SCHEMA",
        "CATALOG_SCHEMA",
        "HB_API_TABLE_SCHEMA",
        "QUERY_SCHEMA",
        "REFRESH_SCHEMA",
        "SMOKE_SCHEMA",
        "STATUS_SCHEMA",
        "WRITE_SCHEMA",
    ]
    assert table["kind_index"]["TypedDict"] == [
        "CatalogApiRow",
        "CatalogApiTable",
        "HbApiRow",
        "HbApiTable",
    ]
    assert len(table["kind_index"]["function"]) == 13
    assert row_by_symbol["HB_API_TABLE_SCHEMA"]["value"] == HB_API_TABLE_SCHEMA
    assert row_by_symbol["CATALOG_API_TABLE_ROWS"]["returns"] == "tuple[37]"
    assert row_by_symbol["ENTITY_TYPES"]["value"] == "16 entity types"
    assert row_by_symbol["catalog_preview"]["returns"] == "dict[str, object]"
    assert row_by_symbol["catalog_completion_items"]["registry_seam"] == "LSP catalog completion"
    assert row_by_symbol["catalog_write"]["registry_seam"] == "HeavenBase SQLite backend"
    assert row_by_symbol["get_hb_api_table"]["returns"] == "HbApiTable"
    assert reference.startswith("# HeavenBase Facade API Reference\n")
    assert "Generated from `paradev.hb.get_hb_api_table()`." in reference
    assert (
        "| `api` | 6 | `HB_API_TABLE_SCHEMA`, `HbApiRow`, `HbApiTable`, `get_hb_api_selection`, `get_hb_api_table`, `render_hb_api_reference_markdown` |"
        in reference
    )
    assert (
        "| `catalog-api` | 6 | `CATALOG_API_TABLE_ROWS`, `CATALOG_API_TABLE_SCHEMA`, `CatalogApiRow`, "
        "`CatalogApiTable`, `get_catalog_api_table`, `render_catalog_api_reference_markdown` |"
    ) in reference
    assert (
        "| `catalog_preview` | `function` | `hb` | `catalog` | `preview` | `paradev.hb.catalog_preview` | "
        "`dict[str, object]` |  | `HeavenBase catalog integration` |"
    ) in reference
    manual = Path("docs/user-manual/hb-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_hb_api_table()["rows"][0]["symbol"] == "CATALOG_API_TABLE_ROWS"
    table["module_index"]["api"].append("changed")
    assert get_hb_api_table()["module_index"]["api"] == [
        "HB_API_TABLE_SCHEMA",
        "HbApiRow",
        "HbApiTable",
        "get_hb_api_selection",
        "get_hb_api_table",
        "render_hb_api_reference_markdown",
    ]


def test_bundle_surface_contract_is_sdk_owned() -> None:
    from paradev.surfaces.bundle import get_bundle_contract

    contract = get_bundle_contract()

    assert contract["identifier"] == "bundle"
    assert contract["status"] == "implemented"
    assert contract["runtime"] == "python-wheel-loopback"
    assert contract["tools"] == ["uv", "npm", "Vite", "setuptools"]
    assert contract["outputs"]["macos_application"] == "~/Applications/ParaDev.app"
    assert contract["platform_priority"] == ["macos-system-webview", "browser-fallback"]
    assert contract["sdk_owned"] is True


def test_surface_contract_catalog_lists_static_boundaries() -> None:
    from typing_extensions import is_typeddict

    from paradev.surfaces import (
        SURFACE_CONTRACT_IDS,
        SURFACE_CONTRACT_INDEX_CATALOG,
        SURFACE_CONTRACT_SUMMARY_SCHEMA,
        SurfaceContractIdentifier,
        SurfaceContractIndexCatalogRow,
        SurfaceContractPayload,
        SurfaceContractSummary,
        SurfaceContractSummaryRow,
        get_surface_contract,
        get_surface_contract_ids,
        get_surface_contract_index_catalog,
        get_surface_contract_selection,
        get_surface_contract_summary,
        get_surface_contract_summary_row,
        get_surface_contract_status_ids,
        get_surface_contracts,
        render_surface_contract_reference_markdown,
    )

    contracts = get_surface_contracts()
    index_catalog = get_surface_contract_index_catalog()
    summary = get_surface_contract_summary()
    summary_rows = {row["identifier"]: row for row in summary["rows"]}
    reference = render_surface_contract_reference_markdown()

    assert SurfaceContractIdentifier.__args__ == SURFACE_CONTRACT_IDS
    assert SurfaceContractPayload == dict[str, object]
    assert is_typeddict(SurfaceContractSummary)
    assert is_typeddict(SurfaceContractIndexCatalogRow)
    assert is_typeddict(SurfaceContractSummaryRow)
    assert tuple(index_catalog) == SURFACE_CONTRACT_INDEX_CATALOG
    assert set(SurfaceContractIndexCatalogRow.__annotations__) == {
        "id",
        "contract_path",
        "python_helper",
        "usage",
    }
    assert set(SurfaceContractSummary.__annotations__) == {
        "schema",
        "surface_count",
        "sdk_owned_count",
        "status_counts",
        "status_index",
        "index",
        "rows",
    }
    assert set(SurfaceContractSummaryRow.__annotations__) == set(summary["rows"][0])
    assert get_surface_contract_ids() == list(SURFACE_CONTRACT_IDS)
    assert [row["id"] for row in index_catalog] == ["identifier", "status"]
    assert index_catalog[0]["python_helper"] == "get_surface_contract_summary_row(identifier)"
    assert index_catalog[1]["python_helper"] == "get_surface_contract_status_ids(status)"
    assert list(contracts) == get_surface_contract_ids()
    assert summary["schema"] == SURFACE_CONTRACT_SUMMARY_SCHEMA
    assert summary["surface_count"] == len(get_surface_contract_ids())
    assert summary["sdk_owned_count"] == len(get_surface_contract_ids())
    assert summary["status_counts"] == {"scaffold": 3, "implemented": 3}
    assert summary["status_index"] == {
        "scaffold": ["cli", "mcp", "vscode"],
        "implemented": ["bundle", "lsp", "openapi"],
    }
    assert summary["index"] == {identifier: index for index, identifier in enumerate(get_surface_contract_ids())}
    assert get_surface_contract_status_ids("scaffold") == summary["status_index"]["scaffold"]
    assert get_surface_contract_status_ids("implemented") == summary["status_index"]["implemented"]
    assert get_surface_contract_selection() == summary
    assert get_surface_contract_selection(identifier="openapi") == contracts["openapi"]
    assert get_surface_contract_selection(status="implemented") == summary["status_index"]["implemented"]
    assert contracts["bundle"]["identifier"] == "bundle"
    assert contracts["cli"]["identifier"] == "cli"
    assert contracts["lsp"]["identifier"] == "lsp"
    assert contracts["mcp"]["identifier"] == "mcp"
    assert contracts["vscode"]["identifier"] == "vscode"
    assert contracts["openapi"]["openapi"] == "3.1.0"
    assert "/frontend-api" in contracts["openapi"]["paths"]
    assert summary_rows["openapi"]["runtime"] == "openapi-3.1.0"
    assert summary_rows["openapi"]["status"] == "implemented"
    assert summary_rows["openapi"]["sdk_owned"] is True
    assert "paths" in summary_rows["openapi"]["top_level_keys"]
    assert summary_rows["cli"]["top_level_keys"] == sorted(contracts["cli"])
    assert get_surface_contract_summary_row("cli") == summary_rows["cli"]
    assert get_surface_contract_summary_row("openapi") == summary_rows["openapi"]
    assert contracts["bundle"]["sdk_owned"] is True
    assert contracts["vscode"]["sdk_owned"] is True
    assert get_surface_contract("vscode") == contracts["vscode"]
    assert get_surface_contract("openapi")["paths"] == contracts["openapi"]["paths"]
    assert reference.startswith("# Surface Contract Reference\n")
    assert "Generated from `paradev.surfaces.get_surface_contract_summary()`." in reference
    assert "## Index Catalog / Index 目录" in reference
    assert '| `status` | `summary["status_index"][status]` | `get_surface_contract_status_ids(status)` | Contract status to ordered surface ids. |' in reference
    assert "| `implemented` | 3 | `bundle`, `lsp`, `openapi` |" in reference
    assert (
        "| `bundle` | `implemented` | `python-wheel-loopback` | yes | `identifier`, `inputs`, `outputs`, `platform_priority`, `runtime`, "
        "`sdk_owned`, `security`, `status`, `tools` |"
    ) in reference
    assert "| `openapi` | `implemented` | `openapi-3.1.0` | yes |" in reference
    manual = Path("docs/user-manual/surface-contract-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    contracts["vscode"]["identifier"] = "changed"
    assert get_surface_contracts()["vscode"]["identifier"] == "vscode"
    assert get_surface_contract("vscode")["identifier"] == "vscode"
    status_ids = get_surface_contract_status_ids("scaffold")
    status_ids.append("openapi")
    assert get_surface_contract_status_ids("scaffold") == summary["status_index"]["scaffold"]
    index_catalog[0]["id"] = "changed"
    assert get_surface_contract_index_catalog()[0]["id"] == "identifier"

    with pytest.raises(KeyError, match="unknown ParaDev surface contract 'desktop'"):
        get_surface_contract("desktop")
    with pytest.raises(KeyError, match="unknown ParaDev surface contract 'desktop'"):
        get_surface_contract_summary_row("desktop")
    with pytest.raises(KeyError, match="unknown ParaDev surface contract status 'retired'"):
        get_surface_contract_status_ids("retired")
    with pytest.raises(
        ValueError,
        match="Pass only one surface contract selector: identifier or status.",
    ):
        get_surface_contract_selection(identifier="openapi", status="implemented")


def test_package_api_table_lists_root_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev
    from paradev import (
        PACKAGE_API_TABLE_SCHEMA,
        PackageApiRow,
        PackageApiTable,
        get_package_api_table,
        render_package_api_reference_markdown,
    )

    table = get_package_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_package_api_reference_markdown()

    assert is_typeddict(PackageApiRow)
    assert is_typeddict(PackageApiTable)
    assert table["schema"] == PACKAGE_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == 15
    assert [row["symbol"] for row in rows] == list(paradev.__all__)
    assert set(PackageApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(PackageApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "sdk.architecture": [
            "ArchitectureSpec",
            "SurfaceSpec",
            "get_architecture_spec",
        ],
        "config": ["CM_PARADEV"],
        "package_api": [
            "PACKAGE_API_TABLE_SCHEMA",
            "PackageApiRow",
            "PackageApiTable",
            "get_package_api_selection",
            "get_package_api_table",
            "render_package_api_reference_markdown",
        ],
        "sdk.project": [
            "ParaDevProject",
            "Project",
            "ProjectManifestError",
            "open_project",
        ],
        "version": ["__version__"],
    }
    assert table["feature_index"] == {
        "architecture": ["ArchitectureSpec", "SurfaceSpec", "get_architecture_spec"],
        "config": ["CM_PARADEV"],
        "package-api": [
            "PACKAGE_API_TABLE_SCHEMA",
            "PackageApiRow",
            "PackageApiTable",
            "get_package_api_selection",
            "get_package_api_table",
            "render_package_api_reference_markdown",
        ],
        "projects": ["ParaDevProject", "Project", "open_project"],
        "errors": ["ProjectManifestError"],
        "version": ["__version__"],
    }
    assert table["kind_index"]["dataclass"] == [
        "ArchitectureSpec",
        "ParaDevProject",
        "Project",
        "SurfaceSpec",
    ]
    assert table["kind_index"]["function"] == [
        "get_architecture_spec",
        "get_package_api_selection",
        "get_package_api_table",
        "open_project",
        "render_package_api_reference_markdown",
    ]
    assert table["kind_index"]["ConfigManager"] == ["CM_PARADEV"]
    assert table["kind_index"]["TypedDict"] == ["PackageApiRow", "PackageApiTable"]
    assert row_by_symbol["PACKAGE_API_TABLE_SCHEMA"]["value"] == PACKAGE_API_TABLE_SCHEMA
    assert row_by_symbol["CM_PARADEV"]["registry_seam"] == "HeavenBase ConfigManager"
    assert row_by_symbol["Project"]["registry_seam"] == "project family/template registry"
    assert row_by_symbol["__version__"]["returns"] == "str"
    assert row_by_symbol["get_package_api_table"]["returns"] == "PackageApiTable"
    assert row_by_symbol["render_package_api_reference_markdown"]["returns"] == "str"
    assert reference.startswith("# Package API Reference\n")
    assert "Generated from `paradev.get_package_api_table()`." in reference
    assert (
        "| `package_api` | 6 | `PACKAGE_API_TABLE_SCHEMA`, `PackageApiRow`, `PackageApiTable`, "
        "`get_package_api_selection`, `get_package_api_table`, `render_package_api_reference_markdown` |" in reference
    )
    assert "| `projects` | 3 | `ParaDevProject`, `Project`, `open_project` |" in reference
    assert (
        "| `Project` | `dataclass` | `package` | `sdk.project` | `projects` | `paradev.Project` | " "`Project class` |  | `project family/template registry` |"
    ) in reference
    manual = Path("docs/user-manual/package-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_package_api_table()["rows"][0]["symbol"] == "ArchitectureSpec"
    table["module_index"]["config"].append("changed")
    assert get_package_api_table()["module_index"]["config"] == ["CM_PARADEV"]


def test_config_api_table_lists_public_config_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev.config as config
    from paradev.config import (
        CONFIG_API_TABLE_SCHEMA,
        BOOTSTRAP_CONFIG,
        DEFAULT_CONFIG,
        ConfigApiRow,
        ConfigApiTable,
        get_config_api_table,
        render_config_api_reference_markdown,
    )

    table = get_config_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_config_api_reference_markdown()
    config_facade_symbols = [
        "DEFAULT_CONFIG",
        "BOOTSTRAP_CONFIG",
        "CM_PARADEV",
        "config_get",
        "config_list",
        "config_set",
        "config_unset",
        "config_scopes",
        "config_history",
    ]
    config_helper_symbols = [
        "config_get",
        "config_list",
        "config_set",
        "config_unset",
        "config_scopes",
        "config_history",
    ]

    assert is_typeddict(ConfigApiRow)
    assert is_typeddict(ConfigApiTable)
    assert table["schema"] == CONFIG_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == len(config.__all__) == 15
    assert [row["symbol"] for row in rows] == list(config.__all__)
    assert set(ConfigApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(ConfigApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "config": config_facade_symbols,
        "config_api": [
            "CONFIG_API_TABLE_SCHEMA",
            "ConfigApiRow",
            "ConfigApiTable",
            "get_config_api_selection",
            "get_config_api_table",
            "render_config_api_reference_markdown",
        ],
    }
    assert table["feature_index"] == {
        "defaults": ["DEFAULT_CONFIG", "BOOTSTRAP_CONFIG"],
        "config-manager": ["CM_PARADEV"],
        "config": config_helper_symbols,
        "config-api": [
            "CONFIG_API_TABLE_SCHEMA",
            "ConfigApiRow",
            "ConfigApiTable",
            "get_config_api_selection",
            "get_config_api_table",
            "render_config_api_reference_markdown",
        ],
    }
    assert table["kind_index"] == {
        "dict constant": ["DEFAULT_CONFIG", "BOOTSTRAP_CONFIG"],
        "ConfigManager": ["CM_PARADEV"],
        "schema constant": ["CONFIG_API_TABLE_SCHEMA"],
        "TypedDict": ["ConfigApiRow", "ConfigApiTable"],
        "function": [
            "config_get",
            "config_list",
            "config_set",
            "config_unset",
            "config_scopes",
            "config_history",
            "get_config_api_selection",
            "get_config_api_table",
            "render_config_api_reference_markdown",
        ],
    }
    assert row_by_symbol["DEFAULT_CONFIG"]["returns"] == f"dict[{len(DEFAULT_CONFIG)}]"
    assert row_by_symbol["BOOTSTRAP_CONFIG"]["returns"] == f"dict[{len(BOOTSTRAP_CONFIG)}]"
    assert row_by_symbol["CM_PARADEV"]["registry_seam"] == "HeavenBase ConfigManager"
    assert row_by_symbol["config_get"]["returns"] == "object"
    assert row_by_symbol["config_list"]["returns"] == "list[dict[str, object]]"
    assert row_by_symbol["config_set"]["returns"] == "bool"
    assert row_by_symbol["config_unset"]["returns"] == "bool"
    assert row_by_symbol["config_scopes"]["returns"] == "object"
    assert row_by_symbol["config_history"]["returns"] == "object"
    assert row_by_symbol["config_get"]["registry_seam"] == "HeavenBase ConfigManager"
    assert row_by_symbol["CONFIG_API_TABLE_SCHEMA"]["value"] == CONFIG_API_TABLE_SCHEMA
    assert row_by_symbol["get_config_api_table"]["returns"] == "ConfigApiTable"
    assert row_by_symbol["render_config_api_reference_markdown"]["returns"] == "str"
    assert reference.startswith("# Config API Reference\n")
    assert "Generated from `paradev.config.get_config_api_table()`." in reference
    assert (
        "| `config` | 9 | `DEFAULT_CONFIG`, `BOOTSTRAP_CONFIG`, `CM_PARADEV`, `config_get`, `config_list`, "
        "`config_set`, `config_unset`, `config_scopes`, `config_history` |"
    ) in reference
    assert ("| `config` | 6 | `config_get`, `config_list`, `config_set`, `config_unset`, `config_scopes`, " "`config_history` |") in reference
    assert (
        "| `config-api` | 6 | `CONFIG_API_TABLE_SCHEMA`, `ConfigApiRow`, `ConfigApiTable`, "
        "`get_config_api_selection`, `get_config_api_table`, `render_config_api_reference_markdown` |"
    ) in reference
    assert (
        "| `CM_PARADEV` | `ConfigManager` | `config` | `config` | `config-manager` | "
        "`paradev.config.CM_PARADEV` | `ConfigManager` |  | `HeavenBase ConfigManager` |"
    ) in reference
    assert (
        "| `config_get` | `function` | `config` | `config` | `config` | `paradev.config.config_get` | " "`object` |  | `HeavenBase ConfigManager` |"
    ) in reference
    manual = Path("docs/user-manual/config-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_config_api_table()["rows"][0]["symbol"] == "DEFAULT_CONFIG"
    table["module_index"]["config_api"].append("changed")
    assert get_config_api_table()["module_index"]["config_api"] == [
        "CONFIG_API_TABLE_SCHEMA",
        "ConfigApiRow",
        "ConfigApiTable",
        "get_config_api_selection",
        "get_config_api_table",
        "render_config_api_reference_markdown",
    ]


def test_gui_api_table_lists_public_gui_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev.gui as gui
    from paradev.gui import (
        GUI_API_TABLE_SCHEMA,
        GuiApiRow,
        GuiApiTable,
        build_parser,
        get_gui_api_table,
        main,
        render_gui_api_reference_markdown,
    )

    table = get_gui_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_gui_api_reference_markdown()

    assert is_typeddict(GuiApiRow)
    assert is_typeddict(GuiApiTable)
    assert table["schema"] == GUI_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == len(gui.__all__) == 8
    assert [row["symbol"] for row in rows] == list(gui.__all__)
    assert build_parser().prog == "paradev-gui"
    assert callable(main)
    assert set(GuiApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(GuiApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "gui": ["build_parser", "main"],
        "gui_api": [
            "GUI_API_TABLE_SCHEMA",
            "GuiApiRow",
            "GuiApiTable",
            "get_gui_api_selection",
            "get_gui_api_table",
            "render_gui_api_reference_markdown",
        ],
    }
    assert table["feature_index"] == {
        "launcher": ["build_parser", "main"],
        "gui-api": [
            "GUI_API_TABLE_SCHEMA",
            "GuiApiRow",
            "GuiApiTable",
            "get_gui_api_selection",
            "get_gui_api_table",
            "render_gui_api_reference_markdown",
        ],
    }
    assert table["kind_index"] == {
        "function": [
            "build_parser",
            "main",
            "get_gui_api_selection",
            "get_gui_api_table",
            "render_gui_api_reference_markdown",
        ],
        "schema constant": ["GUI_API_TABLE_SCHEMA"],
        "TypedDict": ["GuiApiRow", "GuiApiTable"],
    }
    assert row_by_symbol["build_parser"]["returns"] == "argparse.ArgumentParser"
    assert row_by_symbol["main"]["returns"] == "int"
    assert row_by_symbol["main"]["surface"] == "desktop"
    assert row_by_symbol["GUI_API_TABLE_SCHEMA"]["value"] == GUI_API_TABLE_SCHEMA
    assert row_by_symbol["get_gui_api_table"]["returns"] == "GuiApiTable"
    assert row_by_symbol["render_gui_api_reference_markdown"]["returns"] == "str"
    assert reference.startswith("# GUI API Reference\n")
    assert "Generated from `paradev.gui.get_gui_api_table()`." in reference
    assert "| `gui` | 2 | `build_parser`, `main` |" in reference
    assert (
        "| `gui-api` | 6 | `GUI_API_TABLE_SCHEMA`, `GuiApiRow`, `GuiApiTable`, "
        "`get_gui_api_selection`, `get_gui_api_table`, `render_gui_api_reference_markdown` |"
    ) in reference
    assert (
        "| `main` | `function` | `gui` | `gui` | `launcher` | `paradev.gui.main` | " "`int` |  | `Python GUI script entry point` | `desktop` |"
    ) in reference
    manual = Path("docs/user-manual/gui-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_gui_api_table()["rows"][0]["symbol"] == "build_parser"
    table["module_index"]["gui_api"].append("changed")
    assert get_gui_api_table()["module_index"]["gui_api"] == [
        "GUI_API_TABLE_SCHEMA",
        "GuiApiRow",
        "GuiApiTable",
        "get_gui_api_selection",
        "get_gui_api_table",
        "render_gui_api_reference_markdown",
    ]


def test_desktop_api_table_lists_public_desktop_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev.desktop as desktop
    from paradev.desktop import (
        DESKTOP_API_TABLE_SCHEMA,
        DESKTOP_STATE_SCHEMA,
        BUILD_RUN_SCHEMA,
        BUILD_RUNS_SCHEMA,
        PROJECT_PACKAGE_CATALOG_SCHEMA,
        PROJECT_PACKAGE_INSTALL_SCHEMA,
        DesktopApiRow,
        DesktopApiTable,
        DesktopBuildRegistry,
        desktop_state,
        get_desktop_api_table,
        render_desktop_api_reference_markdown,
    )

    table = get_desktop_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_desktop_api_reference_markdown()

    assert is_typeddict(DesktopApiRow)
    assert is_typeddict(DesktopApiTable)
    assert table["schema"] == DESKTOP_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == len(desktop.__all__) == 57
    assert [row["symbol"] for row in rows] == list(desktop.__all__)
    assert callable(desktop_state)
    assert isinstance(DesktopBuildRegistry(), DesktopBuildRegistry)
    assert set(DesktopApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(DesktopApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "sdk.project": ["DESKTOP_STATE_SCHEMA", "desktop_state"],
        "desktop.builds": [
            "BUILD_RUN_SCHEMA",
            "BUILD_RUNS_SCHEMA",
            "DesktopBuildRegistry",
            "desktop_start_build",
            "desktop_build_runs",
            "desktop_build_status",
            "desktop_interrupt_build",
        ],
        "desktop.local": [
            "AI_CHAT_SCHEMA",
            "AI_CHAT_PROFILES_SCHEMA",
            "AI_CHAT_PROFILES_CONFIG_KEY",
            "AI_CHAT_PROFILES_CONFIG_SCHEMA",
            "BINARY_SOURCE_SCHEMA",
            "DESKTOP_CONFIG_KEYS",
            "DESKTOP_APP_CONFIG_KEY",
            "desktop_chat",
            "desktop_chat_profiles",
            "desktop_config_rows",
            "desktop_reset_chat_profile",
            "desktop_write_chat_profile",
            "desktop_test_llm_route",
            "render_desktop_typescript",
            "desktop_source_path",
            "desktop_read_text_source",
            "desktop_read_binary_source",
            "desktop_binary_source",
            "desktop_browser_cache_path",
            "read_project_browser_cache",
            "desktop_write_browser_cache",
            "desktop_thumbnail_cache_path",
            "desktop_read_thumbnail_cache",
            "desktop_write_thumbnail_cache",
            "desktop_read_app_config",
            "desktop_write_app_config",
            "desktop_read_config_value",
            "desktop_write_config_value",
            "desktop_mime_type",
            "desktop_dependency_status",
            "desktop_install_dependency",
        ],
        "desktop.project_packages": [
            "PROJECT_PACKAGE_CATALOG_SCHEMA",
            "PROJECT_PACKAGE_INSTALL_SCHEMA",
            "desktop_project_package_catalog",
            "desktop_install_project_package",
        ],
        "desktop.shell": [
            "desktop_project_build_command",
            "desktop_hoi4_launch_command",
            "desktop_run_hoi4",
            "desktop_open_path_command",
            "desktop_open_path",
            "desktop_open_path_targets",
            "desktop_path_status",
        ],
        "desktop.api": [
            "DESKTOP_API_TABLE_SCHEMA",
            "DesktopApiRow",
            "DesktopApiTable",
            "get_desktop_api_selection",
            "get_desktop_api_table",
            "render_desktop_api_reference_markdown",
        ],
    }
    assert table["feature_index"] == {
        "state": ["DESKTOP_STATE_SCHEMA", "desktop_state"],
        "ai-chat": [
            "AI_CHAT_SCHEMA",
            "AI_CHAT_PROFILES_SCHEMA",
            "AI_CHAT_PROFILES_CONFIG_KEY",
            "AI_CHAT_PROFILES_CONFIG_SCHEMA",
            "desktop_chat",
            "desktop_chat_profiles",
            "desktop_reset_chat_profile",
            "desktop_write_chat_profile",
            "desktop_test_llm_route",
        ],
        "sources": [
            "BINARY_SOURCE_SCHEMA",
            "desktop_source_path",
            "desktop_read_text_source",
            "desktop_read_binary_source",
            "desktop_binary_source",
            "desktop_mime_type",
        ],
        "config": [
            "DESKTOP_CONFIG_KEYS",
            "DESKTOP_APP_CONFIG_KEY",
            "desktop_config_rows",
            "render_desktop_typescript",
            "desktop_read_app_config",
            "desktop_write_app_config",
            "desktop_read_config_value",
            "desktop_write_config_value",
        ],
        "cache": [
            "desktop_browser_cache_path",
            "read_project_browser_cache",
            "desktop_write_browser_cache",
            "desktop_thumbnail_cache_path",
            "desktop_read_thumbnail_cache",
            "desktop_write_thumbnail_cache",
        ],
        "dependencies": ["desktop_dependency_status", "desktop_install_dependency"],
        "project-packages": [
            "PROJECT_PACKAGE_CATALOG_SCHEMA",
            "PROJECT_PACKAGE_INSTALL_SCHEMA",
            "desktop_project_package_catalog",
            "desktop_install_project_package",
        ],
        "build": [
            "BUILD_RUN_SCHEMA",
            "BUILD_RUNS_SCHEMA",
            "DesktopBuildRegistry",
            "desktop_start_build",
            "desktop_build_runs",
            "desktop_build_status",
            "desktop_interrupt_build",
            "desktop_project_build_command",
        ],
        "game-launch": ["desktop_hoi4_launch_command", "desktop_run_hoi4"],
        "open-path": [
            "desktop_open_path_command",
            "desktop_open_path",
            "desktop_open_path_targets",
            "desktop_path_status",
        ],
        "desktop-api": [
            "DESKTOP_API_TABLE_SCHEMA",
            "DesktopApiRow",
            "DesktopApiTable",
            "get_desktop_api_selection",
            "get_desktop_api_table",
            "render_desktop_api_reference_markdown",
        ],
    }
    assert table["kind_index"] == {
        "schema constant": [
            "DESKTOP_STATE_SCHEMA",
            "BUILD_RUN_SCHEMA",
            "BUILD_RUNS_SCHEMA",
            "AI_CHAT_SCHEMA",
            "AI_CHAT_PROFILES_SCHEMA",
            "AI_CHAT_PROFILES_CONFIG_SCHEMA",
            "BINARY_SOURCE_SCHEMA",
            "PROJECT_PACKAGE_CATALOG_SCHEMA",
            "PROJECT_PACKAGE_INSTALL_SCHEMA",
            "DESKTOP_API_TABLE_SCHEMA",
        ],
        "str": ["AI_CHAT_PROFILES_CONFIG_KEY", "DESKTOP_APP_CONFIG_KEY"],
        "tuple": ["DESKTOP_CONFIG_KEYS"],
        "function": [
            "desktop_state",
            "desktop_start_build",
            "desktop_build_runs",
            "desktop_build_status",
            "desktop_interrupt_build",
            "desktop_chat",
            "desktop_chat_profiles",
            "desktop_config_rows",
            "desktop_reset_chat_profile",
            "desktop_write_chat_profile",
            "desktop_test_llm_route",
            "render_desktop_typescript",
            "desktop_source_path",
            "desktop_read_text_source",
            "desktop_read_binary_source",
            "desktop_binary_source",
            "desktop_browser_cache_path",
            "read_project_browser_cache",
            "desktop_write_browser_cache",
            "desktop_thumbnail_cache_path",
            "desktop_read_thumbnail_cache",
            "desktop_write_thumbnail_cache",
            "desktop_read_app_config",
            "desktop_write_app_config",
            "desktop_read_config_value",
            "desktop_write_config_value",
            "desktop_mime_type",
            "desktop_dependency_status",
            "desktop_install_dependency",
            "desktop_project_package_catalog",
            "desktop_install_project_package",
            "desktop_project_build_command",
            "desktop_hoi4_launch_command",
            "desktop_run_hoi4",
            "desktop_open_path_command",
            "desktop_open_path",
            "desktop_open_path_targets",
            "desktop_path_status",
            "get_desktop_api_selection",
            "get_desktop_api_table",
            "render_desktop_api_reference_markdown",
        ],
        "class": ["DesktopBuildRegistry"],
        "TypedDict": ["DesktopApiRow", "DesktopApiTable"],
    }
    assert row_by_symbol["DESKTOP_STATE_SCHEMA"]["value"] == DESKTOP_STATE_SCHEMA
    assert row_by_symbol["BUILD_RUN_SCHEMA"]["value"] == BUILD_RUN_SCHEMA
    assert row_by_symbol["BUILD_RUNS_SCHEMA"]["value"] == BUILD_RUNS_SCHEMA
    assert row_by_symbol["DesktopBuildRegistry"]["kind"] == "class"
    assert row_by_symbol["desktop_start_build"]["returns"] == "dict[str, object]"
    assert row_by_symbol["desktop_start_build"]["registry_seam"] == "desktop build lifecycle and CLI command planner"
    assert row_by_symbol["desktop_build_runs"]["registry_seam"] == "desktop build lifecycle and CLI command planner"
    assert row_by_symbol["desktop_build_status"]["registry_seam"] == "desktop build lifecycle and CLI command planner"
    assert row_by_symbol["desktop_interrupt_build"]["registry_seam"] == "desktop build lifecycle and CLI command planner"
    assert row_by_symbol["AI_CHAT_SCHEMA"]["value"] == "paradev.desktop.ai-chat.v1"
    assert row_by_symbol["AI_CHAT_PROFILES_SCHEMA"]["value"] == "paradev.desktop.ai-chat-profiles.v1"
    assert row_by_symbol["AI_CHAT_PROFILES_CONFIG_SCHEMA"]["value"] == "paradev.sdk.ai-chat-profile-overrides.v1"
    assert row_by_symbol["desktop_state"]["returns"] == "dict[str, object]"
    assert row_by_symbol["desktop_state"]["surface"] == "desktop"
    assert row_by_symbol["desktop_state"]["registry_seam"] == "desktop state contract"
    assert row_by_symbol["desktop_chat"]["returns"] == "dict[str, object]"
    assert row_by_symbol["desktop_chat"]["registry_seam"] == "HeavenBase desktop AI chat"
    assert row_by_symbol["desktop_chat_profiles"]["returns"] == "dict[str, object]"
    assert row_by_symbol["desktop_chat_profiles"]["registry_seam"] == "HeavenBase desktop AI chat"
    assert row_by_symbol["desktop_config_rows"]["returns"] == "list[dict[str, object]]"
    assert row_by_symbol["desktop_config_rows"]["registry_seam"] == "CM_PARADEV desktop GUI config"
    assert row_by_symbol["desktop_reset_chat_profile"]["returns"] == "dict[str, object]"
    assert row_by_symbol["desktop_reset_chat_profile"]["registry_seam"] == "HeavenBase desktop AI chat"
    assert row_by_symbol["desktop_write_chat_profile"]["returns"] == "dict[str, object]"
    assert row_by_symbol["desktop_write_chat_profile"]["registry_seam"] == "HeavenBase desktop AI chat"
    assert row_by_symbol["desktop_test_llm_route"]["registry_seam"] == "HeavenBase desktop AI chat"
    assert row_by_symbol["desktop_read_binary_source"]["returns"] == "dict[str, object]"
    assert row_by_symbol["desktop_read_binary_source"]["registry_seam"] == "project-contained desktop source files"
    assert row_by_symbol["desktop_write_thumbnail_cache"]["registry_seam"] == "project .paradev desktop cache"
    assert row_by_symbol["DESKTOP_CONFIG_KEYS"]["registry_seam"] == "CM_PARADEV desktop GUI config"
    assert row_by_symbol["render_desktop_typescript"]["returns"] == "str"
    assert row_by_symbol["desktop_write_app_config"]["registry_seam"] == "CM_PARADEV desktop GUI config"
    assert row_by_symbol["desktop_read_config_value"]["returns"] == "dict[str, object]"
    assert row_by_symbol["desktop_write_config_value"]["registry_seam"] == "CM_PARADEV desktop GUI config"
    assert row_by_symbol["desktop_dependency_status"]["registry_seam"] == "desktop dependency manager"
    assert row_by_symbol["desktop_install_dependency"]["registry_seam"] == "desktop dependency manager"
    assert row_by_symbol["PROJECT_PACKAGE_CATALOG_SCHEMA"]["value"] == PROJECT_PACKAGE_CATALOG_SCHEMA
    assert row_by_symbol["PROJECT_PACKAGE_INSTALL_SCHEMA"]["value"] == PROJECT_PACKAGE_INSTALL_SCHEMA
    assert row_by_symbol["desktop_project_package_catalog"]["returns"] == "ProjectPackageCatalog"
    assert row_by_symbol["desktop_install_project_package"]["registry_seam"] == "publisher-verified project package catalog and installer"
    assert row_by_symbol["desktop_project_build_command"]["registry_seam"] == "desktop build lifecycle and CLI command planner"
    assert row_by_symbol["desktop_run_hoi4"]["registry_seam"] == "desktop HOI4 launcher command"
    assert row_by_symbol["desktop_open_path"]["registry_seam"] == "desktop local path opener"
    assert row_by_symbol["desktop_open_path_targets"]["returns"] == "dict[str, object]"
    assert row_by_symbol["desktop_open_path_targets"]["registry_seam"] == "desktop local path opener"
    assert row_by_symbol["desktop_path_status"]["returns"] == "dict[str, object]"
    assert row_by_symbol["desktop_path_status"]["registry_seam"] == "desktop local path opener"
    assert row_by_symbol["DESKTOP_API_TABLE_SCHEMA"]["value"] == DESKTOP_API_TABLE_SCHEMA
    assert row_by_symbol["get_desktop_api_table"]["returns"] == "DesktopApiTable"
    assert row_by_symbol["render_desktop_api_reference_markdown"]["returns"] == "str"
    assert reference.startswith("# Desktop API Reference\n")
    assert "Generated from `paradev.desktop.get_desktop_api_table()`." in reference
    assert "| `sdk.project` | 2 | `DESKTOP_STATE_SCHEMA`, `desktop_state` |" in reference
    assert (
        "| `desktop.builds` | 7 | `BUILD_RUN_SCHEMA`, `BUILD_RUNS_SCHEMA`, `DesktopBuildRegistry`, "
        "`desktop_start_build`, `desktop_build_runs`, `desktop_build_status`, `desktop_interrupt_build` |"
    ) in reference
    assert (
        "| `desktop.local` | 31 | `AI_CHAT_SCHEMA`, `AI_CHAT_PROFILES_SCHEMA`, `AI_CHAT_PROFILES_CONFIG_KEY`, "
        "`AI_CHAT_PROFILES_CONFIG_SCHEMA`, `BINARY_SOURCE_SCHEMA`, `DESKTOP_CONFIG_KEYS`, `DESKTOP_APP_CONFIG_KEY`, "
        "`desktop_chat`, `desktop_chat_profiles`, `desktop_config_rows`, `desktop_reset_chat_profile`, `desktop_write_chat_profile`, `desktop_test_llm_route`, `render_desktop_typescript`, `desktop_source_path`, `desktop_read_text_source`, `desktop_read_binary_source`, "
        "`desktop_binary_source`, `desktop_browser_cache_path`, `read_project_browser_cache`, `desktop_write_browser_cache`, "
        "`desktop_thumbnail_cache_path`, `desktop_read_thumbnail_cache`, `desktop_write_thumbnail_cache`, `desktop_read_app_config`, "
        "`desktop_write_app_config`, `desktop_read_config_value`, `desktop_write_config_value`, `desktop_mime_type`, `desktop_dependency_status`, `desktop_install_dependency` |"
    ) in reference
    assert (
        "| `desktop.project_packages` | 4 | `PROJECT_PACKAGE_CATALOG_SCHEMA`, "
        "`PROJECT_PACKAGE_INSTALL_SCHEMA`, `desktop_project_package_catalog`, "
        "`desktop_install_project_package` |"
    ) in reference
    assert (
        "| `config` | 8 | `DESKTOP_CONFIG_KEYS`, `DESKTOP_APP_CONFIG_KEY`, `desktop_config_rows`, `render_desktop_typescript`, `desktop_read_app_config`, `desktop_write_app_config`, `desktop_read_config_value`, `desktop_write_config_value` |"
        in reference
    )
    assert (
        "| `ai-chat` | 9 | `AI_CHAT_SCHEMA`, `AI_CHAT_PROFILES_SCHEMA`, `AI_CHAT_PROFILES_CONFIG_KEY`, "
        "`AI_CHAT_PROFILES_CONFIG_SCHEMA`, `desktop_chat`, `desktop_chat_profiles`, `desktop_reset_chat_profile`, `desktop_write_chat_profile`, `desktop_test_llm_route` |"
    ) in reference
    assert "| `dependencies` | 2 | `desktop_dependency_status`, `desktop_install_dependency` |" in reference
    assert (
        "| `project-packages` | 4 | `PROJECT_PACKAGE_CATALOG_SCHEMA`, "
        "`PROJECT_PACKAGE_INSTALL_SCHEMA`, `desktop_project_package_catalog`, "
        "`desktop_install_project_package` |"
    ) in reference
    assert (
        "| `desktop.shell` | 7 | `desktop_project_build_command`, `desktop_hoi4_launch_command`, "
        "`desktop_run_hoi4`, `desktop_open_path_command`, `desktop_open_path`, `desktop_open_path_targets`, `desktop_path_status` |"
    ) in reference
    assert (
        "| `build` | 8 | `BUILD_RUN_SCHEMA`, `BUILD_RUNS_SCHEMA`, `DesktopBuildRegistry`, `desktop_start_build`, "
        "`desktop_build_runs`, `desktop_build_status`, `desktop_interrupt_build`, `desktop_project_build_command` |"
    ) in reference
    assert "| `game-launch` | 2 | `desktop_hoi4_launch_command`, `desktop_run_hoi4` |" in reference
    assert "| `open-path` | 4 | `desktop_open_path_command`, `desktop_open_path`, `desktop_open_path_targets`, `desktop_path_status` |" in reference
    assert (
        "| `desktop-api` | 6 | `DESKTOP_API_TABLE_SCHEMA`, `DesktopApiRow`, `DesktopApiTable`, "
        "`get_desktop_api_selection`, `get_desktop_api_table`, `render_desktop_api_reference_markdown` |"
    ) in reference
    assert (
        "| `desktop_state` | `function` | `desktop` | `sdk.project` | `state` | "
        "`paradev.desktop.desktop_state` | `dict[str, object]` |  | `desktop state contract` |"
    ) in reference
    assert "| `desktop_read_binary_source` | `function` | `desktop` | `desktop.local` | `sources` |" in reference
    assert "| `desktop_start_build` | `function` | `desktop` | `desktop.builds` | `build` |" in reference
    assert "| `desktop_run_hoi4` | `function` | `desktop` | `desktop.shell` | `game-launch` |" in reference
    manual = Path("docs/user-manual/desktop-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_desktop_api_table()["rows"][0]["symbol"] == "DESKTOP_STATE_SCHEMA"
    table["module_index"]["desktop.api"].append("changed")
    assert get_desktop_api_table()["module_index"]["desktop.api"] == [
        "DESKTOP_API_TABLE_SCHEMA",
        "DesktopApiRow",
        "DesktopApiTable",
        "get_desktop_api_selection",
        "get_desktop_api_table",
        "render_desktop_api_reference_markdown",
    ]


def test_games_api_table_lists_public_games_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev.games as games
    from paradev.games import (
        GAMES_API_TABLE_SCHEMA,
        PROFILE_REGISTRIES,
        GamesApiRow,
        GamesApiTable,
        get_games_api_table,
        registry_for_profile,
        render_games_api_reference_markdown,
    )

    table = get_games_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_games_api_reference_markdown()

    assert is_typeddict(GamesApiRow)
    assert is_typeddict(GamesApiTable)
    assert table["schema"] == GAMES_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == len(games.__all__) == 8
    assert [row["symbol"] for row in rows] == list(games.__all__)
    assert "hoi4" in PROFILE_REGISTRIES
    assert callable(registry_for_profile)
    assert set(GamesApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(GamesApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "games": ["PROFILE_REGISTRIES", "registry_for_profile"],
        "games.api": [
            "GAMES_API_TABLE_SCHEMA",
            "GamesApiRow",
            "GamesApiTable",
            "get_games_api_selection",
            "get_games_api_table",
            "render_games_api_reference_markdown",
        ],
    }
    assert table["feature_index"] == {
        "profiles": ["PROFILE_REGISTRIES", "registry_for_profile"],
        "games-api": [
            "GAMES_API_TABLE_SCHEMA",
            "GamesApiRow",
            "GamesApiTable",
            "get_games_api_selection",
            "get_games_api_table",
            "render_games_api_reference_markdown",
        ],
    }
    assert table["kind_index"] == {
        "dict constant": ["PROFILE_REGISTRIES"],
        "function": [
            "registry_for_profile",
            "get_games_api_selection",
            "get_games_api_table",
            "render_games_api_reference_markdown",
        ],
        "schema constant": ["GAMES_API_TABLE_SCHEMA"],
        "TypedDict": ["GamesApiRow", "GamesApiTable"],
    }
    assert row_by_symbol["PROFILE_REGISTRIES"]["returns"] == f"dict[{len(PROFILE_REGISTRIES)}]"
    assert row_by_symbol["PROFILE_REGISTRIES"]["value"] == "hoi4"
    assert row_by_symbol["registry_for_profile"]["returns"] == "BuildRegistry"
    assert row_by_symbol["registry_for_profile"]["registry_seam"] == "game profile registry"
    assert row_by_symbol["GAMES_API_TABLE_SCHEMA"]["value"] == GAMES_API_TABLE_SCHEMA
    assert row_by_symbol["get_games_api_table"]["returns"] == "GamesApiTable"
    assert row_by_symbol["render_games_api_reference_markdown"]["returns"] == "str"
    assert reference.startswith("# Games API Reference\n")
    assert "Generated from `paradev.games.get_games_api_table()`." in reference
    assert "| `games` | 2 | `PROFILE_REGISTRIES`, `registry_for_profile` |" in reference
    assert (
        "| `games-api` | 6 | `GAMES_API_TABLE_SCHEMA`, `GamesApiRow`, `GamesApiTable`, "
        "`get_games_api_selection`, `get_games_api_table`, `render_games_api_reference_markdown` |"
    ) in reference
    assert (
        "| `registry_for_profile` | `function` | `games` | `games` | `profiles` | "
        "`paradev.games.registry_for_profile` | `BuildRegistry` |  | `game profile registry` |"
    ) in reference
    manual = Path("docs/user-manual/games-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_games_api_table()["rows"][0]["symbol"] == "PROFILE_REGISTRIES"
    table["module_index"]["games.api"].append("changed")
    assert get_games_api_table()["module_index"]["games.api"] == [
        "GAMES_API_TABLE_SCHEMA",
        "GamesApiRow",
        "GamesApiTable",
        "get_games_api_selection",
        "get_games_api_table",
        "render_games_api_reference_markdown",
    ]


def test_project_facade_api_table_lists_project_package_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev.project as project
    from paradev.project import (
        PROJECT_FACADE_API_TABLE_SCHEMA,
        ProjectFacadeApiRow,
        ProjectFacadeApiTable,
        get_project_facade_api_table,
        render_project_facade_api_reference_markdown,
    )

    table = get_project_facade_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_project_facade_api_reference_markdown()

    assert is_typeddict(ProjectFacadeApiRow)
    assert is_typeddict(ProjectFacadeApiTable)
    assert table["schema"] == PROJECT_FACADE_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == 8
    assert [row["symbol"] for row in rows] == list(project.__all__)
    assert set(ProjectFacadeApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(ProjectFacadeApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "sdk.project": ["Project", "ProjectManifestError"],
        "api": [
            "PROJECT_FACADE_API_TABLE_SCHEMA",
            "ProjectFacadeApiRow",
            "ProjectFacadeApiTable",
            "get_project_facade_api_selection",
            "get_project_facade_api_table",
            "render_project_facade_api_reference_markdown",
        ],
    }
    assert table["feature_index"] == {
        "projects": ["Project"],
        "errors": ["ProjectManifestError"],
        "project-facade-api": [
            "PROJECT_FACADE_API_TABLE_SCHEMA",
            "ProjectFacadeApiRow",
            "ProjectFacadeApiTable",
            "get_project_facade_api_selection",
            "get_project_facade_api_table",
            "render_project_facade_api_reference_markdown",
        ],
    }
    assert table["kind_index"] == {
        "dataclass": ["Project"],
        "exception": ["ProjectManifestError"],
        "schema constant": ["PROJECT_FACADE_API_TABLE_SCHEMA"],
        "TypedDict": ["ProjectFacadeApiRow", "ProjectFacadeApiTable"],
        "function": [
            "get_project_facade_api_selection",
            "get_project_facade_api_table",
            "render_project_facade_api_reference_markdown",
        ],
    }
    assert row_by_symbol["PROJECT_FACADE_API_TABLE_SCHEMA"]["value"] == PROJECT_FACADE_API_TABLE_SCHEMA
    assert row_by_symbol["Project"]["registry_seam"] == "project family/template registry"
    assert row_by_symbol["ProjectManifestError"]["registry_seam"] == "project manifest validation"
    assert row_by_symbol["get_project_facade_api_table"]["returns"] == "ProjectFacadeApiTable"
    assert row_by_symbol["render_project_facade_api_reference_markdown"]["returns"] == "str"
    assert reference.startswith("# Project Facade API Reference\n")
    assert "Generated from `paradev.project.get_project_facade_api_table()`." in reference
    assert "| `sdk.project` | 2 | `Project`, `ProjectManifestError` |" in reference
    assert (
        "| `project-facade-api` | 6 | `PROJECT_FACADE_API_TABLE_SCHEMA`, `ProjectFacadeApiRow`, `ProjectFacadeApiTable`, "
        "`get_project_facade_api_selection`, `get_project_facade_api_table`, `render_project_facade_api_reference_markdown` |"
    ) in reference
    assert (
        "| `Project` | `dataclass` | `project` | `sdk.project` | `projects` | `paradev.project.Project` | "
        "`Project class` |  | `project family/template registry` |"
    ) in reference
    manual = Path("docs/user-manual/project-facade-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_project_facade_api_table()["rows"][0]["symbol"] == "Project"
    table["module_index"]["api"].append("changed")
    assert get_project_facade_api_table()["module_index"]["api"] == [
        "PROJECT_FACADE_API_TABLE_SCHEMA",
        "ProjectFacadeApiRow",
        "ProjectFacadeApiTable",
        "get_project_facade_api_selection",
        "get_project_facade_api_table",
        "render_project_facade_api_reference_markdown",
    ]


def test_localization_api_table_lists_public_localization_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev.localization as localization
    from paradev.localization import (
        LOCALIZATION_API_TABLE_SCHEMA,
        LocalizationApiRow,
        LocalizationApiTable,
        get_localization_api_table,
        render_localization_api_reference_markdown,
    )

    table = get_localization_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_localization_api_reference_markdown()

    assert is_typeddict(LocalizationApiRow)
    assert is_typeddict(LocalizationApiTable)
    assert table["schema"] == LOCALIZATION_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == len(localization.__all__) == 8
    assert [row["symbol"] for row in rows] == list(localization.__all__)
    assert set(LocalizationApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(LocalizationApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "localization": ["HOI4_LANGUAGE_ALIASES", "canonical_language"],
        "api": [
            "LOCALIZATION_API_TABLE_SCHEMA",
            "LocalizationApiRow",
            "LocalizationApiTable",
            "get_localization_api_selection",
            "get_localization_api_table",
            "render_localization_api_reference_markdown",
        ],
    }
    assert table["feature_index"] == {
        "languages": ["HOI4_LANGUAGE_ALIASES", "canonical_language"],
        "localization-api": [
            "LOCALIZATION_API_TABLE_SCHEMA",
            "LocalizationApiRow",
            "LocalizationApiTable",
            "get_localization_api_selection",
            "get_localization_api_table",
            "render_localization_api_reference_markdown",
        ],
    }
    assert table["kind_index"] == {
        "dict constant": ["HOI4_LANGUAGE_ALIASES"],
        "function": [
            "canonical_language",
            "get_localization_api_selection",
            "get_localization_api_table",
            "render_localization_api_reference_markdown",
        ],
        "schema constant": ["LOCALIZATION_API_TABLE_SCHEMA"],
        "TypedDict": ["LocalizationApiRow", "LocalizationApiTable"],
    }
    assert row_by_symbol["HOI4_LANGUAGE_ALIASES"]["returns"] == "dict[24]"
    assert row_by_symbol["canonical_language"]["returns"] == "str"
    assert row_by_symbol["canonical_language"]["registry_seam"] == "HOI4 language alias normalization"
    assert row_by_symbol["LOCALIZATION_API_TABLE_SCHEMA"]["value"] == LOCALIZATION_API_TABLE_SCHEMA
    assert row_by_symbol["get_localization_api_table"]["returns"] == "LocalizationApiTable"
    assert row_by_symbol["render_localization_api_reference_markdown"]["returns"] == "str"
    assert reference.startswith("# Localization API Reference\n")
    assert "Generated from `paradev.localization.get_localization_api_table()`." in reference
    assert "| `localization` | 2 | `HOI4_LANGUAGE_ALIASES`, `canonical_language` |" in reference
    assert (
        "| `localization-api` | 6 | `LOCALIZATION_API_TABLE_SCHEMA`, `LocalizationApiRow`, `LocalizationApiTable`, "
        "`get_localization_api_selection`, `get_localization_api_table`, `render_localization_api_reference_markdown` |"
    ) in reference
    assert (
        "| `canonical_language` | `function` | `localization` | `localization` | `languages` | "
        "`paradev.localization.canonical_language` | `str` |  | `HOI4 language alias normalization` |"
    ) in reference
    manual = Path("docs/user-manual/localization-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_localization_api_table()["rows"][0]["symbol"] == "HOI4_LANGUAGE_ALIASES"
    table["module_index"]["api"].append("changed")
    assert get_localization_api_table()["module_index"]["api"] == [
        "LOCALIZATION_API_TABLE_SCHEMA",
        "LocalizationApiRow",
        "LocalizationApiTable",
        "get_localization_api_selection",
        "get_localization_api_table",
        "render_localization_api_reference_markdown",
    ]


def test_surfaces_api_table_lists_surface_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev.surfaces as surfaces
    from paradev.surfaces import (
        SURFACES_API_TABLE_SCHEMA,
        SurfacesApiRow,
        SurfacesApiTable,
        get_surfaces_api_table,
        render_surfaces_api_reference_markdown,
    )

    table = get_surfaces_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_surfaces_api_reference_markdown()

    assert is_typeddict(SurfacesApiRow)
    assert is_typeddict(SurfacesApiTable)
    assert table["schema"] == SURFACES_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == 56
    assert [row["symbol"] for row in rows] == list(surfaces.__all__)
    assert set(SurfacesApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(SurfacesApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "api_catalog": [
            "API_CATALOG_INDEX_CATALOG",
            "API_CATALOG_SCHEMA",
            "API_CATALOG_SOURCE_ROWS",
            "ApiCatalogIndexCatalogRow",
            "ApiCatalogReferenceGroupRow",
            "ApiCatalogRow",
            "ApiCatalogSourceRow",
            "ApiCatalogSummary",
            "ApiCatalogTable",
            "get_api_catalog_group_reference_ids",
            "get_api_catalog_reference_group",
            "get_api_catalog_reference_groups",
            "get_api_catalog_index_catalog",
            "get_api_catalog_reference",
            "get_api_catalog_reference_ids",
            "get_api_catalog_selection",
            "get_api_catalog_summary",
            "get_api_catalog_table",
            "render_api_catalog_reference_markdown",
        ],
        "api": [
            "SURFACES_API_TABLE_SCHEMA",
            "SurfacesApiRow",
            "SurfacesApiTable",
            "get_surfaces_api_selection",
            "get_surfaces_api_table",
            "render_surfaces_api_reference_markdown",
        ],
        "surface_contracts": [
            "SURFACE_CONTRACT_IDS",
            "SURFACE_CONTRACT_INDEX_CATALOG",
            "SURFACE_CONTRACT_SUMMARY_SCHEMA",
            "SurfaceContractIdentifier",
            "SurfaceContractIndexCatalogRow",
            "SurfaceContractPayload",
            "SurfaceContractSummary",
            "SurfaceContractSummaryRow",
            "get_surface_contract",
            "get_surface_contract_ids",
            "get_surface_contract_index_catalog",
            "get_surface_contract_selection",
            "get_surface_contract_summary",
            "get_surface_contract_summary_row",
            "get_surface_contract_status_ids",
            "get_surface_contracts",
            "render_surface_contract_reference_markdown",
        ],
        "bundle": ["get_bundle_contract"],
        "cli": [
            "get_cli_api_table",
            "get_cli_contract",
            "render_cli_api_reference_markdown",
        ],
        "lsp": ["get_lsp_contract"],
        "mcp": [
            "get_mcp_api_selection",
            "get_mcp_api_table",
            "get_mcp_contract",
            "render_mcp_api_reference_markdown",
        ],
        "rest": [
            "get_openapi_seed",
            "get_rest_api_selection",
            "get_rest_api_table",
            "render_rest_api_reference_markdown",
        ],
        "vscode": ["get_vscode_contract"],
    }
    assert table["feature_index"]["api-catalog"] == [
        "API_CATALOG_INDEX_CATALOG",
        "API_CATALOG_SCHEMA",
        "API_CATALOG_SOURCE_ROWS",
        "ApiCatalogIndexCatalogRow",
        "ApiCatalogReferenceGroupRow",
        "ApiCatalogRow",
        "ApiCatalogSourceRow",
        "ApiCatalogSummary",
        "ApiCatalogTable",
        "get_api_catalog_group_reference_ids",
        "get_api_catalog_reference_group",
        "get_api_catalog_reference_groups",
        "get_api_catalog_index_catalog",
        "get_api_catalog_reference",
        "get_api_catalog_reference_ids",
        "get_api_catalog_selection",
        "get_api_catalog_summary",
        "get_api_catalog_table",
        "render_api_catalog_reference_markdown",
    ]
    assert table["feature_index"]["surfaces-api"] == [
        "SURFACES_API_TABLE_SCHEMA",
        "SurfacesApiRow",
        "SurfacesApiTable",
        "get_surfaces_api_selection",
        "get_surfaces_api_table",
        "render_surfaces_api_reference_markdown",
    ]
    assert table["feature_index"]["surface-contracts"] == table["module_index"]["surface_contracts"]
    assert table["feature_index"]["openapi"] == ["get_openapi_seed"]
    assert table["feature_index"]["rest"] == [
        "get_rest_api_selection",
        "get_rest_api_table",
        "render_rest_api_reference_markdown",
    ]
    assert table["kind_index"]["schema constant"] == [
        "API_CATALOG_SCHEMA",
        "SURFACES_API_TABLE_SCHEMA",
        "SURFACE_CONTRACT_SUMMARY_SCHEMA",
    ]
    assert table["kind_index"]["tuple constant"] == [
        "API_CATALOG_INDEX_CATALOG",
        "API_CATALOG_SOURCE_ROWS",
        "SURFACE_CONTRACT_IDS",
        "SURFACE_CONTRACT_INDEX_CATALOG",
    ]
    assert table["kind_index"]["TypedDict"] == [
        "ApiCatalogIndexCatalogRow",
        "ApiCatalogReferenceGroupRow",
        "ApiCatalogRow",
        "ApiCatalogSourceRow",
        "ApiCatalogSummary",
        "ApiCatalogTable",
        "SurfacesApiRow",
        "SurfacesApiTable",
        "SurfaceContractIndexCatalogRow",
        "SurfaceContractSummary",
        "SurfaceContractSummaryRow",
    ]
    assert table["kind_index"]["type alias"] == [
        "SurfaceContractIdentifier",
        "SurfaceContractPayload",
    ]
    assert len(table["kind_index"]["function"]) == 36
    assert row_by_symbol["API_CATALOG_INDEX_CATALOG"]["returns"] == "tuple[11]"
    assert row_by_symbol["API_CATALOG_SOURCE_ROWS"]["returns"] == "tuple[29]"
    assert row_by_symbol["API_CATALOG_SOURCE_ROWS"]["value"] == "29 items"
    assert row_by_symbol["SURFACES_API_TABLE_SCHEMA"]["value"] == SURFACES_API_TABLE_SCHEMA
    assert row_by_symbol["get_surfaces_api_table"]["returns"] == "SurfacesApiTable"
    assert row_by_symbol["get_surfaces_api_table"]["registry_seam"] == "surface facade API table"
    assert row_by_symbol["get_api_catalog_selection"]["returns"] == "ApiCatalogTable | ApiCatalogRow | list[str]"
    assert row_by_symbol["get_api_catalog_table"]["registry_seam"] == "API reference catalog"
    assert row_by_symbol["get_surface_contract_selection"]["returns"] == "SurfaceContractSummary | SurfaceContractPayload | list[SurfaceContractIdentifier]"
    assert row_by_symbol["get_surface_contract_summary"]["registry_seam"] == "surface contract catalog"
    assert row_by_symbol["get_rest_api_table"]["registry_seam"] == "REST/OpenAPI route contract"
    assert row_by_symbol["get_mcp_api_table"]["surface"] == "mcp"
    assert row_by_symbol["get_openapi_seed"]["feature"] == "openapi"
    assert reference.startswith("# Surfaces API Reference\n")
    assert "Generated from `paradev.surfaces.get_surfaces_api_table()`." in reference
    assert (
        "| `api` | 6 | `SURFACES_API_TABLE_SCHEMA`, `SurfacesApiRow`, `SurfacesApiTable`, "
        "`get_surfaces_api_selection`, `get_surfaces_api_table`, `render_surfaces_api_reference_markdown` |"
    ) in reference
    assert ("| `api_catalog` | 19 | `API_CATALOG_INDEX_CATALOG`, `API_CATALOG_SCHEMA`, `API_CATALOG_SOURCE_ROWS`, " "`ApiCatalogIndexCatalogRow`,") in reference
    assert ("| `surface_contracts` | 17 | `SURFACE_CONTRACT_IDS`, `SURFACE_CONTRACT_INDEX_CATALOG`, " "`SURFACE_CONTRACT_SUMMARY_SCHEMA`,") in reference
    assert "| `rest` | 4 | `get_openapi_seed`, `get_rest_api_selection`, `get_rest_api_table`, `render_rest_api_reference_markdown` |" in reference
    assert (
        "| `get_surfaces_api_table` | `function` | `surface` | `api` | `surfaces-api` | "
        "`paradev.surfaces.get_surfaces_api_table` | `SurfacesApiTable` |  | `surface facade API table` |"
    ) in reference
    manual = Path("docs/user-manual/surfaces-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_surfaces_api_table()["rows"][0]["symbol"] == "API_CATALOG_INDEX_CATALOG"
    table["module_index"]["api"].append("changed")
    assert get_surfaces_api_table()["module_index"]["api"] == [
        "SURFACES_API_TABLE_SCHEMA",
        "SurfacesApiRow",
        "SurfacesApiTable",
        "get_surfaces_api_selection",
        "get_surfaces_api_table",
        "render_surfaces_api_reference_markdown",
    ]


def test_api_catalog_lists_generated_references() -> None:
    from importlib import import_module
    from typing_extensions import is_typeddict

    import paradev.surfaces as surfaces
    from paradev.surfaces import (
        API_CATALOG_INDEX_CATALOG,
        API_CATALOG_SCHEMA,
        API_CATALOG_SOURCE_ROWS,
        ApiCatalogIndexCatalogRow,
        ApiCatalogReferenceGroupRow,
        ApiCatalogRow,
        ApiCatalogSourceRow,
        ApiCatalogSummary,
        ApiCatalogTable,
        get_api_catalog_index_catalog,
        get_api_catalog_reference_group,
        get_api_catalog_reference_groups,
        get_api_catalog_reference,
        get_api_catalog_reference_ids,
        get_api_catalog_selection,
        get_api_catalog_summary,
        get_api_catalog_table,
        render_api_catalog_reference_markdown,
    )

    table = get_api_catalog_table()
    rows = table["rows"]
    rows_by_id = {row["id"]: row for row in rows}
    reference = render_api_catalog_reference_markdown()

    assert is_typeddict(ApiCatalogRow)
    assert is_typeddict(ApiCatalogIndexCatalogRow)
    assert is_typeddict(ApiCatalogReferenceGroupRow)
    assert is_typeddict(ApiCatalogSourceRow)
    assert is_typeddict(ApiCatalogSummary)
    assert is_typeddict(ApiCatalogTable)
    assert "get_rest_api_table" in surfaces.__all__
    assert "render_rest_api_reference_markdown" in surfaces.__all__
    assert "get_mcp_api_table" in surfaces.__all__
    assert "render_mcp_api_reference_markdown" in surfaces.__all__
    assert "get_surfaces_api_table" in surfaces.__all__
    assert "render_surfaces_api_reference_markdown" in surfaces.__all__
    assert table["schema"] == API_CATALOG_SCHEMA
    assert table["row_count"] == len(rows) == len(API_CATALOG_SOURCE_ROWS) == 29
    assert len({source["id"] for source in API_CATALOG_SOURCE_ROWS}) == len(API_CATALOG_SOURCE_ROWS)
    assert len({source["doc_page"] for source in API_CATALOG_SOURCE_ROWS}) == len(API_CATALOG_SOURCE_ROWS)
    assert len({source["markdown_cli_command"] for source in API_CATALOG_SOURCE_ROWS}) == len(API_CATALOG_SOURCE_ROWS)
    assert all(
        isinstance(source[field], str) and source[field]
        for source in API_CATALOG_SOURCE_ROWS
        for field in (
            "id",
            "title",
            "kind",
            "layer",
            "feature",
            "owner_module",
            "table_helper",
            "markdown_helper",
            "cli_command",
            "markdown_cli_command",
            "doc_page",
        )
    )
    assert all(source["surfaces"] for source in API_CATALOG_SOURCE_ROWS)
    assert all(len(source["surfaces"]) == len(set(source["surfaces"])) for source in API_CATALOG_SOURCE_ROWS)
    assert all(surface for source in API_CATALOG_SOURCE_ROWS for surface in source["surfaces"])
    assert [row["id"] for row in rows] == [
        "api-catalog",
        "sdk-api",
        "package-api",
        "config-api",
        "gui-api",
        "desktop-api",
        "games-api",
        "surfaces-api",
        "project-api",
        "templates-api",
        "copy-roots-api",
        "project-facade-api",
        "localization-api",
        "build-api",
        "frontend-api",
        "sdk-cli-reference",
        "project-inspection-reference",
        "architecture-api",
        "pdx-api",
        "pdx-core-api",
        "lsp-api",
        "lsp-server-api",
        "catalog-api",
        "hb-api",
        "rest-api",
        "rest-facade-api",
        "mcp-api",
        "cli-api",
        "surface-contract-reference",
    ]
    for source in API_CATALOG_SOURCE_ROWS:
        module = import_module(source["owner_module"])
        assert callable(getattr(module, source["table_helper"]))
        assert callable(getattr(module, source["markdown_helper"]))
        if source["selector_helper"]:
            assert callable(getattr(module, source["selector_helper"]))
    assert set(ApiCatalogSourceRow.__annotations__) == {
        "id",
        "title",
        "kind",
        "layer",
        "feature",
        "owner_module",
        "table_helper",
        "selector_helper",
        "markdown_helper",
        "cli_command",
        "markdown_cli_command",
        "doc_page",
        "surfaces",
    }
    assert set(ApiCatalogIndexCatalogRow.__annotations__) == {
        "id",
        "table_path",
        "python_helper",
        "usage",
    }
    assert set(ApiCatalogReferenceGroupRow.__annotations__) == {
        "id",
        "title",
        "reference_count",
        "kinds",
        "reference_ids",
        "usage",
    }
    assert set(ApiCatalogRow.__annotations__) == {
        *ApiCatalogSourceRow.__annotations__,
        "schema",
        "row_count",
        "index_names",
        "test_anchor",
    }
    assert set(ApiCatalogSummary.__annotations__) == {
        "reference_count",
        "layer_count",
        "feature_count",
        "kind_count",
        "reference_group_count",
        "index_count",
        "owner_module_count",
        "surface_count",
        "cli_command_count",
        "selector_helper_count",
        "doc_page_count",
    }
    assert set(ApiCatalogTable.__annotations__) == {
        "schema",
        "row_count",
        "summary",
        "layer_index",
        "feature_index",
        "kind_index",
        "owner_module_index",
        "surface_index",
        "cli_command_index",
        "selector_helper_index",
        "doc_page_index",
        "group_index",
        "index_catalog",
        "reference_groups",
        "rows",
    }
    assert get_api_catalog_index_catalog() == list(API_CATALOG_INDEX_CATALOG)
    assert table["index_catalog"] == get_api_catalog_index_catalog()
    assert get_api_catalog_index_catalog()[0] == {
        "id": "id",
        "table_path": 'table["rows"][*]["id"]',
        "python_helper": "get_api_catalog_reference(reference_id)",
        "usage": "Reference id to one aggregate API catalog row.",
    }
    assert get_api_catalog_index_catalog()[4] == {
        "id": "group",
        "table_path": 'table["group_index"][group]',
        "python_helper": "get_api_catalog_group_reference_ids(group)",
        "usage": "Reader-oriented reference group to generated reference ids.",
    }
    assert get_api_catalog_index_catalog()[5] == {
        "id": "reference_group",
        "table_path": 'table["reference_groups"][*]["id"]',
        "python_helper": "get_api_catalog_reference_group(group)",
        "usage": "Reference group id to one reader-oriented reference group row.",
    }
    assert get_api_catalog_index_catalog()[6] == {
        "id": "owner_module",
        "table_path": 'table["owner_module_index"][owner_module]',
        "python_helper": "get_api_catalog_reference_ids('owner_module', owner_module)",
        "usage": "Owner module import path to generated reference ids.",
    }
    assert get_api_catalog_index_catalog()[9] == {
        "id": "selector_helper",
        "table_path": 'table["selector_helper_index"][selector_helper]',
        "python_helper": "get_api_catalog_reference_ids('selector_helper', selector_helper)",
        "usage": "Shared selector helper to generated reference ids.",
    }
    assert get_api_catalog_selection() == table
    assert get_api_catalog_selection(reference_id="frontend-api") == rows_by_id["frontend-api"]
    assert get_api_catalog_selection(index_name="surface", key="rest") == table["surface_index"]["rest"]
    assert get_api_catalog_selection(index_name="selector_helper", key="get_frontend_api_selection") == [
        "frontend-api",
        "sdk-cli-reference",
    ]
    assert get_api_catalog_reference("frontend-api") == rows_by_id["frontend-api"]
    assert get_api_catalog_summary() == table["summary"]
    assert table["summary"]["reference_count"] == 29
    assert get_api_catalog_reference_groups() == table["reference_groups"]
    assert get_api_catalog_reference_group("facades")["reference_ids"] == table["group_index"]["facades"]
    assert get_api_catalog_reference_ids("surface", "rest") == table["surface_index"]["rest"]
    assert get_api_catalog_reference_ids("selector_helper", "get_surface_contract_selection") == ["surface-contract-reference"]
    assert get_api_catalog_reference_ids("owner_module", "paradev.sdk") == table["owner_module_index"]["paradev.sdk"]
    assert get_api_catalog_reference_ids("feature", "overall") == ["api-catalog"]
    assert table["layer_index"] == {
        "surface": ["api-catalog", "surfaces-api", "surface-contract-reference"],
        "sdk": [
            "sdk-api",
            "project-api",
            "templates-api",
            "copy-roots-api",
            "frontend-api",
            "sdk-cli-reference",
            "project-inspection-reference",
            "architecture-api",
            "pdx-api",
            "lsp-api",
        ],
        "package": ["package-api"],
        "config": ["config-api"],
        "gui": ["gui-api"],
        "desktop": ["desktop-api"],
        "games": ["games-api"],
        "project": ["project-facade-api"],
        "localization": ["localization-api"],
        "build": ["build-api"],
        "pdx": ["pdx-core-api"],
        "lsp": ["lsp-server-api"],
        "hb": ["catalog-api", "hb-api"],
        "rest": ["rest-api", "rest-facade-api"],
        "mcp": ["mcp-api"],
        "cli": ["cli-api"],
    }
    assert table["feature_index"]["overall"] == ["api-catalog"]
    assert table["feature_index"]["facade"] == ["sdk-api", "package-api", "hb-api"]
    assert table["feature_index"]["config"] == ["config-api"]
    assert table["feature_index"]["launcher"] == ["gui-api"]
    assert table["feature_index"]["state"] == ["desktop-api"]
    assert table["feature_index"]["profiles"] == ["games-api"]
    assert table["feature_index"]["surfaces"] == ["surfaces-api"]
    assert table["feature_index"]["authoring"] == ["templates-api"]
    assert table["feature_index"]["copy-roots"] == ["copy-roots-api"]
    assert table["feature_index"]["compiler"] == ["build-api"]
    assert table["feature_index"]["pdx-core"] == ["pdx-core-api"]
    assert table["feature_index"]["lsp-server"] == ["lsp-server-api"]
    assert table["feature_index"]["project-facade"] == ["project-facade-api"]
    assert table["feature_index"]["localization"] == ["localization-api"]
    assert table["feature_index"]["rest-facade"] == ["rest-facade-api"]
    assert table["feature_index"]["adapters"] == ["surface-contract-reference"]
    assert table["kind_index"]["api-table"] == [
        "architecture-api",
        "pdx-api",
        "lsp-api",
        "catalog-api",
    ]
    assert table["kind_index"]["module-table"] == ["templates-api", "copy-roots-api"]
    assert table["kind_index"]["facade-table"] == [
        "sdk-api",
        "package-api",
        "config-api",
        "gui-api",
        "desktop-api",
        "games-api",
        "surfaces-api",
        "project-facade-api",
        "localization-api",
        "build-api",
        "pdx-core-api",
        "lsp-server-api",
        "hb-api",
        "rest-facade-api",
    ]
    assert table["owner_module_index"] == {
        "paradev.surfaces": [
            "api-catalog",
            "surfaces-api",
            "surface-contract-reference",
        ],
        "paradev.sdk": [
            "sdk-api",
            "project-api",
            "frontend-api",
            "sdk-cli-reference",
            "project-inspection-reference",
            "architecture-api",
            "pdx-api",
            "lsp-api",
        ],
        "paradev.sdk.templates": ["templates-api"],
        "paradev.sdk.copy_roots": ["copy-roots-api"],
        "paradev": ["package-api"],
        "paradev.config": ["config-api"],
        "paradev.gui": ["gui-api"],
        "paradev.desktop": ["desktop-api"],
        "paradev.games": ["games-api"],
        "paradev.project": ["project-facade-api"],
        "paradev.localization": ["localization-api"],
        "paradev.build": ["build-api"],
        "paradev.pdx": ["pdx-core-api"],
        "paradev.lsp": ["lsp-server-api"],
        "paradev.hb": ["catalog-api", "hb-api"],
        "paradev.surfaces.rest": ["rest-api"],
        "paradev.api": ["rest-facade-api"],
        "paradev.surfaces.mcp": ["mcp-api"],
        "paradev.surfaces.cli": ["cli-api"],
    }
    assert table["surface_index"]["sdk"] == [
        "api-catalog",
        "sdk-api",
        "package-api",
        "config-api",
        "gui-api",
        "desktop-api",
        "games-api",
        "surfaces-api",
        "project-api",
        "templates-api",
        "copy-roots-api",
        "project-facade-api",
        "localization-api",
        "build-api",
        "frontend-api",
        "sdk-cli-reference",
        "project-inspection-reference",
        "architecture-api",
        "pdx-api",
        "pdx-core-api",
        "lsp-api",
        "lsp-server-api",
        "catalog-api",
        "hb-api",
        "rest-facade-api",
    ]
    assert table["surface_index"]["docs"] == [
        "api-catalog",
        "sdk-api",
        "package-api",
        "config-api",
        "gui-api",
        "desktop-api",
        "games-api",
        "surfaces-api",
        "project-api",
        "templates-api",
        "copy-roots-api",
        "project-facade-api",
        "localization-api",
        "build-api",
        "frontend-api",
        "sdk-cli-reference",
        "project-inspection-reference",
        "architecture-api",
        "pdx-api",
        "pdx-core-api",
        "lsp-api",
        "lsp-server-api",
        "catalog-api",
        "hb-api",
        "rest-api",
        "rest-facade-api",
        "mcp-api",
        "cli-api",
        "surface-contract-reference",
    ]
    assert table["surface_index"]["rest"] == [
        "api-catalog",
        "surfaces-api",
        "frontend-api",
        "project-inspection-reference",
        "architecture-api",
        "pdx-api",
        "lsp-api",
        "catalog-api",
        "rest-api",
        "rest-facade-api",
        "cli-api",
        "surface-contract-reference",
    ]
    assert table["surface_index"]["mcp"] == [
        "api-catalog",
        "surfaces-api",
        "frontend-api",
        "project-inspection-reference",
        "architecture-api",
        "pdx-api",
        "lsp-api",
        "catalog-api",
        "mcp-api",
        "cli-api",
        "surface-contract-reference",
    ]
    assert table["surface_index"]["lsp"] == [
        "surfaces-api",
        "frontend-api",
        "lsp-api",
        "lsp-server-api",
        "catalog-api",
        "surface-contract-reference",
    ]
    assert table["surface_index"]["frontend"] == [
        "project-api",
        "templates-api",
        "frontend-api",
        "project-inspection-reference",
        "rest-api",
        "mcp-api",
        "cli-api",
    ]
    assert table["surface_index"]["typescript"] == ["frontend-api"]
    assert table["surface_index"]["desktop"] == ["gui-api", "desktop-api"]
    assert table["surface_index"]["vscode"] == ["surface-contract-reference"]
    assert table["surface_index"]["bundle"] == ["surface-contract-reference"]
    assert table["cli_command_index"]["frontend-api"] == [
        "frontend-api",
        "sdk-cli-reference",
    ]
    assert table["cli_command_index"]["surfaces-api"] == ["surfaces-api"]
    assert table["cli_command_index"]["architecture --surface-contracts"] == ["surface-contract-reference"]
    selector_helper_index = table["selector_helper_index"]
    assert selector_helper_index["get_api_catalog_selection"] == ["api-catalog"]
    assert selector_helper_index["get_frontend_api_selection"] == [
        "frontend-api",
        "sdk-cli-reference",
    ]
    assert selector_helper_index["get_architecture_api_selection"] == ["architecture-api"]
    assert selector_helper_index["get_project_inspection_selection"] == ["project-inspection-reference"]
    assert selector_helper_index["get_mcp_api_selection"] == ["mcp-api"]
    assert selector_helper_index["get_cli_api_selection"] == ["cli-api"]
    assert selector_helper_index["get_surface_contract_selection"] == ["surface-contract-reference"]
    assert table["doc_page_index"]["docs/user-manual/api-catalog-reference.md"] == ["api-catalog"]
    assert rows_by_id["api-catalog"]["schema"] == API_CATALOG_SCHEMA
    assert rows_by_id["api-catalog"]["row_count"] == 29
    assert rows_by_id["api-catalog"]["index_names"] == [
        "cli_command_index",
        "doc_page_index",
        "feature_index",
        "group_index",
        "kind_index",
        "layer_index",
        "owner_module_index",
        "selector_helper_index",
        "surface_index",
    ]
    assert rows_by_id["sdk-api"]["schema"] == "paradev.sdk.api-table.v1"
    assert rows_by_id["sdk-api"]["row_count"] == 138
    assert rows_by_id["package-api"]["schema"] == "paradev.package.api-table.v1"
    assert rows_by_id["package-api"]["row_count"] == 15
    assert rows_by_id["package-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["config-api"]["schema"] == "paradev.config.api-table.v1"
    assert rows_by_id["config-api"]["row_count"] == 15
    assert rows_by_id["config-api"]["owner_module"] == "paradev.config"
    assert rows_by_id["config-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["gui-api"]["schema"] == "paradev.gui.api-table.v1"
    assert rows_by_id["gui-api"]["row_count"] == 8
    assert rows_by_id["gui-api"]["owner_module"] == "paradev.gui"
    assert rows_by_id["gui-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["desktop-api"]["schema"] == "paradev.desktop.api-table.v1"
    assert rows_by_id["desktop-api"]["row_count"] == 57
    assert rows_by_id["desktop-api"]["owner_module"] == "paradev.desktop"
    assert rows_by_id["desktop-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["games-api"]["schema"] == "paradev.games.api-table.v1"
    assert rows_by_id["games-api"]["row_count"] == 8
    assert rows_by_id["games-api"]["owner_module"] == "paradev.games"
    assert rows_by_id["games-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["surfaces-api"]["schema"] == "paradev.surfaces.api-table.v1"
    assert rows_by_id["surfaces-api"]["row_count"] == 56
    assert rows_by_id["surfaces-api"]["selector_helper"] == "get_surfaces_api_selection"
    assert rows_by_id["surfaces-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["project-api"]["row_count"] == 81
    assert rows_by_id["templates-api"]["schema"] == "paradev.sdk.templates.api-table.v1"
    assert rows_by_id["templates-api"]["row_count"] == 18
    assert rows_by_id["templates-api"]["owner_module"] == "paradev.sdk.templates"
    assert rows_by_id["templates-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["copy-roots-api"]["schema"] == "paradev.sdk.copy_roots.api-table.v1"
    assert rows_by_id["copy-roots-api"]["row_count"] == 12
    assert rows_by_id["copy-roots-api"]["owner_module"] == "paradev.sdk.copy_roots"
    assert rows_by_id["copy-roots-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["project-facade-api"]["schema"] == "paradev.project.facade-api-table.v1"
    assert rows_by_id["project-facade-api"]["row_count"] == 8
    assert rows_by_id["project-facade-api"]["owner_module"] == "paradev.project"
    assert rows_by_id["project-facade-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["localization-api"]["schema"] == "paradev.localization.api-table.v1"
    assert rows_by_id["localization-api"]["row_count"] == 8
    assert rows_by_id["localization-api"]["owner_module"] == "paradev.localization"
    assert rows_by_id["localization-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["build-api"]["row_count"] == 133
    assert rows_by_id["architecture-api"]["row_count"] == 17
    assert rows_by_id["architecture-api"]["selector_helper"] == "get_architecture_api_selection"
    assert rows_by_id["pdx-core-api"]["schema"] == "paradev.pdx.core-api-table.v1"
    assert rows_by_id["pdx-core-api"]["row_count"] == 23
    assert rows_by_id["pdx-core-api"]["owner_module"] == "paradev.pdx"
    assert rows_by_id["pdx-core-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["lsp-server-api"]["schema"] == "paradev.lsp.server-api-table.v1"
    assert rows_by_id["lsp-server-api"]["row_count"] == 11
    assert rows_by_id["lsp-server-api"]["owner_module"] == "paradev.lsp"
    assert rows_by_id["lsp-server-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["hb-api"]["schema"] == "paradev.hb.api-table.v1"
    assert rows_by_id["hb-api"]["row_count"] == 27
    assert rows_by_id["hb-api"]["owner_module"] == "paradev.hb"
    assert rows_by_id["hb-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["catalog-api"]["row_count"] == 37
    assert rows_by_id["frontend-api"]["row_count"] == 98
    assert rows_by_id["frontend-api"]["table_helper"] == "get_frontend_api_contract"
    assert rows_by_id["frontend-api"]["selector_helper"] == "get_frontend_api_selection"
    assert rows_by_id["sdk-cli-reference"]["row_count"] == 98
    assert rows_by_id["sdk-cli-reference"]["selector_helper"] == "get_frontend_api_selection"
    assert rows_by_id["project-inspection-reference"]["row_count"] == 19
    assert rows_by_id["project-inspection-reference"]["selector_helper"] == "get_project_inspection_selection"
    assert rows_by_id["lsp-api"]["row_count"] == 42
    assert rows_by_id["lsp-api"]["surfaces"] == [
        "sdk",
        "cli",
        "rest",
        "mcp",
        "lsp",
        "docs",
    ]
    assert rows_by_id["rest-api"]["row_count"] == 84
    assert rows_by_id["rest-api"]["index_names"] == [
        "feature_index",
        "frontend_operation_index",
        "method_index",
    ]
    assert rows_by_id["rest-facade-api"]["schema"] == "paradev.rest.facade-api-table.v1"
    assert rows_by_id["rest-facade-api"]["row_count"] == 13
    assert rows_by_id["rest-facade-api"]["owner_module"] == "paradev.api"
    assert rows_by_id["rest-facade-api"]["index_names"] == [
        "feature_index",
        "kind_index",
        "module_index",
    ]
    assert rows_by_id["mcp-api"]["row_count"] == 51
    assert rows_by_id["mcp-api"]["index_names"] == [
        "feature_index",
        "frontend_operation_index",
        "mode_index",
    ]
    assert rows_by_id["mcp-api"]["selector_helper"] == "get_mcp_api_selection"
    assert rows_by_id["surface-contract-reference"]["index_names"] == [
        "status_index",
        "index",
    ]
    assert rows_by_id["surface-contract-reference"]["selector_helper"] == "get_surface_contract_selection"
    assert rows_by_id["api-catalog"]["selector_helper"] == "get_api_catalog_selection"
    assert rows_by_id["cli-api"]["row_count"] == 208
    assert rows_by_id["cli-api"]["selector_helper"] == "get_cli_api_selection"
    assert rows_by_id["cli-api"]["markdown_cli_command"] == "cli-api --markdown"
    assert rows_by_id["surfaces-api"]["surfaces"] == [
        "sdk",
        "cli",
        "rest",
        "mcp",
        "lsp",
        "docs",
    ]
    assert rows_by_id["surface-contract-reference"]["surfaces"] == [
        "cli",
        "rest",
        "mcp",
        "lsp",
        "vscode",
        "bundle",
        "docs",
    ]
    assert reference.startswith("# API Catalog Reference\n")
    assert "Generated from `paradev.surfaces.get_api_catalog_table()`." in reference
    assert "## Index Catalog / Index 目录" in reference
    assert (
        "| `surface` | `table[\"surface_index\"][surface]` | `get_api_catalog_reference_ids('surface', surface)` | " "Surface id to generated reference ids. |"
    ) in reference
    assert (
        '| `selector_helper` | `table["selector_helper_index"][selector_helper]` | '
        "`get_api_catalog_reference_ids('selector_helper', selector_helper)` | Shared selector helper to generated reference ids. |"
    ) in reference
    assert (
        "| `sdk` | 10 | `sdk-api`, `project-api`, `templates-api`, `copy-roots-api`, `frontend-api`, `sdk-cli-reference`, `project-inspection-reference`, `architecture-api`, `pdx-api`, `lsp-api` |"
        in reference
    )
    assert "| `lsp` | 1 | `lsp-server-api` |" in reference
    assert "| `pdx` | 1 | `pdx-core-api` |" in reference
    assert "| `package` | 1 | `package-api` |" in reference
    assert "| `config` | 1 | `config-api` |" in reference
    assert "| `gui` | 1 | `gui-api` |" in reference
    assert "| `desktop` | 1 | `desktop-api` |" in reference
    assert "| `games` | 1 | `games-api` |" in reference
    assert "| `project` | 1 | `project-facade-api` |" in reference
    assert "| `authoring` | 1 | `templates-api` |" in reference
    assert "| `copy-roots` | 1 | `copy-roots-api` |" in reference
    assert "| `module-table` | 2 | `templates-api`, `copy-roots-api` |" in reference
    assert (
        "| `facade-table` | 14 | `sdk-api`, `package-api`, `config-api`, `gui-api`, `desktop-api`, `games-api`, `surfaces-api`, `project-facade-api`, `localization-api`, `build-api`, `pdx-core-api`, "
        "`lsp-server-api`, `hb-api`, `rest-facade-api` |"
    ) in reference
    assert "| `paradev.surfaces` | 3 | `api-catalog`, `surfaces-api`, `surface-contract-reference` |" in reference
    assert "| `paradev.config` | 1 | `config-api` |" in reference
    assert "| `paradev.gui` | 1 | `gui-api` |" in reference
    assert "| `paradev.desktop` | 1 | `desktop-api` |" in reference
    assert "| `paradev.games` | 1 | `games-api` |" in reference
    assert "| `paradev.sdk.templates` | 1 | `templates-api` |" in reference
    assert "| `paradev.sdk.copy_roots` | 1 | `copy-roots-api` |" in reference
    assert "| `paradev.project` | 1 | `project-facade-api` |" in reference
    assert "| `paradev.localization` | 1 | `localization-api` |" in reference
    assert "| `paradev.pdx` | 1 | `pdx-core-api` |" in reference
    assert "| `paradev.lsp` | 1 | `lsp-server-api` |" in reference
    assert "| `paradev.hb` | 2 | `catalog-api`, `hb-api` |" in reference
    assert "| `paradev.api` | 1 | `rest-facade-api` |" in reference
    assert "| `get_api_catalog_selection` | 1 | `api-catalog` |" in reference
    assert "| `get_frontend_api_selection` | 2 | `frontend-api`, `sdk-cli-reference` |" in reference
    assert "| `get_architecture_api_selection` | 1 | `architecture-api` |" in reference
    assert "| `get_mcp_api_selection` | 1 | `mcp-api` |" in reference
    assert "| `get_cli_api_selection` | 1 | `cli-api` |" in reference
    assert "| `get_surface_contract_selection` | 1 | `surface-contract-reference` |" in reference
    assert (
        "| `sdk` | 25 | `api-catalog`, `sdk-api`, `package-api`, `config-api`, `gui-api`, `desktop-api`, `games-api`, `surfaces-api`, `project-api`, `templates-api`, `copy-roots-api`, `project-facade-api`, `localization-api`, "
        "`build-api`, `frontend-api`, `sdk-cli-reference`, `project-inspection-reference`, `architecture-api`, `pdx-api`, "
        "`pdx-core-api`, `lsp-api`, `lsp-server-api`, `catalog-api`, `hb-api`, `rest-facade-api` |"
    ) in reference
    assert (
        "| `mcp` | 11 | `api-catalog`, `surfaces-api`, `frontend-api`, `project-inspection-reference`, `architecture-api`, `pdx-api`, `lsp-api`," in reference
    )
    assert "| `docs` | 29 | `api-catalog`, `sdk-api`, `package-api`, `config-api`, `gui-api`, `desktop-api`, `games-api`, `surfaces-api`," in reference
    assert "| `desktop` | 2 | `gui-api`, `desktop-api` |" in reference
    assert "| `frontend-api` | 2 | `frontend-api`, `sdk-cli-reference` |" in reference
    assert (
        "| `frontend-api` | Frontend API Reference | `operation-contract` | `sdk` | `frontend` | `paradev.sdk.frontend-api.v1` | 98 | "
        "`get_frontend_api_contract` | `get_frontend_api_selection` | `render_frontend_api_reference_markdown` | `frontend-api` | `frontend-api --markdown` |"
    ) in reference
    assert (
        "| `templates-api` | Authoring Templates API Reference | `module-table` | `sdk` | `authoring` | "
        "`paradev.sdk.templates.api-table.v1` | 18 | `get_templates_api_table` | "
        "`get_templates_api_selection` | `render_templates_api_reference_markdown` | `templates-api` | `templates-api --markdown` |"
    ) in reference
    assert (
        "| `copy-roots-api` | Copy Roots API Reference | `module-table` | `sdk` | `copy-roots` | "
        "`paradev.sdk.copy_roots.api-table.v1` | 12 | `get_copy_roots_api_table` | "
        "`get_copy_roots_api_selection` | `render_copy_roots_api_reference_markdown` | `copy-roots-api` | `copy-roots-api --markdown` |"
    ) in reference
    assert (
        "| `package-api` | Package API Reference | `facade-table` | `package` | `facade` | `paradev.package.api-table.v1` | 15 | "
        "`get_package_api_table` | `get_package_api_selection` | `render_package_api_reference_markdown` | `package-api` | `package-api --markdown` |"
    ) in reference
    assert (
        "| `config-api` | Config API Reference | `facade-table` | `config` | `config` | `paradev.config.api-table.v1` | 15 | "
        "`get_config_api_table` | `get_config_api_selection` | `render_config_api_reference_markdown` | `config-api` | `config-api --markdown` |"
    ) in reference
    assert (
        "| `gui-api` | GUI API Reference | `facade-table` | `gui` | `launcher` | `paradev.gui.api-table.v1` | 8 | "
        "`get_gui_api_table` | `get_gui_api_selection` | `render_gui_api_reference_markdown` | `gui-api` | `gui-api --markdown` |"
    ) in reference
    assert (
        "| `desktop-api` | Desktop API Reference | `facade-table` | `desktop` | `state` | `paradev.desktop.api-table.v1` | 57 | "
        "`get_desktop_api_table` | `get_desktop_api_selection` | `render_desktop_api_reference_markdown` | `desktop-api` | `desktop-api --markdown` |"
    ) in reference
    assert (
        "| `games-api` | Games API Reference | `facade-table` | `games` | `profiles` | `paradev.games.api-table.v1` | 8 | "
        "`get_games_api_table` | `get_games_api_selection` | `render_games_api_reference_markdown` | `games-api` | `games-api --markdown` |"
    ) in reference
    assert (
        "| `project-facade-api` | Project Facade API Reference | `facade-table` | `project` | `project-facade` | "
        "`paradev.project.facade-api-table.v1` | 8 | `get_project_facade_api_table` | "
        "`get_project_facade_api_selection` | `render_project_facade_api_reference_markdown` | `project-facade-api` | `project-facade-api --markdown` |"
    ) in reference
    assert (
        "| `localization-api` | Localization API Reference | `facade-table` | `localization` | `localization` | "
        "`paradev.localization.api-table.v1` | 8 | `get_localization_api_table` | "
        "`get_localization_api_selection` | `render_localization_api_reference_markdown` | `localization-api` | `localization-api --markdown` |"
    ) in reference
    assert (
        "| `surfaces-api` | Surfaces API Reference | `facade-table` | `surface` | `surfaces` | `paradev.surfaces.api-table.v1` | 56 | "
        "`get_surfaces_api_table` | `get_surfaces_api_selection` | `render_surfaces_api_reference_markdown` | `surfaces-api` | `surfaces-api --markdown` |"
    ) in reference
    assert (
        "| `architecture-api` | Architecture API Reference | `api-table` | `sdk` | `architecture` | `paradev.sdk.architecture-api-table.v1` | 17 | "
        "`get_architecture_api_table` | `get_architecture_api_selection` | `render_architecture_api_reference_markdown` | `architecture --api-table` | `architecture --api-table-markdown` |"
    ) in reference
    assert (
        "| `pdx-core-api` | PDX Core API Reference | `facade-table` | `pdx` | `pdx-core` | `paradev.pdx.core-api-table.v1` | 23 | "
        "`get_pdx_core_api_table` | `get_pdx_core_api_selection` | `render_pdx_core_api_reference_markdown` | `pdx-core-api` | `pdx-core-api --markdown` |"
    ) in reference
    assert (
        "| `lsp-server-api` | LSP Server API Reference | `facade-table` | `lsp` | `lsp-server` | `paradev.lsp.server-api-table.v1` | 11 | "
        "`get_lsp_server_api_table` | `get_lsp_server_api_selection` | `render_lsp_server_api_reference_markdown` | `lsp-server-api` | `lsp-server-api --markdown` |"
    ) in reference
    assert (
        "| `hb-api` | HeavenBase Facade API Reference | `facade-table` | `hb` | `facade` | `paradev.hb.api-table.v1` | 27 | "
        "`get_hb_api_table` | `get_hb_api_selection` | `render_hb_api_reference_markdown` | `hb-api` | `hb-api --markdown` |"
    ) in reference
    assert (
        "| `catalog-api` | Catalog API Reference | `api-table` | `hb` | `catalog` | `paradev.hb.catalog-api-table.v1` | 37 | "
        "`get_catalog_api_table` | `get_catalog_api_selection` | `render_catalog_api_reference_markdown` | `catalog-api` | `catalog-api --markdown` |"
    ) in reference
    assert (
        "| `rest-api` | REST API Reference | `route-table` | `rest` | `rest` | `paradev.rest.api-table.v1` | 84 | "
        "`get_rest_api_table` | `get_rest_api_selection` | `render_rest_api_reference_markdown` | `rest-api` | `rest-api --markdown` |"
    ) in reference
    assert (
        "| `mcp-api` | MCP API Reference | `tool-table` | `mcp` | `mcp` | `paradev.mcp.api-table.v1` | 51 | "
        "`get_mcp_api_table` | `get_mcp_api_selection` | `render_mcp_api_reference_markdown` | `mcp-api` | `mcp-api --markdown` |"
    ) in reference
    assert (
        "| `rest-facade-api` | REST Facade API Reference | `facade-table` | `rest` | `rest-facade` | "
        "`paradev.rest.facade-api-table.v1` | 13 | `get_rest_facade_api_table` | "
        "`get_rest_facade_api_selection` | `render_rest_facade_api_reference_markdown` | `rest-facade-api` | `rest-facade-api --markdown` |"
    ) in reference
    manual = Path("docs/user-manual/api-catalog-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["id"] = "changed"
    assert get_api_catalog_table()["rows"][0]["id"] == "api-catalog"
    rows_by_id["frontend-api"]["surfaces"].append("changed")
    assert get_api_catalog_table()["rows"][14]["surfaces"] == [
        "sdk",
        "cli",
        "rest",
        "mcp",
        "lsp",
        "frontend",
        "typescript",
        "docs",
    ]
    frontend_row = get_api_catalog_reference("frontend-api")
    frontend_row["surfaces"].append("changed")
    assert get_api_catalog_reference("frontend-api")["surfaces"] == [
        "sdk",
        "cli",
        "rest",
        "mcp",
        "lsp",
        "frontend",
        "typescript",
        "docs",
    ]


def test_api_catalog_helpers_reject_unknown_keys() -> None:
    from paradev.surfaces import (
        get_api_catalog_reference,
        get_api_catalog_reference_ids,
        get_api_catalog_selection,
    )

    with pytest.raises(
        KeyError,
        match="unknown ParaDev API catalog reference 'missing-api'; expected one of:",
    ):
        get_api_catalog_reference("missing-api")

    with pytest.raises(
        ValueError,
        match="Unknown ParaDev API catalog index: missing. Available indexes:",
    ):
        get_api_catalog_reference_ids("missing", "sdk")

    with pytest.raises(
        ValueError,
        match="Unknown ParaDev API catalog layer: missing. Available layers:",
    ):
        get_api_catalog_reference_ids("layer", "missing")

    with pytest.raises(
        ValueError,
        match="Pass only one API catalog selector: reference_id or index_name/key.",
    ):
        get_api_catalog_selection(reference_id="frontend-api", index_name="surface", key="rest")

    with pytest.raises(
        ValueError,
        match="index_name requires key, and key requires index_name.",
    ):
        get_api_catalog_selection(index_name="surface")


def test_api_catalog_source_index_rejects_duplicate_identity_fields() -> None:
    from paradev.surfaces import API_CATALOG_SOURCE_ROWS
    from paradev.surfaces.api_catalog import _api_catalog_source_index

    base = API_CATALOG_SOURCE_ROWS[1]

    duplicate_id = {**API_CATALOG_SOURCE_ROWS[2], "id": base["id"]}
    with pytest.raises(ValueError, match="duplicate ParaDev API catalog source id 'sdk-api'"):
        _api_catalog_source_index((base, duplicate_id))

    duplicate_doc_page = {
        **API_CATALOG_SOURCE_ROWS[2],
        "id": "sdk-api-doc-page-copy",
        "doc_page": base["doc_page"],
    }
    with pytest.raises(
        ValueError,
        match="duplicate ParaDev API catalog source doc_page 'docs/user-manual/sdk-api-reference.md'",
    ):
        _api_catalog_source_index((base, duplicate_doc_page))

    duplicate_markdown_command = {
        **API_CATALOG_SOURCE_ROWS[2],
        "id": "sdk-api-markdown-command-copy",
        "markdown_cli_command": base["markdown_cli_command"],
    }
    with pytest.raises(
        ValueError,
        match="duplicate ParaDev API catalog source markdown_cli_command 'sdk-api --markdown'",
    ):
        _api_catalog_source_index((base, duplicate_markdown_command))


def test_api_catalog_source_index_rejects_invalid_text_fields() -> None:
    from paradev.surfaces import API_CATALOG_SOURCE_ROWS
    from paradev.surfaces.api_catalog import _api_catalog_source_index

    base = API_CATALOG_SOURCE_ROWS[1]

    missing_title = dict(base)
    missing_title.pop("title")
    with pytest.raises(KeyError, match="ParaDev API catalog source missing 'title'"):
        _api_catalog_source_index((missing_title,))

    missing_selector_helper = dict(base)
    missing_selector_helper.pop("selector_helper")
    with pytest.raises(KeyError, match="ParaDev API catalog source missing 'selector_helper'"):
        _api_catalog_source_index((missing_selector_helper,))

    non_string_kind = {**base, "id": "sdk-api-non-string-kind", "kind": 42}
    with pytest.raises(
        TypeError,
        match="ParaDev API catalog source 'sdk-api-non-string-kind' kind must be a string value, not int",
    ):
        _api_catalog_source_index((non_string_kind,))

    non_string_selector_helper = {
        **base,
        "id": "sdk-api-non-string-selector-helper",
        "selector_helper": 42,
    }
    with pytest.raises(
        TypeError,
        match="ParaDev API catalog source 'sdk-api-non-string-selector-helper' selector_helper must be a string value, not int",
    ):
        _api_catalog_source_index((non_string_selector_helper,))

    empty_doc_page = {**base, "id": "sdk-api-empty-doc-page", "doc_page": ""}
    with pytest.raises(
        ValueError,
        match="ParaDev API catalog source 'sdk-api-empty-doc-page' doc_page must not be empty",
    ):
        _api_catalog_source_index((empty_doc_page,))


def test_api_catalog_source_index_rejects_invalid_surfaces() -> None:
    from paradev.surfaces import API_CATALOG_SOURCE_ROWS
    from paradev.surfaces.api_catalog import _api_catalog_source_index

    base = API_CATALOG_SOURCE_ROWS[1]

    empty_surfaces = {**base, "id": "sdk-api-empty-surfaces", "surfaces": []}
    with pytest.raises(
        ValueError,
        match="ParaDev API catalog source 'sdk-api-empty-surfaces' must expose at least one surface",
    ):
        _api_catalog_source_index((empty_surfaces,))

    duplicate_surfaces = {
        **base,
        "id": "sdk-api-duplicate-surfaces",
        "surfaces": ["sdk", "sdk"],
    }
    with pytest.raises(
        ValueError,
        match="duplicate ParaDev API catalog source surface 'sdk' for 'sdk-api-duplicate-surfaces'",
    ):
        _api_catalog_source_index((duplicate_surfaces,))

    empty_surface_value = {
        **base,
        "id": "sdk-api-empty-surface",
        "surfaces": ["sdk", ""],
    }
    with pytest.raises(
        ValueError,
        match="ParaDev API catalog source 'sdk-api-empty-surface' surface value must not be empty",
    ):
        _api_catalog_source_index((empty_surface_value,))

    string_surfaces = {**base, "id": "sdk-api-string-surfaces", "surfaces": "sdk"}
    with pytest.raises(
        TypeError,
        match="ParaDev API catalog source 'sdk-api-string-surfaces' surfaces must be a list-like value, not str",
    ):
        _api_catalog_source_index((string_surfaces,))

    non_string_surface = {
        **base,
        "id": "sdk-api-non-string-surface",
        "surfaces": ["sdk", 42],
    }
    with pytest.raises(
        TypeError,
        match="ParaDev API catalog source 'sdk-api-non-string-surface' surface values must be strings, not int",
    ):
        _api_catalog_source_index((non_string_surface,))


def test_api_catalog_load_payload_validates_helper_metadata() -> None:
    from paradev.surfaces import API_CATALOG_SCHEMA, API_CATALOG_SOURCE_ROWS
    from paradev.surfaces.api_catalog import _api_catalog_load_payload

    base = {
        **API_CATALOG_SOURCE_ROWS[1],
        "owner_module": "paradev.surfaces.api_catalog",
        "table_helper": "_api_catalog_self_payload",
        "selector_helper": "",
        "markdown_helper": "render_api_catalog_reference_markdown",
    }

    assert _api_catalog_load_payload(base)["schema"] == API_CATALOG_SCHEMA

    selector_base = {**base, "selector_helper": "get_api_catalog_selection"}
    assert _api_catalog_load_payload(selector_base)["schema"] == API_CATALOG_SCHEMA

    noncallable_table_helper = {**base, "table_helper": "API_CATALOG_SCHEMA"}
    noncallable_table_pattern = (
        "ParaDev API catalog source 'sdk-api' table_helper " "paradev\\.surfaces\\.api_catalog\\.API_CATALOG_SCHEMA must be callable, got str"
    )
    with pytest.raises(
        TypeError,
        match=noncallable_table_pattern,
    ):
        _api_catalog_load_payload(noncallable_table_helper)

    noncallable_selector_helper = {
        **base,
        "id": "sdk-api-selector-helper-copy",
        "selector_helper": "API_CATALOG_SCHEMA",
    }
    with pytest.raises(
        TypeError,
        match=(
            "ParaDev API catalog source 'sdk-api-selector-helper-copy' selector_helper "
            "paradev\\.surfaces\\.api_catalog\\.API_CATALOG_SCHEMA must be callable, got str"
        ),
    ):
        _api_catalog_load_payload(noncallable_selector_helper)

    noncallable_markdown_helper = {
        **base,
        "id": "sdk-api-markdown-helper-copy",
        "markdown_helper": "API_CATALOG_SCHEMA",
    }
    with pytest.raises(
        TypeError,
        match=(
            "ParaDev API catalog source 'sdk-api-markdown-helper-copy' markdown_helper "
            "paradev\\.surfaces\\.api_catalog\\.API_CATALOG_SCHEMA must be callable, got str"
        ),
    ):
        _api_catalog_load_payload(noncallable_markdown_helper)

    missing_table_helper = {
        **base,
        "id": "sdk-api-missing-table-helper",
        "table_helper": "missing_api_catalog_helper",
    }
    missing_table_pattern = (
        "ParaDev API catalog source 'sdk-api-missing-table-helper' table_helper " "paradev\\.surfaces\\.api_catalog\\.missing_api_catalog_helper is missing"
    )
    with pytest.raises(
        AttributeError,
        match=missing_table_pattern,
    ):
        _api_catalog_load_payload(missing_table_helper)


def test_project_view_is_sdk_owned(tmp_path) -> None:
    from paradev.sdk import open_project

    (tmp_path / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: test_project",
                "title: Test Project",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
            ]
        ),
        encoding="utf-8",
    )

    project = open_project(tmp_path)
    view = project.to_view()

    assert view["root"] == str(tmp_path)
    assert view["game"] == "hoi4"
    assert view["sdk"]["status"] == "scaffold"
    assert view["surfaces"]["rest"]["status"] == "scaffold"
    assert "mcp" in view["surfaces"]


def test_openapi_seed_renders_without_runtime_server() -> None:
    from paradev.sdk.project import MAX_MODULE_CREATE_BATCH_SIZE
    from paradev.surfaces.rest import get_openapi_seed

    seed = get_openapi_seed()

    assert seed["openapi"] == "3.1.0"
    assert seed["info"]["title"] == "ParaDev Local API"
    assert "/frontend-api" in seed["paths"]
    assert "/frontend-api/workspace" in seed["paths"]
    assert "/frontend-api/action" in seed["paths"]
    assert "/frontend-api/normalize" in seed["paths"]
    assert "/frontend-api/rest-request" in seed["paths"]
    assert "/frontend-api/options" in seed["paths"]
    assert "/frontend-api/binding" in seed["paths"]
    assert "/api-catalog" in seed["paths"]
    assert "/surface-contracts" in seed["paths"]
    assert "/architecture" in seed["paths"]
    assert "/projects/{project_id}/sources" in seed["paths"]
    assert "/projects/{project_id}/drafts/apply" in seed["paths"]
    assert "/projects/{project_id}/modules/{family_id}/drafts" in seed["paths"]
    assert "/projects/modules/create-batch" in seed["paths"]
    assert "/projects/modules/duplicate" in seed["paths"]
    assert "/pdx/parse" in seed["paths"]
    assert "/pdx/format" in seed["paths"]
    assert "/lsp-api" in seed["paths"]
    assert "/lsp/diagnostics" in seed["paths"]
    assert "/lsp/symbols" in seed["paths"]
    assert "/lsp/hover" in seed["paths"]
    assert "/lsp/formatting" in seed["paths"]
    assert "/lsp/completion" in seed["paths"]
    assert "/lsp/semantic-tokens" in seed["paths"]
    assert "/lsp/keywords" in seed["paths"]
    assert "/projects/inspections" in seed["paths"]
    assert "/projects/inspect" in seed["paths"]
    assert "/projects/templates" in seed["paths"]
    assert "/projects/authoring-path" in seed["paths"]
    assert "/projects/authoring-plan" in seed["paths"]
    assert "/projects/scaffold" in seed["paths"]
    assert "/projects/build" in seed["paths"]
    assert "/projects/catalog" in seed["paths"]
    assert "/projects" in seed["paths"]
    assert "/projects/list" in seed["paths"]
    assert "/desktop/state" in seed["paths"]
    assert "/desktop/builds" in seed["paths"]
    assert "/desktop/builds/status" in seed["paths"]
    assert "/desktop/builds/interrupt" in seed["paths"]
    assert "/desktop/path-status" in seed["paths"]
    assert "/desktop/select-project" in seed["paths"]
    assert "/desktop/hoi4-launch-readiness" in seed["paths"]
    assert "/desktop/app-config" in seed["paths"]
    assert "/desktop/config-value" in seed["paths"]
    assert "/desktop/llm/test" in seed["paths"]
    assert "/desktop/ai/chat" in seed["paths"]
    assert "/desktop/ai/profiles" in seed["paths"]
    assert "/desktop/ai/profiles/{profile_id}" in seed["paths"]
    assert "/projects/browser" in seed["paths"]
    assert "/projects/find" in seed["paths"]
    assert "/projects/rename" in seed["paths"]
    assert "/projects/language" in seed["paths"]
    assert "/projects/modules/rename" in seed["paths"]
    assert "/projects/modules/remove" in seed["paths"]
    assert "/projects/modules/file" in seed["paths"]
    assert "/projects/collections/scaffold" in seed["paths"]
    assert "/projects/collections" in seed["paths"]
    assert "/projects/collections/rename" in seed["paths"]
    assert "/projects/collections/file" in seed["paths"]
    template_params = {param["name"]: param for param in seed["paths"]["/projects/templates"]["get"]["parameters"]}
    assert template_params["template_id"]["required"] is False
    assert template_params["family"]["required"] is False
    assert template_params["kind"]["schema"]["enum"] == ["module", "collection"]
    assert template_params["authoring_ready"]["schema"]["type"] == "boolean"
    assert template_params["diagnostic_code"]["required"] is False
    authoring_params = {param["name"]: param for param in seed["paths"]["/projects/authoring-path"]["get"]["parameters"]}
    assert authoring_params["kind"]["required"] is True
    assert authoring_params["family"]["required"] is True
    assert authoring_params["target_id"]["required"] is True
    assert authoring_params["source_root"]["required"] is False
    scaffold = seed["paths"]["/projects/scaffold"]["post"]
    scaffold_params = {param["name"]: param for param in scaffold["parameters"]}
    assert scaffold_params["template_id"]["required"] is True
    assert scaffold_params["object_id"]["required"] is True
    assert scaffold_params["source_root"]["required"] is False
    assert scaffold_params["write"]["schema"]["default"] is False
    assert scaffold["requestBody"]["required"] is False
    collection_scaffold = seed["paths"]["/projects/collections/scaffold"]["post"]
    collection_scaffold_params = {param["name"]: param for param in collection_scaffold["parameters"]}
    assert collection_scaffold_params["template_id"]["required"] is True
    assert collection_scaffold_params["collection_id"]["required"] is True
    assert collection_scaffold_params["write"]["schema"]["default"] is False
    assert collection_scaffold_params["force"]["schema"]["default"] is False
    assert collection_scaffold_params["plan_hash"]["required"] is False
    assert collection_scaffold["requestBody"]["required"] is False
    project_build = seed["paths"]["/projects/build"]["post"]
    project_build_params = {param["name"]: param for param in project_build["parameters"]}
    assert project_build_params["path"]["required"] is False
    assert project_build_params["emit_artifacts"]["schema"]["default"] is False
    assert project_build_params["emit_manifests"]["schema"]["default"] is False
    assert "default" not in project_build_params["strict_metadata"]["schema"]
    assert project_build["responses"]["200"]["description"] == "Build result payload."
    source_get = seed["paths"]["/projects/{project_id}/sources"]["get"]
    assert {
        "name": "path",
        "in": "query",
        "required": True,
        "schema": {"type": "string"},
    } in source_get["parameters"]
    source_response_schema = source_get["responses"]["200"]["content"]["application/json"]["schema"]
    assert source_response_schema["additionalProperties"] is False
    assert source_response_schema["properties"]["size"] == {
        "type": "integer",
        "minimum": 0,
    }
    assert source_response_schema["properties"]["mtime_ns"] == {
        "type": "string",
        "pattern": "^[0-9]+$",
    }
    draft_apply = seed["paths"]["/projects/{project_id}/drafts/apply"]["post"]
    draft_apply_body_schema = draft_apply["requestBody"]["content"]["application/json"]["schema"]
    assert draft_apply_body_schema["additionalProperties"] is False
    assert draft_apply_body_schema["anyOf"] == [
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
        {
            "required": ["module_rename"],
        },
    ]
    draft_apply_schema = draft_apply_body_schema["properties"]
    assert draft_apply_schema["source_edits"]["type"] == "array"
    assert draft_apply_schema["source_removals"]["type"] == "array"
    assert draft_apply_schema["source_replacements"]["type"] == "array"
    assert draft_apply_schema["module_rename"] == {
        "type": "object",
        "additionalProperties": False,
        "description": ("Optional canonical module-folder rename committed after every " "source draft succeeds."),
        "required": ["module_id", "object_id"],
        "properties": {
            "module_id": {"type": "string"},
            "object_id": {"type": "string"},
            "source_root": {"type": ["string", "null"]},
            "title": {"type": ["string", "null"]},
        },
    }
    edit_schema = draft_apply_schema["source_edits"]["items"]
    assert edit_schema["additionalProperties"] is False
    assert edit_schema["dependentRequired"] == {
        "expected_size": ["expected_mtime_ns"],
        "expected_mtime_ns": ["expected_size"],
    }
    assert edit_schema["properties"]["expected_size"] == {
        "type": "integer",
        "minimum": 0,
    }
    assert edit_schema["properties"]["expected_mtime_ns"] == {
        "type": "string",
        "pattern": "^[0-9]+$",
    }
    replacement_schema = draft_apply_schema["source_replacements"]["items"]
    assert replacement_schema["additionalProperties"] is False
    assert replacement_schema["dependentRequired"] == {
        "expected_size": ["expected_mtime_ns"],
        "expected_mtime_ns": ["expected_size"],
        "content_format": ["target_format"],
        "target_format": ["content_format"],
    }
    assert replacement_schema["allOf"] == [
        {
            "if": {
                "required": ["expected_absent"],
                "properties": {"expected_absent": {"const": True}},
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
    ]
    assert replacement_schema["properties"]["expected_size"] == {
        "type": "integer",
        "minimum": 0,
    }
    assert replacement_schema["properties"]["expected_mtime_ns"] == {
        "type": "string",
        "pattern": "^[0-9]+$",
    }
    assert replacement_schema["properties"]["expected_absent"] == {"type": "boolean"}
    removal_schema = draft_apply_schema["source_removals"]["items"]["oneOf"][1]
    assert removal_schema["additionalProperties"] is False
    assert removal_schema["dependentRequired"] == {
        "expected_size": ["expected_mtime_ns"],
        "expected_mtime_ns": ["expected_size"],
    }
    assert replacement_schema["properties"]["content_format"]["enum"] == ["png"]
    assert replacement_schema["properties"]["target_format"]["enum"] == [
        "bmp",
        "dds",
        "jpeg",
        "jpg",
        "tga",
        "webp",
    ]
    module_draft = seed["paths"]["/projects/{project_id}/modules/{family_id}/drafts"]["post"]
    assert module_draft["requestBody"]["content"]["application/json"]["schema"]["properties"]["object_id"]["type"] == "string"
    module_create_batch = seed["paths"]["/projects/modules/create-batch"]["post"]
    module_create_batch_schema = module_create_batch["requestBody"]["content"]["application/json"]["schema"]
    assert module_create_batch_schema["required"] == ["project_id", "modules"]
    assert module_create_batch_schema["additionalProperties"] is False
    assert module_create_batch_schema["properties"]["modules"]["minItems"] == 1
    assert module_create_batch_schema["properties"]["modules"]["maxItems"] == MAX_MODULE_CREATE_BATCH_SIZE
    assert module_create_batch_schema["properties"]["write"]["default"] is False
    module_duplicate = seed["paths"]["/projects/modules/duplicate"]["post"]
    module_duplicate_schema = module_duplicate["requestBody"]["content"]["application/json"]["schema"]
    assert module_duplicate_schema["required"] == [
        "project_root",
        "module_id",
        "object_id",
    ]
    assert module_duplicate_schema["additionalProperties"] is False
    assert module_duplicate_schema["properties"]["write"]["default"] is False
    assert module_duplicate_schema["properties"]["plan_hash"]["type"] == "string"
    module_metadata_clean = seed["paths"]["/projects/modules/metadata/clean"]["post"]
    module_metadata_clean_schema = module_metadata_clean["requestBody"]["content"]["application/json"]["schema"]
    assert module_metadata_clean_schema["required"] == ["project_root"]
    assert module_metadata_clean_schema["additionalProperties"] is False
    assert module_metadata_clean_schema["properties"]["write"]["default"] is False
    assert module_metadata_clean_schema["allOf"][0]["then"] == {"required": ["plan_hash"]}
    module_collection = seed["paths"]["/projects/modules/collection"]["post"]
    module_collection_schema = module_collection["requestBody"]["content"]["application/json"]["schema"]
    assert module_collection_schema["required"] == ["project_root", "module_id"]
    assert module_collection_schema["additionalProperties"] is False
    assert module_collection_schema["properties"]["collection_id"]["type"] == ["string", "null"]
    assert module_collection_schema["properties"]["write"]["default"] is False
    assert module_collection_schema["allOf"][0]["then"] == {"required": ["plan_hash"]}
    catalog_status = seed["paths"]["/projects/catalog"]["get"]
    catalog_write = seed["paths"]["/projects/catalog"]["post"]
    catalog_refresh = seed["paths"]["/projects/catalog"]["put"]
    catalog_status_params = {param["name"]: param for param in catalog_status["parameters"]}
    catalog_write_params = {param["name"]: param for param in catalog_write["parameters"]}
    catalog_refresh_params = {param["name"]: param for param in catalog_refresh["parameters"]}
    assert catalog_status_params["path"]["schema"]["default"] == "."
    assert catalog_status["responses"]["200"]["description"] == "Catalog status payload."
    assert catalog_write_params["path"]["schema"]["default"] == "."
    assert catalog_write_params["profile"]["required"] is False
    assert catalog_write_params["database"]["required"] is False
    assert catalog_refresh_params == catalog_write_params
    assert catalog_write["responses"]["200"]["description"] == "Catalog write payload."
    assert catalog_refresh["responses"]["200"]["description"] == "Catalog refresh payload."
    project_open = seed["paths"]["/projects"]["get"]
    project_open_params = {param["name"]: param for param in project_open["parameters"]}
    assert project_open_params["path"]["required"] is False
    assert project_open_params["game"]["required"] is False
    assert project_open_params["title"]["required"] is False
    assert project_open["responses"]["200"]["description"] == "Project view payload."
    project_create = seed["paths"]["/projects"]["post"]
    project_create_params = {param["name"]: param for param in project_create["parameters"]}
    assert project_create_params["path"]["required"] is True
    assert project_create_params["project_id"]["required"] is False
    assert project_create_params["title"]["required"] is False
    assert project_create_params["game"]["schema"]["default"] == "hoi4"
    assert project_create_params["force"]["schema"]["default"] is False
    assert project_create["responses"]["200"]["description"] == "Project create payload."
    project_list = seed["paths"]["/projects/list"]["get"]
    project_list_params = {param["name"]: param for param in project_list["parameters"]}
    assert project_list_params["project_paths"]["schema"]["type"] == "array"
    assert project_list_params["search_roots"]["schema"]["default"] == []
    assert project_list["responses"]["200"]["description"] == "Project registry payload."
    desktop_state = seed["paths"]["/desktop/state"]["get"]
    desktop_state_params = {param["name"]: param for param in desktop_state["parameters"]}
    assert desktop_state_params["project_path"]["required"] is False
    assert desktop_state_params["project_paths"]["schema"]["type"] == "array"
    assert desktop_state["responses"]["200"]["description"] == "Desktop state payload."
    desktop_build_start = seed["paths"]["/desktop/builds"]["post"]
    desktop_build_start_schema = desktop_build_start["requestBody"]["content"]["application/json"]["schema"]
    assert desktop_build_start["requestBody"]["required"] is True
    assert desktop_build_start_schema["required"] == ["project_root"]
    assert desktop_build_start_schema["properties"]["projectRoot"]["type"] == "string"
    assert desktop_build_start_schema["properties"]["project_root"]["type"] == "string"
    assert desktop_build_start_schema["properties"]["strictMetadata"]["type"] == "boolean"
    assert desktop_build_start_schema["properties"]["parallelism"]["minimum"] == 1
    assert desktop_build_start_schema["properties"]["target"]["properties"]["kind"]["enum"] == ["module", "collection", "family"]
    assert desktop_build_start["responses"]["200"]["description"] == "Desktop build run payload."
    desktop_build_status = seed["paths"]["/desktop/builds/status"]["get"]
    desktop_build_status_params = {param["name"]: param for param in desktop_build_status["parameters"]}
    assert desktop_build_status_params["run_id"]["required"] is True
    assert desktop_build_status_params["run_id"]["schema"] == {
        "type": "string",
        "minLength": 1,
        "pattern": r".*\S.*",
    }
    assert desktop_build_status["responses"]["200"]["description"] == "Desktop build run payload."
    desktop_build_interrupt = seed["paths"]["/desktop/builds/interrupt"]["post"]
    desktop_build_interrupt_schema = desktop_build_interrupt["requestBody"]["content"]["application/json"]["schema"]
    assert desktop_build_interrupt["requestBody"]["required"] is True
    nonblank_run_id_schema = {
        "type": "string",
        "minLength": 1,
        "pattern": r".*\S.*",
    }
    assert desktop_build_interrupt_schema == {
        "type": "object",
        "additionalProperties": False,
        "anyOf": [
            {"required": ["runId"], "properties": {"runId": nonblank_run_id_schema}},
            {"required": ["run_id"], "properties": {"run_id": nonblank_run_id_schema}},
        ],
        "properties": {
            "runId": {"anyOf": [nonblank_run_id_schema, {"type": "null"}]},
            "run_id": {"anyOf": [nonblank_run_id_schema, {"type": "null"}]},
        },
    }
    assert desktop_build_interrupt["responses"]["200"]["description"] == "Desktop build run payload."
    desktop_open_path = seed["paths"]["/desktop/open-path"]["post"]
    desktop_open_path_schema = desktop_open_path["requestBody"]["content"]["application/json"]["schema"]
    assert desktop_open_path["requestBody"]["required"] is True
    assert desktop_open_path_schema["required"] == ["path"]
    assert desktop_open_path_schema["properties"]["path"]["type"] == "string"
    assert desktop_open_path_schema["properties"]["target"]["type"] == "string"
    assert desktop_open_path["responses"]["200"]["description"] == "Desktop open-path payload."
    desktop_select_project = seed["paths"]["/desktop/select-project"]["post"]
    assert desktop_select_project["responses"]["200"]["description"] == "Desktop project-selection payload."
    desktop_path_status = seed["paths"]["/desktop/path-status"]["get"]
    desktop_path_status_params = {param["name"]: param for param in desktop_path_status["parameters"]}
    assert desktop_path_status_params["path"]["required"] is True
    assert desktop_path_status["responses"]["200"]["description"] == "Desktop path status payload."
    desktop_app_config = seed["paths"]["/desktop/app-config"]
    assert desktop_app_config["get"]["responses"]["200"]["description"] == "Desktop app config payload."
    assert desktop_app_config["put"]["requestBody"]["required"] is True
    assert desktop_app_config["put"]["responses"]["200"]["description"] == "Desktop app config write status."
    desktop_config_value = seed["paths"]["/desktop/config-value"]
    desktop_config_value_get_params = {param["name"]: param for param in desktop_config_value["get"]["parameters"]}
    desktop_config_value_put_schema = desktop_config_value["put"]["requestBody"]["content"]["application/json"]["schema"]
    assert desktop_config_value_get_params["key"]["required"] is True
    assert desktop_config_value_put_schema["required"] == ["key", "value"]
    assert desktop_config_value_put_schema["properties"]["key"]["type"] == "string"
    assert desktop_config_value["put"]["responses"]["200"]["description"] == "Desktop config value payload."
    desktop_llm_test = seed["paths"]["/desktop/llm/test"]["post"]
    desktop_llm_test_schema = desktop_llm_test["requestBody"]["content"]["application/json"]["schema"]
    assert desktop_llm_test_schema["required"] == ["provider", "model", "gateway"]
    assert desktop_llm_test_schema["properties"]["preset"]["default"] == "chat"
    assert desktop_llm_test_schema["properties"]["preset"]["enum"] == [
        "system",
        "chat",
        "reason",
        "coder",
    ]
    assert desktop_llm_test_schema["properties"]["base_url"]["type"] == "string"
    assert desktop_llm_test["responses"]["200"]["description"] == "Desktop LLM route test payload."
    desktop_ai_chat = seed["paths"]["/desktop/ai/chat"]["post"]
    desktop_ai_chat_schema = desktop_ai_chat["requestBody"]["content"]["application/json"]["schema"]
    assert desktop_ai_chat_schema["required"] == [
        "provider",
        "model",
        "gateway",
        "prompt",
    ]
    assert desktop_ai_chat_schema["properties"]["provider"]["default"] == "deepseek"
    assert desktop_ai_chat_schema["properties"]["model"]["default"] == "deepseek-v4-flash"
    assert desktop_ai_chat_schema["properties"]["gateway"]["default"] == "openai"
    assert desktop_ai_chat_schema["properties"]["preset"]["default"] == "chat"
    assert desktop_ai_chat_schema["properties"]["preset"]["enum"] == [
        "system",
        "chat",
        "reason",
        "coder",
    ]
    assert desktop_ai_chat_schema["properties"]["key_env"]["type"] == "string"
    assert desktop_ai_chat_schema["properties"]["base_url"]["type"] == "string"
    assert desktop_ai_chat_schema["properties"]["sources"]["items"]["type"] == "object"
    assert desktop_ai_chat["responses"]["200"]["description"] == "Desktop AI chat payload."
    desktop_ai_profiles = seed["paths"]["/desktop/ai/profiles"]["get"]
    desktop_ai_profiles_params = {param["name"]: param for param in desktop_ai_profiles["parameters"]}
    assert desktop_ai_profiles_params["project_root"]["required"] is False
    assert desktop_ai_profiles["responses"]["200"]["description"] == "Desktop AI chat profile payload."
    desktop_ai_profiles_response_schema = desktop_ai_profiles["responses"]["200"]["content"]["application/json"]["schema"]
    assert desktop_ai_profiles_response_schema["properties"]["sourceKindRows"]["items"]["properties"]["frontendKinds"]["items"]["type"] == "string"
    assert desktop_ai_profiles_response_schema["properties"]["sourceKindRows"]["items"]["properties"]["id"]["enum"] == [
        "project",
        "selection",
        "diagnostics",
        "templates",
    ]
    assert desktop_ai_profiles_response_schema["properties"]["sourceKindRows"]["items"]["properties"]["frontendKinds"]["default"] == ["workspace"]
    desktop_ai_profile_write = seed["paths"]["/desktop/ai/profiles/{profile_id}"]["put"]
    desktop_ai_profile_write_params = {param["name"]: param for param in desktop_ai_profile_write["parameters"]}
    desktop_ai_profile_write_schema = desktop_ai_profile_write["requestBody"]["content"]["application/json"]["schema"]
    assert desktop_ai_profile_write_params["profile_id"]["required"] is True
    planned_ai_profile_schema, legacy_ai_profile_schema = desktop_ai_profile_write_schema["oneOf"]
    assert planned_ai_profile_schema["required"] == ["profile"]
    assert planned_ai_profile_schema["properties"]["profile"]["type"] == "object"
    assert planned_ai_profile_schema["properties"]["profile"]["properties"]["sourceKinds"]["items"]["type"] == "string"
    assert planned_ai_profile_schema["properties"]["profile"]["properties"]["sourceKinds"]["items"]["enum"] == [
        "project",
        "selection",
        "diagnostics",
        "templates",
    ]
    assert planned_ai_profile_schema["properties"]["project_root"]["type"] == "string"
    assert legacy_ai_profile_schema["required"] == ["prompt"]
    assert legacy_ai_profile_schema["properties"]["sourceKinds"]["items"]["type"] == "string"
    assert legacy_ai_profile_schema["properties"]["sourceKinds"]["items"]["enum"] == [
        "project",
        "selection",
        "diagnostics",
        "templates",
    ]
    assert legacy_ai_profile_schema["properties"]["projectRoot"]["type"] == "string"
    assert desktop_ai_profile_write["responses"]["200"]["description"] == "Desktop AI chat profile payload."
    assert desktop_ai_profile_write["responses"]["200"]["content"]["application/json"]["schema"] == desktop_ai_profiles_response_schema
    desktop_ai_profile_reset = seed["paths"]["/desktop/ai/profiles/{profile_id}"]["delete"]
    desktop_ai_profile_reset_params = {param["name"]: param for param in desktop_ai_profile_reset["parameters"]}
    assert desktop_ai_profile_reset["x-paradev-frontend-api-operation-ids"] == ["ai.profile.reset"]
    assert desktop_ai_profile_reset_params["profile_id"]["required"] is True
    assert desktop_ai_profile_reset_params["project_root"]["required"] is False
    assert desktop_ai_profile_reset["responses"]["200"]["description"] == "Desktop AI chat profile payload."
    assert desktop_ai_profile_reset["responses"]["200"]["content"]["application/json"]["schema"] == desktop_ai_profiles_response_schema
    project_browser = seed["paths"]["/projects/browser"]["get"]
    project_browser_params = {param["name"]: param for param in project_browser["parameters"]}
    assert project_browser_params["path"]["schema"]["default"] == "."
    assert project_browser_params["kind"]["schema"]["enum"] == ["module", "collection"]
    assert project_browser_params["collection_id"]["required"] is False
    assert project_browser["responses"]["200"]["description"] == "Project browser payload."
    inspect_contract = seed["paths"]["/projects/inspect"]["get"]["x-paradev-inspection-contract"]
    inspect_rows = {row["kind"]: row for row in inspect_contract["inspections"]}
    assert inspect_rows["modules"]["filters"] == [
        "profile",
        "family",
        "module_id",
        "collection_id",
        "source_slot",
    ]
    assert inspect_rows["sources"]["filters"] == [
        "profile",
        "family",
        "module_id",
        "collection_id",
        "slot",
        "loader",
        "status",
        "owner_kind",
    ]
    assert inspect_rows["assets"]["filters"] == [
        "profile",
        "module_id",
        "collection_id",
        "family",
        "slot",
        "file_format",
    ]
    assert inspect_rows["sprites"]["filters"] == [
        "profile",
        "module_id",
        "collection_id",
        "family",
        "slot",
        "name",
    ]
    assert "modules" in inspect_contract["index"]["filter"]["module_id"]
    assert "sources" in inspect_contract["index"]["filter"]["owner_kind"]
    assert "assets" in inspect_contract["index"]["filter"]["file_format"]
    assert "sprites" in inspect_contract["index"]["filter"]["name"]
    frontend_contract = seed["paths"]["/frontend-api"]["get"]["x-paradev-frontend-api-contract"]
    assert frontend_contract["schema"] == "paradev.sdk.frontend-api.v1"
    assert frontend_contract["workspace"]["schema"] == "paradev.sdk.frontend-api.workspace.v1"
    assert "project.find" in frontend_contract["index"]["status"]["implemented"]
    assert "project.create" in frontend_contract["index"]["status"]["implemented"]
    assert "project.rename" in frontend_contract["index"]["status"]["implemented"]
    frontend_params = {param["name"]: param for param in seed["paths"]["/frontend-api"]["get"]["parameters"]}
    assert frontend_params["operation_id"]["required"] is False
    assert frontend_params["group_id"]["required"] is False
    assert frontend_params["operation_id"]["schema"]["type"] == "string"
    assert frontend_params["group_id"]["schema"]["type"] == "string"
    assert frontend_params["form"]["schema"]["default"] is False
    frontend_workspace = seed["paths"]["/frontend-api/workspace"]["get"]
    assert frontend_workspace["responses"]["200"]["description"] == "Frontend API workspace projection."
    assert frontend_workspace["x-paradev-frontend-api-operation-ids"] == ["surface.frontend_api.workspace"]
    frontend_action = seed["paths"]["/frontend-api/action"]["get"]
    frontend_action_params = {param["name"]: param for param in frontend_action["parameters"]}
    assert frontend_action_params["operation_id"]["required"] is True
    assert frontend_action["responses"]["200"]["description"] == "Frontend API action detail."
    frontend_normalize = seed["paths"]["/frontend-api/normalize"]["post"]
    frontend_normalize_params = {param["name"]: param for param in frontend_normalize["parameters"]}
    assert frontend_normalize_params["operation_id"]["required"] is True
    assert frontend_normalize["requestBody"]["required"] is False
    assert frontend_normalize["requestBody"]["content"]["application/json"]["schema"] == {"type": "object", "additionalProperties": True}
    assert frontend_normalize["responses"]["200"]["description"] == "Normalized frontend API input payload."
    frontend_rest_request = seed["paths"]["/frontend-api/rest-request"]["post"]
    frontend_rest_request_params = {param["name"]: param for param in frontend_rest_request["parameters"]}
    assert frontend_rest_request_params["operation_id"]["required"] is True
    assert frontend_rest_request["requestBody"]["required"] is False
    assert frontend_rest_request["requestBody"]["content"]["application/json"]["schema"] == {"type": "object", "additionalProperties": True}
    assert frontend_rest_request["responses"]["200"]["description"] == "Frontend API REST request plan."
    frontend_options = seed["paths"]["/frontend-api/options"]["post"]
    frontend_options_params = {param["name"]: param for param in frontend_options["parameters"]}
    assert frontend_options_params["operation_id"]["required"] is True
    assert frontend_options_params["field_name"]["required"] is True
    assert frontend_options["requestBody"]["required"] is False
    assert frontend_options["requestBody"]["content"]["application/json"]["schema"] == {
        "type": "object",
        "additionalProperties": True,
    }
    assert frontend_options["responses"]["200"]["description"] == "Frontend API option-source payload."
    frontend_binding = seed["paths"]["/frontend-api/binding"]["get"]
    frontend_binding_params = {param["name"]: param for param in frontend_binding["parameters"]}
    assert frontend_binding_params["binding_surface"]["required"] is True
    assert frontend_binding_params["binding_surface"]["schema"]["enum"] == [
        "cli",
        "lsp",
        "mcp",
        "rest",
        "sdk",
    ]
    assert frontend_binding_params["binding_key"]["required"] is True
    assert frontend_binding["responses"]["200"]["description"] == "Frontend API binding lookup payload."
    assert frontend_binding["x-paradev-frontend-api-operation-ids"] == ["surface.frontend_api.binding_lookup"]
    api_catalog = seed["paths"]["/api-catalog"]["get"]
    api_catalog_params = {param["name"]: param for param in api_catalog["parameters"]}
    assert api_catalog_params["reference_id"]["required"] is False
    assert api_catalog_params["index_name"]["required"] is False
    assert api_catalog_params["key"]["required"] is False
    assert api_catalog["responses"]["200"]["description"] == "API catalog table, row, or index lookup payload."
    assert api_catalog["responses"]["400"]["description"] == "Invalid API catalog selector."
    rest_api = seed["paths"]["/rest-api"]["get"]
    rest_api_params = {param["name"]: param for param in rest_api["parameters"]}
    assert rest_api_params["symbol"]["required"] is False
    assert rest_api_params["index_name"]["required"] is False
    assert rest_api_params["key"]["required"] is False
    assert rest_api["responses"]["200"]["description"] == "REST API table, row, or index lookup payload."
    assert rest_api["responses"]["400"]["description"] == "Invalid REST API selector."
    catalog_api = seed["paths"]["/catalog-api"]["get"]
    catalog_api_params = {param["name"]: param for param in catalog_api["parameters"]}
    assert catalog_api_params["symbol"]["required"] is False
    assert catalog_api_params["index_name"]["required"] is False
    assert catalog_api_params["key"]["required"] is False
    assert catalog_api["responses"]["200"]["description"] == "Catalog API table, row, or index lookup payload."
    assert catalog_api["responses"]["400"]["description"] == "Invalid catalog API selector."
    surface_contracts = seed["paths"]["/surface-contracts"]["get"]
    surface_contracts_params = {param["name"]: param for param in surface_contracts["parameters"]}
    assert surface_contracts_params["identifier"]["required"] is False
    assert surface_contracts_params["status"]["required"] is False
    assert surface_contracts["responses"]["200"]["description"] == "Surface contract summary, contract payload, or status id list."
    assert surface_contracts["responses"]["400"]["description"] == "Invalid surface contract selector."
    pdx_format = seed["paths"]["/pdx/format"]["post"]
    pdx_format_params = {param["name"]: param for param in pdx_format["parameters"]}
    assert pdx_format_params["path"]["required"] is True
    assert pdx_format_params["write"]["schema"]["default"] is False
    lsp_formatting = seed["paths"]["/lsp/formatting"]["post"]
    assert lsp_formatting["requestBody"]["required"] is True
    lsp_formatting_schema = lsp_formatting["requestBody"]["content"]["application/json"]["schema"]
    assert lsp_formatting_schema["required"] == ["text"]
    assert lsp_formatting_schema["properties"]["uri"]["type"] == "string"
    lsp_diagnostics = seed["paths"]["/lsp/diagnostics"]["post"]
    assert lsp_diagnostics["requestBody"]["required"] is True
    lsp_diagnostics_schema = lsp_diagnostics["requestBody"]["content"]["application/json"]["schema"]
    assert lsp_diagnostics_schema["required"] == ["text"]
    assert lsp_diagnostics_schema["properties"]["path"]["type"] == "string"
    lsp_symbols = seed["paths"]["/lsp/symbols"]["post"]
    assert lsp_symbols["requestBody"]["required"] is True
    lsp_symbols_schema = lsp_symbols["requestBody"]["content"]["application/json"]["schema"]
    assert lsp_symbols_schema["required"] == ["text"]
    assert lsp_symbols_schema["properties"]["uri"]["type"] == "string"
    lsp_hover = seed["paths"]["/lsp/hover"]["post"]
    assert lsp_hover["requestBody"]["required"] is True
    lsp_hover_schema = lsp_hover["requestBody"]["content"]["application/json"]["schema"]
    assert lsp_hover_schema["required"] == ["text", "line", "character"]
    assert lsp_hover_schema["properties"]["line"]["type"] == "integer"
    assert lsp_hover_schema["properties"]["character"]["minimum"] == 0
    lsp_completion = seed["paths"]["/lsp/completion"]["post"]
    assert lsp_completion["requestBody"]["required"] is True
    lsp_completion_schema = lsp_completion["requestBody"]["content"]["application/json"]["schema"]
    assert lsp_completion_schema["required"] == ["text", "line", "character"]
    assert lsp_completion_schema["properties"]["offset"]["minimum"] == 0
    assert lsp_completion_schema["properties"]["project_path"]["type"] == "string"
    assert lsp_completion_schema["properties"]["game_root"]["type"] == "string"
    lsp_semantic_tokens = seed["paths"]["/lsp/semantic-tokens"]["post"]
    assert lsp_semantic_tokens["requestBody"]["required"] is True
    lsp_semantic_tokens_schema = lsp_semantic_tokens["requestBody"]["content"]["application/json"]["schema"]
    assert lsp_semantic_tokens_schema["required"] == ["text"]
    assert lsp_semantic_tokens_schema["properties"]["path"]["type"] == "string"
    lsp_keywords = seed["paths"]["/lsp/keywords"]["get"]
    lsp_keywords_params = {param["name"]: param for param in lsp_keywords["parameters"]}
    assert lsp_keywords_params["game_root"]["required"] is False
    assert lsp_keywords_params["game_root"]["schema"]["type"] == "string"
    find_params = {param["name"]: param for param in seed["paths"]["/projects/find"]["get"]["parameters"]}
    assert find_params["path"]["required"] is False
    rename_params = {param["name"]: param for param in seed["paths"]["/projects/rename"]["patch"]["parameters"]}
    assert rename_params["title"]["required"] is True
    language_params = {param["name"]: param for param in seed["paths"]["/projects/language"]["patch"]["parameters"]}
    assert language_params["preferred_language"]["required"] is True
    assert language_params["preferred_language"]["schema"]["enum"] == [
        "en",
        "fr",
        "de",
        "ru",
        "es",
        "pl",
        "pt_br",
        "zh",
        "ja",
        "ko",
    ]
    assert language_params["write"]["schema"]["default"] is False
    assert language_params["plan_hash"]["required"] is False
    module_rename_params = {param["name"]: param for param in seed["paths"]["/projects/modules/rename"]["patch"]["parameters"]}
    assert module_rename_params["module_id"]["required"] is True
    assert module_rename_params["object_id"]["required"] is True
    assert module_rename_params["title"]["required"] is False
    module_remove = seed["paths"]["/projects/modules/remove"]["delete"]
    module_remove_params = {param["name"]: param for param in module_remove["parameters"]}
    assert module_remove_params["module_id"]["required"] is True
    assert module_remove_params["write"]["schema"]["default"] is False
    module_file_params = {param["name"]: param for param in seed["paths"]["/projects/modules/file"]["get"]["parameters"]}
    assert module_file_params["module_id"]["required"] is True
    assert module_file_params["relative_path"]["required"] is True
    module_edit_params = {param["name"]: param for param in seed["paths"]["/projects/modules/file"]["patch"]["parameters"]}
    assert module_edit_params["relative_path"]["required"] is True
    assert seed["paths"]["/projects/modules/file"]["patch"]["requestBody"]["required"] is True
    collection_file_params = {param["name"]: param for param in seed["paths"]["/projects/collections/file"]["get"]["parameters"]}
    assert collection_file_params["collection_id"]["required"] is True
    assert collection_file_params["relative_path"]["required"] is True
    collection_edit_params = {param["name"]: param for param in seed["paths"]["/projects/collections/file"]["patch"]["parameters"]}
    assert collection_edit_params["relative_path"]["required"] is True
    assert seed["paths"]["/projects/collections/file"]["patch"]["requestBody"]["required"] is True
    collection_create = seed["paths"]["/projects/collections"]["post"]
    collection_create_params = {param["name"]: param for param in collection_create["parameters"]}
    assert collection_create_params["family"]["required"] is True
    assert collection_create_params["collection_id"]["required"] is True
    assert collection_create_params["write"]["schema"]["default"] is False
    assert collection_create["requestBody"]["required"] is False
    collection_remove = seed["paths"]["/projects/collections"]["delete"]
    collection_remove_params = {param["name"]: param for param in collection_remove["parameters"]}
    assert collection_remove_params["collection_id"]["required"] is True
    assert collection_remove_params["family"]["required"] is False
    assert collection_remove_params["write"]["schema"]["default"] is False
    assert collection_remove_params["plan_hash"]["required"] is False
    assert collection_remove["responses"]["200"]["description"] == "Collection remove payload."
    collection_rename = seed["paths"]["/projects/collections/rename"]["patch"]
    collection_rename_params = {param["name"]: param for param in collection_rename["parameters"]}
    assert collection_rename_params["collection_id"]["required"] is True
    assert collection_rename_params["target_id"]["required"] is True
    assert collection_rename_params["family"]["required"] is False
    assert collection_rename["responses"]["200"]["description"] == "Collection rename payload."
    json.dumps(seed)


def test_rest_api_table_lists_openapi_routes() -> None:
    from typing_extensions import is_typeddict

    from paradev.surfaces.rest import (
        REST_API_TABLE_SCHEMA,
        RestApiRow,
        RestApiTable,
        get_openapi_seed,
        get_rest_api_table,
        render_rest_api_reference_markdown,
    )

    seed = get_openapi_seed()
    table = get_rest_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_rest_api_reference_markdown()

    assert is_typeddict(RestApiRow)
    assert is_typeddict(RestApiTable)
    assert table["schema"] == REST_API_TABLE_SCHEMA
    assert table["row_count"] == 84 == len(rows)
    assert table["row_count"] == sum(1 for path_item in seed["paths"].values() for method in ("get", "post", "put", "patch", "delete") if method in path_item)
    assert set(RestApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "feature",
        "method",
        "path",
        "inputs",
        "required_inputs",
        "returns",
        "raises",
        "registry_seam",
        "surface",
        "frontend_operation_ids",
        "doc_page",
        "test_anchor",
    }
    assert set(RestApiTable.__annotations__) == {
        "schema",
        "row_count",
        "method_index",
        "feature_index",
        "frontend_operation_index",
        "rows",
    }
    assert table["method_index"]["GET"][0] == "GET /health"
    assert len(table["method_index"]["GET"]) == 37
    assert len(table["method_index"]["POST"]) == 34
    assert len(table["method_index"]["PUT"]) == 4
    assert len(table["method_index"]["DELETE"]) == 3
    assert table["feature_index"]["api-catalog"] == ["GET /api-catalog"]
    assert table["feature_index"]["rest"] == ["GET /rest-api"]
    assert table["feature_index"]["cli"] == ["GET /cli-api"]
    assert table["feature_index"]["surface-contracts"] == ["GET /surface-contracts"]
    assert row_by_symbol["POST /desktop/import-project-package"]["returns"] == ("200 Desktop project-package installation payload or null.")
    assert row_by_symbol["POST /projects/collections/scaffold"] == {
        "symbol": "POST /projects/collections/scaffold",
        "kind": "REST route",
        "layer": "rest",
        "feature": "collections",
        "method": "POST",
        "path": "/projects/collections/scaffold",
        "inputs": ("query:path, query:template_id, query:collection_id, " "query:source_root, query:write, query:force, query:plan_hash, body"),
        "required_inputs": "query:template_id, query:collection_id",
        "returns": "200 Guarded collection scaffold plan or apply payload.",
        "raises": "",
        "registry_seam": "OpenAPI path /projects/collections/scaffold",
        "surface": "rest",
        "frontend_operation_ids": ["collection.scaffold"],
        "doc_page": "docs/user-manual/rest-api-reference.md",
        "test_anchor": ("tests/test_architecture.py::test_rest_api_table_lists_openapi_routes"),
    }
    assert table["feature_index"]["catalog"] == [
        "GET /catalog-api",
        "GET /projects/catalog",
        "POST /projects/catalog",
        "PUT /projects/catalog",
    ]
    assert table["feature_index"]["desktop"] == [
        "GET /desktop/state",
        "GET /desktop/builds",
        "POST /desktop/builds",
        "GET /desktop/builds/status",
        "POST /desktop/builds/interrupt",
        "POST /desktop/open-path",
        "POST /desktop/select-project",
        "POST /desktop/import-project-package",
        "GET /desktop/path-status",
        "GET /desktop/hoi4-launch-readiness",
        "GET /desktop/app-config",
        "PUT /desktop/app-config",
        "GET /desktop/config-value",
        "PUT /desktop/config-value",
        "POST /desktop/llm/test",
        "POST /desktop/ai/chat",
        "GET /desktop/ai/profiles",
        "PUT /desktop/ai/profiles/{profile_id}",
        "DELETE /desktop/ai/profiles/{profile_id}",
    ]
    assert "GET /projects/inspect" in table["feature_index"]["inspections"]
    assert row_by_symbol["POST /projects/{project_id}/sources/form"]["frontend_operation_ids"] == ["project.source_form"]
    assert row_by_symbol["POST /projects/{project_id}/localization/workspace"]["frontend_operation_ids"] == ["localization.workspace"]
    assert row_by_symbol["POST /projects/{project_id}/localization/workspace"]["required_inputs"] == ("path:project_id, body")
    assert row_by_symbol["POST /projects/{project_id}/localization/plan"]["frontend_operation_ids"] == ["localization.plan"]
    assert row_by_symbol["GET /frontend-api"]["inputs"] == "query:operation_id, query:group_id, query:form, query:index_name, query:key"
    assert row_by_symbol["GET /frontend-api"]["required_inputs"] == "none"
    assert row_by_symbol["GET /api-catalog"]["inputs"] == "query:reference_id, query:index_name, query:key"
    assert row_by_symbol["GET /api-catalog"]["required_inputs"] == "none"
    assert row_by_symbol["GET /api-catalog"]["raises"] == "400 Invalid API catalog selector."
    assert row_by_symbol["GET /rest-api"]["feature"] == "rest"
    assert row_by_symbol["GET /rest-api"]["inputs"] == "query:symbol, query:index_name, query:key"
    assert row_by_symbol["GET /rest-api"]["required_inputs"] == "none"
    assert row_by_symbol["GET /rest-api"]["returns"] == "200 REST API table, row, or index lookup payload."
    assert row_by_symbol["GET /rest-api"]["raises"] == "400 Invalid REST API selector."
    assert row_by_symbol["GET /cli-api"]["feature"] == "cli"
    assert row_by_symbol["GET /cli-api"]["inputs"] == "query:symbol, query:index_name, query:key"
    assert row_by_symbol["GET /cli-api"]["required_inputs"] == "none"
    assert row_by_symbol["GET /cli-api"]["returns"] == "200 CLI API table, row, or index lookup payload."
    assert row_by_symbol["GET /cli-api"]["raises"] == "400 Invalid CLI API selector."
    assert row_by_symbol["GET /catalog-api"]["feature"] == "catalog"
    assert row_by_symbol["GET /catalog-api"]["inputs"] == "query:symbol, query:index_name, query:key"
    assert row_by_symbol["GET /catalog-api"]["required_inputs"] == "none"
    assert row_by_symbol["GET /catalog-api"]["returns"] == "200 Catalog API table, row, or index lookup payload."
    assert row_by_symbol["GET /catalog-api"]["raises"] == "400 Invalid catalog API selector."
    assert row_by_symbol["GET /desktop/builds"]["inputs"] == "query:project_root"
    assert row_by_symbol["GET /desktop/builds"]["required_inputs"] == "none"
    assert row_by_symbol["GET /desktop/builds"]["returns"] == "200 Desktop build-runs payload."
    assert row_by_symbol["GET /desktop/builds"]["frontend_operation_ids"] == ["build.runs"]
    assert row_by_symbol["POST /desktop/builds"]["inputs"] == "body"
    assert row_by_symbol["POST /desktop/builds"]["required_inputs"] == "body"
    assert row_by_symbol["POST /desktop/builds"]["returns"] == "200 Desktop build run payload."
    assert row_by_symbol["POST /desktop/builds"]["frontend_operation_ids"] == ["build.start"]
    assert row_by_symbol["GET /desktop/builds/status"]["inputs"] == "query:run_id"
    assert row_by_symbol["GET /desktop/builds/status"]["required_inputs"] == "query:run_id"
    assert row_by_symbol["GET /desktop/builds/status"]["returns"] == "200 Desktop build run payload."
    assert row_by_symbol["GET /desktop/builds/status"]["frontend_operation_ids"] == ["build.status"]
    assert row_by_symbol["POST /desktop/builds/interrupt"]["inputs"] == "body"
    assert row_by_symbol["POST /desktop/builds/interrupt"]["required_inputs"] == "body"
    assert row_by_symbol["POST /desktop/builds/interrupt"]["returns"] == "200 Desktop build run payload."
    assert row_by_symbol["POST /desktop/builds/interrupt"]["frontend_operation_ids"] == ["build.interrupt"]
    assert row_by_symbol["GET /desktop/path-status"]["inputs"] == "query:path"
    assert row_by_symbol["GET /desktop/path-status"]["required_inputs"] == "query:path"
    assert row_by_symbol["GET /desktop/path-status"]["returns"] == "200 Desktop path status payload."
    assert row_by_symbol["GET /desktop/hoi4-launch-readiness"]["inputs"] == "query:project_root"
    assert row_by_symbol["GET /desktop/hoi4-launch-readiness"]["required_inputs"] == "query:project_root"
    assert row_by_symbol["GET /desktop/hoi4-launch-readiness"]["returns"] == "200 Desktop HOI4 launch-readiness payload."
    assert row_by_symbol["POST /desktop/open-path"]["inputs"] == "body"
    assert row_by_symbol["POST /desktop/open-path"]["required_inputs"] == "body"
    assert row_by_symbol["POST /desktop/open-path"]["returns"] == "200 Desktop open-path payload."
    assert row_by_symbol["POST /desktop/select-project"]["required_inputs"] == "none"
    assert row_by_symbol["POST /desktop/select-project"]["returns"] == "200 Desktop project-selection payload."
    assert row_by_symbol["GET /desktop/app-config"]["required_inputs"] == "none"
    assert row_by_symbol["GET /desktop/app-config"]["returns"] == "200 Desktop app config payload."
    assert row_by_symbol["PUT /desktop/app-config"]["required_inputs"] == "body"
    assert row_by_symbol["PUT /desktop/app-config"]["returns"] == "200 Desktop app config write status."
    assert row_by_symbol["GET /desktop/config-value"]["inputs"] == "query:key"
    assert row_by_symbol["GET /desktop/config-value"]["required_inputs"] == "query:key"
    assert row_by_symbol["GET /desktop/config-value"]["returns"] == "200 Desktop config value payload."
    assert row_by_symbol["PUT /desktop/config-value"]["required_inputs"] == "body"
    assert row_by_symbol["PUT /desktop/config-value"]["returns"] == "200 Desktop config value payload."
    assert row_by_symbol["POST /desktop/llm/test"]["required_inputs"] == "body"
    assert row_by_symbol["POST /desktop/llm/test"]["returns"] == "200 Desktop LLM route test payload."
    assert row_by_symbol["GET /lsp-api"]["feature"] == "lsp"
    assert row_by_symbol["GET /lsp-api"]["inputs"] == "query:symbol, query:index_name, query:key"
    assert row_by_symbol["GET /lsp-api"]["required_inputs"] == "none"
    assert row_by_symbol["GET /lsp-api"]["returns"] == "200 LSP API table, row, or index lookup payload."
    assert row_by_symbol["GET /lsp-api"]["raises"] == "400 Invalid LSP API selector."
    assert row_by_symbol["GET /surface-contracts"]["inputs"] == "query:identifier, query:status"
    assert row_by_symbol["GET /surface-contracts"]["required_inputs"] == "none"
    assert row_by_symbol["GET /surface-contracts"]["raises"] == "400 Invalid surface contract selector."
    assert row_by_symbol["POST /frontend-api/options"]["required_inputs"] == "query:operation_id, query:field_name"
    assert row_by_symbol["POST /projects/modules/create-batch"]["required_inputs"] == "body"
    assert row_by_symbol["POST /projects/modules/create-batch"]["frontend_operation_ids"] == ["module.create_batch"]
    assert row_by_symbol["POST /projects/modules/metadata/clean"]["required_inputs"] == "body"
    assert row_by_symbol["POST /projects/modules/metadata/clean"]["feature"] == "modules"
    assert row_by_symbol["POST /projects/modules/metadata/clean"]["frontend_operation_ids"] == ["module.metadata.clean"]
    assert row_by_symbol["POST /projects/modules/collection"]["required_inputs"] == "body"
    assert row_by_symbol["POST /projects/modules/collection"]["feature"] == "modules"
    assert row_by_symbol["POST /projects/modules/collection"]["frontend_operation_ids"] == ["module.collection.set"]
    assert row_by_symbol["POST /projects/modules/activity"]["required_inputs"] == "body"
    assert row_by_symbol["POST /projects/modules/activity"]["feature"] == "modules"
    assert row_by_symbol["POST /projects/modules/activity"]["frontend_operation_ids"] == ["module.activity.set"]
    assert row_by_symbol["GET /projects/modules/diagram"]["frontend_operation_ids"] == ["module.diagram"]
    assert row_by_symbol["POST /projects/modules/diagram/edit"]["frontend_operation_ids"] == ["module.diagram.edit"]
    assert row_by_symbol["PATCH /projects/modules/file"]["required_inputs"] == "query:module_id, query:relative_path, body"
    assert row_by_symbol["GET /projects/catalog"]["inputs"] == "query:path"
    assert row_by_symbol["GET /projects/catalog"]["required_inputs"] == "none"
    assert row_by_symbol["GET /projects/catalog"]["returns"] == "200 Catalog status payload."
    assert row_by_symbol["GET /projects/catalog"]["frontend_operation_ids"] == []
    assert row_by_symbol["POST /projects/catalog"]["frontend_operation_ids"] == ["catalog.write"]
    assert row_by_symbol["POST /desktop/ai/chat"]["frontend_operation_ids"] == ["ai.chat"]
    assert row_by_symbol["POST /desktop/ai/chat"]["required_inputs"] == "body"
    assert row_by_symbol["GET /desktop/ai/profiles"]["frontend_operation_ids"] == ["ai.profiles"]
    assert row_by_symbol["GET /desktop/ai/profiles"]["required_inputs"] == "none"
    assert row_by_symbol["GET /desktop/ai/profiles"]["returns"] == "200 Desktop AI chat profile payload."
    assert row_by_symbol["PUT /desktop/ai/profiles/{profile_id}"]["frontend_operation_ids"] == ["ai.profile.write"]
    assert row_by_symbol["PUT /desktop/ai/profiles/{profile_id}"]["required_inputs"] == "path:profile_id, body"
    assert row_by_symbol["PUT /desktop/ai/profiles/{profile_id}"]["returns"] == "200 Desktop AI chat profile payload."
    assert row_by_symbol["DELETE /desktop/ai/profiles/{profile_id}"]["frontend_operation_ids"] == ["ai.profile.reset"]
    assert row_by_symbol["DELETE /desktop/ai/profiles/{profile_id}"]["required_inputs"] == "path:profile_id"
    assert row_by_symbol["DELETE /desktop/ai/profiles/{profile_id}"]["inputs"] == "path:profile_id, query:project_root"
    assert row_by_symbol["DELETE /desktop/ai/profiles/{profile_id}"]["returns"] == "200 Desktop AI chat profile payload."
    assert "catalog.query" in row_by_symbol["GET /projects/inspect"]["frontend_operation_ids"]
    assert table["frontend_operation_index"]["catalog.write"] == ["POST /projects/catalog"]
    assert table["frontend_operation_index"]["build.start"] == ["POST /desktop/builds"]
    assert table["frontend_operation_index"]["build.runs"] == ["GET /desktop/builds"]
    assert table["frontend_operation_index"]["build.status"] == ["GET /desktop/builds/status"]
    assert table["frontend_operation_index"]["build.interrupt"] == ["POST /desktop/builds/interrupt"]
    assert table["frontend_operation_index"]["ai.chat"] == ["POST /desktop/ai/chat"]
    assert table["frontend_operation_index"]["ai.profiles"] == ["GET /desktop/ai/profiles"]
    assert table["frontend_operation_index"]["ai.profile.write"] == ["PUT /desktop/ai/profiles/{profile_id}"]
    assert table["frontend_operation_index"]["ai.profile.reset"] == ["DELETE /desktop/ai/profiles/{profile_id}"]
    assert table["frontend_operation_index"]["module.create_batch"] == ["POST /projects/modules/create-batch"]
    assert table["frontend_operation_index"]["module.diagram"] == ["GET /projects/modules/diagram"]
    assert table["frontend_operation_index"]["module.diagram.edit"] == ["POST /projects/modules/diagram/edit"]
    assert table["frontend_operation_index"]["project.inspect"] == ["GET /projects/inspect"]
    assert row_by_symbol["PATCH /projects/modules/file"]["raises"] == ""
    assert row_by_symbol["GET /projects/{project_id}/sources"]["raises"] == "400 Invalid project or source path."
    assert reference.startswith("# REST API Reference\n")
    assert "Generated from `paradev.surfaces.rest.get_rest_api_table()`." in reference
    assert "| `GET` | 37 | `GET /health`, `GET /api-catalog`, `GET /rest-api`, `GET /cli-api`," in reference
    assert "| `lsp` | 8 | `GET /lsp-api`, `POST /lsp/diagnostics`, `POST /lsp/symbols`," in reference
    assert "| `POST` | 34 | `POST /frontend-api/normalize`, `POST /frontend-api/rest-request`," in reference
    assert (
        "| `PUT` | 4 | `PUT /projects/catalog`, `PUT /desktop/app-config`, `PUT /desktop/config-value`, " "`PUT /desktop/ai/profiles/{profile_id}` |"
    ) in reference
    assert ("| `DELETE` | 3 | `DELETE /desktop/ai/profiles/{profile_id}`, " "`DELETE /projects/modules/remove`, `DELETE /projects/collections` |") in reference
    assert "| `api-catalog` | 1 | `GET /api-catalog` |" in reference
    assert "| `rest` | 1 | `GET /rest-api` |" in reference
    assert "| `cli` | 1 | `GET /cli-api` |" in reference
    assert "| `surface-contracts` | 1 | `GET /surface-contracts` |" in reference
    assert "| `catalog` | 4 | `GET /catalog-api`, `GET /projects/catalog`, `POST /projects/catalog`, `PUT /projects/catalog` |" in reference
    assert (
        "| `desktop` | 19 | `GET /desktop/state`, `GET /desktop/builds`, `POST /desktop/builds`, `GET /desktop/builds/status`, "
        "`POST /desktop/builds/interrupt`, `POST /desktop/open-path`, `POST /desktop/select-project`, `POST /desktop/import-project-package`, `GET /desktop/path-status`, `GET /desktop/hoi4-launch-readiness`, `GET /desktop/app-config`, `PUT /desktop/app-config`, "
        "`GET /desktop/config-value`, `PUT /desktop/config-value`, `POST /desktop/llm/test`, `POST /desktop/ai/chat`, `GET /desktop/ai/profiles`, "
        "`PUT /desktop/ai/profiles/{profile_id}`, `DELETE /desktop/ai/profiles/{profile_id}` |"
    ) in reference
    assert "| `catalog.write` | 1 | `POST /projects/catalog` |" in reference
    assert "| `build.start` | 1 | `POST /desktop/builds` |" in reference
    assert "| `build.runs` | 1 | `GET /desktop/builds` |" in reference
    assert "| `build.status` | 1 | `GET /desktop/builds/status` |" in reference
    assert "| `build.interrupt` | 1 | `POST /desktop/builds/interrupt` |" in reference
    assert "| `ai.profiles` | 1 | `GET /desktop/ai/profiles` |" in reference
    assert "| `ai.profile.write` | 1 | `PUT /desktop/ai/profiles/{profile_id}` |" in reference
    assert "| `ai.profile.reset` | 1 | `DELETE /desktop/ai/profiles/{profile_id}` |" in reference
    assert "| `ai.chat` | 1 | `POST /desktop/ai/chat` |" in reference
    assert (
        "| `GET /api-catalog` | `REST route` | `rest` | `api-catalog` | `GET` | `/api-catalog` | "
        "`query:reference_id, query:index_name, query:key` | `none` | "
        "`200 API catalog table, row, or index lookup payload.` | `400 Invalid API catalog selector.` |"
    ) in reference
    assert (
        "| `GET /rest-api` | `REST route` | `rest` | `rest` | `GET` | `/rest-api` | "
        "`query:symbol, query:index_name, query:key` | `none` | "
        "`200 REST API table, row, or index lookup payload.` | `400 Invalid REST API selector.` |"
    ) in reference
    assert (
        "| `GET /cli-api` | `REST route` | `rest` | `cli` | `GET` | `/cli-api` | "
        "`query:symbol, query:index_name, query:key` | `none` | "
        "`200 CLI API table, row, or index lookup payload.` | `400 Invalid CLI API selector.` |"
    ) in reference
    assert (
        "| `GET /catalog-api` | `REST route` | `rest` | `catalog` | `GET` | `/catalog-api` | "
        "`query:symbol, query:index_name, query:key` | `none` | "
        "`200 Catalog API table, row, or index lookup payload.` | `400 Invalid catalog API selector.` |"
    ) in reference
    assert (
        "| `GET /surface-contracts` | `REST route` | `rest` | `surface-contracts` | `GET` | `/surface-contracts` | "
        "`query:identifier, query:status` | `none` | "
        "`200 Surface contract summary, contract payload, or status id list.` | `400 Invalid surface contract selector.` |"
    ) in reference
    assert (
        "| `PATCH /projects/modules/file` | `REST route` | `rest` | `modules` | `PATCH` | "
        "`/projects/modules/file` | `query:path, query:module_id, query:relative_path, query:source_root, "
        "query:create, query:encoding, body` | `query:module_id, query:relative_path, body` | "
        "`200 Module file payload.` |  | `module.edit` |"
    ) in reference
    manual = Path("docs/user-manual/rest-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_rest_api_table()["rows"][0]["symbol"] == "GET /health"
    table["frontend_operation_index"]["catalog.write"].append("GET /health")
    assert get_rest_api_table()["frontend_operation_index"]["catalog.write"] == ["POST /projects/catalog"]


def test_rest_facade_api_table_lists_public_api_facade() -> None:
    from typing_extensions import is_typeddict

    import paradev.api as api
    from paradev.api import (
        REST_FACADE_API_TABLE_SCHEMA,
        RestFacadeApiRow,
        RestFacadeApiTable,
        get_rest_facade_api_table,
        render_rest_facade_api_reference_markdown,
    )

    table = get_rest_facade_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_rest_facade_api_reference_markdown()

    assert is_typeddict(RestFacadeApiRow)
    assert is_typeddict(RestFacadeApiTable)
    assert table["schema"] == REST_FACADE_API_TABLE_SCHEMA
    assert table["row_count"] == len(rows) == 13
    assert [row["symbol"] for row in rows] == list(api.__all__)
    assert set(RestFacadeApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "module",
        "feature",
        "import_path",
        "returns",
        "value",
        "registry_seam",
        "surface",
        "doc_page",
        "test_anchor",
    }
    assert set(RestFacadeApiTable.__annotations__) == {
        "schema",
        "row_count",
        "module_index",
        "feature_index",
        "kind_index",
        "rows",
    }
    assert table["module_index"] == {
        "rest": [
            "apply_project_draft",
            "build_app",
            "create_module_batch",
            "create_module_draft",
            "get_openapi_seed",
            "read_project_source",
            "read_project_source_form",
        ],
        "api": [
            "REST_FACADE_API_TABLE_SCHEMA",
            "RestFacadeApiRow",
            "RestFacadeApiTable",
            "get_rest_facade_api_selection",
            "get_rest_facade_api_table",
            "render_rest_facade_api_reference_markdown",
        ],
    }
    assert table["feature_index"] == {
        "project-drafts": ["apply_project_draft"],
        "server": ["build_app"],
        "module-batches": ["create_module_batch"],
        "module-drafts": ["create_module_draft"],
        "openapi": ["get_openapi_seed"],
        "project-sources": ["read_project_source", "read_project_source_form"],
        "rest-facade-api": [
            "REST_FACADE_API_TABLE_SCHEMA",
            "RestFacadeApiRow",
            "RestFacadeApiTable",
            "get_rest_facade_api_selection",
            "get_rest_facade_api_table",
            "render_rest_facade_api_reference_markdown",
        ],
    }
    assert table["kind_index"] == {
        "function": [
            "apply_project_draft",
            "build_app",
            "create_module_batch",
            "create_module_draft",
            "get_openapi_seed",
            "read_project_source",
            "read_project_source_form",
            "get_rest_facade_api_selection",
            "get_rest_facade_api_table",
            "render_rest_facade_api_reference_markdown",
        ],
        "schema constant": ["REST_FACADE_API_TABLE_SCHEMA"],
        "TypedDict": ["RestFacadeApiRow", "RestFacadeApiTable"],
    }
    assert row_by_symbol["apply_project_draft"]["registry_seam"] == "REST project draft bridge"
    assert row_by_symbol["build_app"]["returns"] == "FastAPI app"
    assert row_by_symbol["create_module_batch"]["registry_seam"] == "REST module batch bridge"
    assert row_by_symbol["create_module_draft"]["registry_seam"] == "REST module draft bridge"
    assert row_by_symbol["get_openapi_seed"]["registry_seam"] == "OpenAPI seed contract"
    assert row_by_symbol["read_project_source"]["registry_seam"] == "REST project source bridge"
    assert row_by_symbol["read_project_source_form"]["registry_seam"] == "REST project source bridge"
    assert row_by_symbol["REST_FACADE_API_TABLE_SCHEMA"]["value"] == REST_FACADE_API_TABLE_SCHEMA
    assert row_by_symbol["get_rest_facade_api_table"]["returns"] == "RestFacadeApiTable"
    assert reference.startswith("# REST Facade API Reference\n")
    assert "Generated from `paradev.api.get_rest_facade_api_table()`." in reference
    assert (
        "| `rest` | 7 | `apply_project_draft`, `build_app`, `create_module_batch`, `create_module_draft`, `get_openapi_seed`, "
        "`read_project_source`, `read_project_source_form` |" in reference
    )
    assert (
        "| `rest-facade-api` | 6 | `REST_FACADE_API_TABLE_SCHEMA`, `RestFacadeApiRow`, `RestFacadeApiTable`, "
        "`get_rest_facade_api_selection`, `get_rest_facade_api_table`, `render_rest_facade_api_reference_markdown` |"
    ) in reference
    assert "| `server` | 1 | `build_app` |" in reference
    assert ("| `build_app` | `function` | `rest` | `rest` | `server` | `paradev.api.build_app` | " "`FastAPI app` |  | `FastAPI app factory` |") in reference
    manual = Path("docs/user-manual/rest-facade-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_rest_facade_api_table()["rows"][0]["symbol"] == "apply_project_draft"
    table["module_index"]["api"].append("changed")
    assert get_rest_facade_api_table()["module_index"]["api"] == [
        "REST_FACADE_API_TABLE_SCHEMA",
        "RestFacadeApiRow",
        "RestFacadeApiTable",
        "get_rest_facade_api_selection",
        "get_rest_facade_api_table",
        "render_rest_facade_api_reference_markdown",
    ]


def test_rest_create_module_draft_uses_sdk_family_resolution(tmp_path: Path) -> None:
    from paradev.sdk import Project
    from paradev.surfaces.rest import create_module_draft

    project = Project.create(tmp_path / "starter", title="Starter")

    payload = create_module_draft(
        project_id=project.project_id,
        family_id="ideas",
        request={
            "project_root": str(project.root),
            "object_id": "GER_industry_spirit",
            "values": {
                "title": "German Industry Spirit",
                "description": "Industrial production spirit.",
            },
        },
    )

    plan = payload["plan"]

    assert payload["schema"] == "paradev.rest.module_draft.v1"
    assert payload["project_id"] == "starter"
    assert payload["family_id"] == "ideas"
    assert payload["draft_id"] == "ideas:GER_industry_spirit"
    assert plan["template_id"] == "hoi4:idea/basic"
    assert plan["written"] is False
    assert plan["blocked"] is False
    assert plan["module_id"] == "idea/GER_industry_spirit"


def test_rest_create_module_draft_returns_blocked_write_payload(tmp_path: Path) -> None:
    from paradev.sdk import Project
    from paradev.surfaces.rest import create_module_draft

    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module(
        "idea",
        "GER_industry_spirit",
        values={"title": "German Industry Spirit"},
        write=True,
    )

    payload = create_module_draft(
        project_id=project.project_id,
        family_id="ideas",
        request={
            "project_root": str(project.root),
            "object_id": "GER_industry_spirit",
            "values": {"title": "German Industry Spirit"},
            "write": True,
        },
    )

    assert payload["schema"] == "paradev.rest.module_draft.v1"
    assert payload["draft_id"] == "ideas:GER_industry_spirit"
    assert payload["plan"]["blocked"] is True
    assert payload["plan"]["written"] is False
    assert payload["plan"]["diagnostics"][0]["code"] == "scaffold.file_exists"
    assert {file["action"] for file in payload["plan"]["files"]} == {"exists"}


def test_rest_read_project_source_returns_browser_source_text(tmp_path: Path) -> None:
    from paradev.sdk import Project
    from paradev.surfaces.rest import read_project_source

    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module(
        "idea",
        "GER_industry_spirit",
        values={"title": "German Industry Spirit"},
        write=True,
    )
    browser = Project.load(project.root).browser(family="ideas")
    source = next(row for row in browser["items"][0]["sources"] if row["slot"] == "def")

    payload = read_project_source(
        project_id=project.project_id,
        project_root=str(project.root),
        source_path=source["path"],
    )

    assert payload["schema"] == "paradev.rest.source_text.v1"
    assert payload["project_id"] == "starter"
    assert payload["path"] == source["path"]
    assert payload["relative_path"] == source["relative_path"]
    assert payload["size"] == source["size"]
    assert payload["mtime_ns"] == source["mtime_ns"]
    assert "GER_industry_spirit" in payload["text"]


def test_rest_apply_project_draft_writes_validated_project_text(tmp_path: Path) -> None:
    from paradev.sdk import Project
    from paradev.surfaces.rest import apply_project_draft

    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module(
        "idea",
        "GER_industry_spirit",
        values={"title": "German Industry Spirit"},
        write=True,
    )
    source_path = "src/modules/idea/GER_industry_spirit/def.txt"
    edited = "ideas = {\n\tcountry = {\n\t\tGER_industry_spirit = {}\n\t}\n}\n"

    payload = apply_project_draft(
        project_id=project.project_id,
        request={
            "project_root": str(project.root),
            "source_edits": [{"path": source_path, "text": edited}],
        },
    )

    assert payload["schema"] == "paradev.rest.draft_apply.v1"
    assert payload["written"] is True
    assert payload["files"] == [
        {
            "path": str(project.root / source_path),
            "relative_path": source_path,
            "operation": "write_text",
            "encoding": "utf-8",
        }
    ]
    assert (project.root / source_path).read_text(encoding="utf-8") == edited

    with pytest.raises(ValueError, match="unsupported fields"):
        apply_project_draft(
            project_id=project.project_id,
            request={
                "project_root": str(project.root),
                "source_edits": [{"path": source_path, "text": "stale overwrite"}],
                "sourceEdits": [],
            },
        )
    assert (project.root / source_path).read_text(encoding="utf-8") == edited


def test_rest_apply_project_draft_commits_source_and_module_rename(
    tmp_path: Path,
) -> None:
    from paradev.sdk import Project
    from paradev.surfaces.rest import apply_project_draft

    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module(
        "idea",
        "IDEA_ALPHA",
        values={"title": "Alpha"},
        write=True,
    )
    previous_root = project.root / "src/modules/idea/IDEA_ALPHA"
    localization = previous_root / "main.loc"

    payload = apply_project_draft(
        project_id=project.project_id,
        request={
            "project_root": str(project.root),
            "source_edits": [
                {
                    "path": str(localization),
                    "text": "[en.IDEA_ALPHA]\nReadable Alpha\n",
                }
            ],
            "module_rename": {
                "module_id": "idea/IDEA_ALPHA",
                "object_id": "IDEA_ALPHA",
                "title": "Readable Alpha",
            },
        },
    )

    renamed_root = project.root / "src/modules/idea/IDEA_ALPHA - Readable Alpha"
    assert payload["module_rename"]["root"] == str(renamed_root)
    assert not previous_root.exists()
    assert (renamed_root / "main.loc").read_text(encoding="utf-8") == ("[en.IDEA_ALPHA]\nReadable Alpha\n")


def test_rest_apply_project_draft_can_write_new_png_replacements(
    tmp_path: Path,
) -> None:
    from paradev.sdk import Project
    from paradev.surfaces.rest import apply_project_draft

    project = Project.create(tmp_path / "starter", title="Starter")
    project.scaffold_module(
        "idea",
        "GER_industry_spirit",
        values={"title": "German Industry Spirit"},
        write=True,
    )
    source_path = "src/modules/idea/GER_industry_spirit/icon.png"

    payload = apply_project_draft(
        project_id=project.project_id,
        request={
            "project_root": str(project.root),
            "source_replacements": [
                {
                    "path": source_path,
                    "content_base64": "cG5nLWJ5dGVz",
                    "expected_absent": True,
                }
            ],
        },
    )

    assert payload["schema"] == "paradev.rest.draft_apply.v1"
    assert payload["written"] is True
    assert payload["files"] == [
        {
            "path": str(project.root / source_path),
            "relative_path": source_path,
            "operation": "replace_bytes",
        }
    ]
    assert (project.root / source_path).read_bytes() == b"png-bytes"


def test_openapi_seed_links_rest_operations_to_frontend_api_rows() -> None:
    from paradev.sdk import get_frontend_api_contract
    from paradev.surfaces.rest import get_openapi_seed

    seed = get_openapi_seed()
    contract = get_frontend_api_contract()

    expected: dict[tuple[str, str], list[str]] = {}
    for row in contract["operations"]:
        bindings = row.get("bindings", {})
        rest = bindings.get("rest") if isinstance(bindings, dict) else None
        if isinstance(rest, dict):
            key = (str(rest["path"]), str(rest["method"]).lower())
            expected.setdefault(key, []).append(str(row["id"]))

    assert expected[("/projects", "get")] == ["project.open", "project.view"]
    assert expected[("/projects/list", "get")] == ["project.list"]
    assert expected[("/desktop/state", "get")] == ["project.state"]
    assert expected[("/desktop/ai/chat", "post")] == ["ai.chat"]
    assert expected[("/desktop/ai/profiles", "get")] == ["ai.profiles"]
    assert expected[("/desktop/ai/profiles/{profile_id}", "put")] == ["ai.profile.write"]
    assert expected[("/desktop/builds", "get")] == ["build.runs"]
    assert expected[("/desktop/builds", "post")] == ["build.start"]
    assert expected[("/desktop/builds/status", "get")] == ["build.status"]
    assert expected[("/desktop/builds/interrupt", "post")] == ["build.interrupt"]
    assert expected[("/projects/browser", "get")] == ["project.browser"]
    assert expected[("/projects/templates", "get")] == ["module.templates"]
    assert expected[("/projects/modules/create-batch", "post")] == ["module.create_batch"]
    assert expected[("/projects/modules/duplicate", "post")] == ["module.duplicate"]
    assert expected[("/projects/modules/collection", "post")] == ["module.collection.set"]
    assert expected[("/projects/modules/metadata/clean", "post")] == ["module.metadata.clean"]
    assert expected[("/projects/catalog", "post")] == ["catalog.write"]
    assert expected[("/projects/catalog", "put")] == ["catalog.refresh"]
    assert expected[("/projects/collections/rename", "patch")] == ["collection.rename"]
    assert expected[("/projects/collections", "delete")] == ["collection.remove"]
    assert "module.list" in expected[("/projects/inspect", "get")]
    assert "build.assets" in expected[("/projects/inspect", "get")]
    assert "build.sprites" in expected[("/projects/inspect", "get")]
    assert "catalog.query" in expected[("/projects/inspect", "get")]

    for (path, method), operation_ids in expected.items():
        assert path in seed["paths"], path
        assert method in seed["paths"][path], f"{method.upper()} {path}"
        assert seed["paths"][path][method]["x-paradev-frontend-api-operation-ids"] == operation_ids

    for path, methods in seed["paths"].items():
        for method, operation in methods.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            operation_ids = operation.get("x-paradev-frontend-api-operation-ids", [])
            for operation_id in operation_ids:
                row = next(row for row in contract["operations"] if row["id"] == operation_id)
                rest = row["bindings"]["rest"]
                assert (rest["path"], rest["method"].lower()) == (path, method)


def test_frontend_api_contract_lists_canonical_operations() -> None:
    from paradev.sdk import (
        FRONTEND_API_ACTION_DETAIL_SCHEMA,
        FRONTEND_API_BINDING_LOOKUP_SCHEMA,
        FRONTEND_API_BINDING_SURFACES,
        FRONTEND_API_FORM_SCHEMA,
        FRONTEND_API_OPTIONS_SCHEMA,
        FRONTEND_API_OPTION_SOURCE_SCHEMA,
        FRONTEND_API_SUMMARY_SCHEMA,
        FRONTEND_API_SELECTORS,
        FRONTEND_API_WORKSPACE_SCHEMA,
        get_frontend_api_contract,
        get_frontend_api_selection,
    )

    contract = get_frontend_api_contract()
    rows = {row["id"]: row for row in contract["operations"]}

    def input_names(operation_id: str) -> list[str]:
        return [field["name"] for field in rows[operation_id]["inputs"]]

    def inputs(operation_id: str) -> dict[str, dict[str, object]]:
        return {field["name"]: field for field in rows[operation_id]["inputs"]}

    assert contract["schema"] == "paradev.sdk.frontend-api.v1"
    assert get_frontend_api_selection() == contract
    assert get_frontend_api_selection(operation_id="module.list") == rows["module.list"]
    assert get_frontend_api_selection(group_id="modules")["operation_ids"] == contract["index"]["group"]["modules"]
    assert get_frontend_api_selection(operation_id="module.create", form=True)["schema"] == FRONTEND_API_FORM_SCHEMA
    with pytest.raises(ValueError, match="Pass only one frontend API selector"):
        get_frontend_api_selection(operation_id="module.list", group_id="modules")
    with pytest.raises(ValueError, match="form requires operation_id"):
        get_frontend_api_selection(form=True)
    assert contract["summary"]["schema"] == FRONTEND_API_SUMMARY_SCHEMA
    assert contract["summary"]["operation_count"] == len(contract["operations"])
    assert contract["summary"]["group_count"] == len(contract["groups"])
    assert contract["summary"]["workspace_section_count"] == len(contract["workspace"]["sections"])
    assert contract["summary"]["status_counts"] == {
        "implemented": 97,
        "frontend-local": 1,
    }
    assert contract["summary"]["mode_counts"] == {"read": 67, "write": 31}
    assert contract["summary"]["surface_counts"] == {
        "operation_count": 98,
        "sdk": 97,
        "cli": 74,
        "rest": 92,
        "mcp": 60,
        "lsp": 6,
        "unbound": 1,
    }
    assert contract["summary"]["group_counts"]["projects"] == {
        "operation_count": 15,
        "read": 9,
        "write": 6,
        "implemented": 14,
        "frontend-local": 1,
    }
    assert contract["summary"]["group_surface_counts"]["projects"] == {
        "operation_count": 15,
        "sdk": 14,
        "cli": 12,
        "rest": 13,
        "mcp": 9,
        "lsp": 0,
        "unbound": 1,
    }
    assert contract["summary"]["group_surface_counts"]["lsp"] == {
        "operation_count": 7,
        "sdk": 7,
        "cli": 1,
        "rest": 7,
        "mcp": 0,
        "lsp": 6,
        "unbound": 0,
    }
    assert contract["index"]["surface"]["rest"][:4] == [
        "project.create",
        "project.find",
        "project.open",
        "project.view",
    ]
    assert contract["index"]["surface"]["mcp"][:4] == [
        "project.create",
        "project.find",
        "project.open",
        "project.view",
    ]
    assert contract["index"]["surface"]["lsp"] == [
        "lsp.diagnostics",
        "lsp.symbols",
        "lsp.hover",
        "lsp.formatting",
        "lsp.completion",
        "lsp.semantic_tokens",
    ]
    assert contract["index"]["surface"]["unbound"] == ["project.activate"]
    assert contract["index"]["payload"]["Project.to_view"] == [
        "project.open",
        "project.view",
    ]
    assert contract["index"]["payload"]["paradev.build.explain.v1"] == [
        "module.view",
        "build.explain",
    ]
    assert contract["index"]["payload"]["untyped"] == [
        "project.config",
        "project.activate",
        "pdx.tokens",
        "pdx.dump",
        "catalog.write",
        "catalog.refresh",
        "surface.architecture",
        "surface.openapi",
        "surface.cli_contract",
        "surface.mcp_contract",
        "surface.lsp_contract",
    ]
    assert contract["index"]["workspace_section"]["project-switcher"] == [
        "project.state",
        "project.list",
        "project.find",
        "project.open",
        "project.create",
        "project.rename",
        "project.language",
        "project.activate",
    ]
    assert contract["index"]["workspace_section"]["catalog"] == [
        "catalog.preview",
        "catalog.write",
        "catalog.refresh",
        "catalog.query",
    ]
    assert contract["index"]["workspace_section"]["ai-chat"] == [
        "ai.profiles",
        "ai.profile.write",
        "ai.profile.reset",
        "ai.chat",
    ]
    assert contract["summary"]["group_counts"]["modules"] == {
        "operation_count": 20,
        "read": 9,
        "write": 11,
        "implemented": 20,
    }
    assert contract["summary"]["group_surface_counts"]["modules"] == {
        "operation_count": 20,
        "sdk": 20,
        "cli": 19,
        "rest": 20,
        "mcp": 19,
        "lsp": 0,
        "unbound": 0,
    }
    assert contract["summary"]["group_counts"]["localization"] == {
        "operation_count": 2,
        "read": 2,
        "write": 0,
        "implemented": 2,
    }
    assert contract["summary"]["group_surface_counts"]["localization"] == {
        "operation_count": 2,
        "sdk": 2,
        "cli": 0,
        "rest": 2,
        "mcp": 2,
        "lsp": 0,
        "unbound": 0,
    }
    assert contract["summary"]["group_counts"]["collections"]["operation_count"] == 12
    assert contract["summary"]["group_counts"]["build"] == {
        "operation_count": 18,
        "read": 15,
        "write": 3,
        "implemented": 18,
    }
    assert contract["summary"]["group_surface_counts"]["build"] == {
        "operation_count": 18,
        "sdk": 18,
        "cli": 14,
        "rest": 18,
        "mcp": 12,
        "lsp": 0,
        "unbound": 0,
    }
    assert contract["summary"]["group_counts"]["ai"] == {
        "operation_count": 4,
        "read": 2,
        "write": 2,
        "implemented": 4,
    }
    assert contract["summary"]["group_surface_counts"]["ai"] == {
        "operation_count": 4,
        "sdk": 4,
        "cli": 0,
        "rest": 4,
        "mcp": 0,
        "lsp": 0,
        "unbound": 0,
    }
    assert contract["summary"]["group_counts"]["surfaces"]["operation_count"] == 12
    assert contract["workspace"]["schema"] == FRONTEND_API_WORKSPACE_SCHEMA
    assert contract["workspace"]["sections"][0]["id"] == "project-switcher"
    assert [group["id"] for group in contract["groups"]] == [
        "projects",
        "modules",
        "collections",
        "localization",
        "build",
        "pdx",
        "lsp",
        "catalog",
        "ai",
        "surfaces",
    ]
    assert [group["operation_count"] for group in contract["groups"]] == [
        15,
        20,
        12,
        2,
        18,
        4,
        7,
        4,
        4,
        12,
    ]
    assert rows["project.create"]["sdk"] == "Project.create"
    assert rows["project.create"]["cli"] == "new"
    assert rows["project.create"]["rest"] == "POST /projects"
    assert rows["project.create"]["mcp"] == "project_create"
    assert rows["project.create"]["payload"] == "paradev.project.create.v1"
    project_create_inputs = inputs("project.create")
    assert list(project_create_inputs) == [
        "path",
        "project_id",
        "title",
        "game",
        "force",
    ]
    assert project_create_inputs["path"]["required"] is True
    assert project_create_inputs["game"]["default"] == "hoi4"
    assert project_create_inputs["force"]["default"] is False
    assert rows["project.find"]["sdk"] == "Project.find"
    assert rows["project.find"]["cli"] == "project-find"
    assert rows["project.find"]["rest"] == "GET /projects/find"
    assert rows["project.find"]["mcp"] == "project_find"
    assert rows["project.find"]["inputs"] == [{"name": "path", "type": "path", "required": False, "default": "."}]
    assert rows["project.open"]["sdk"] == "Project.load"
    assert rows["project.open"]["rest"] == "GET /projects"
    assert rows["project.open"]["mcp"] == "project_open"
    assert rows["project.open"]["payload"] == "Project.to_view"
    assert [field["name"] for field in rows["project.open"]["inputs"]] == [
        "path",
        "game",
        "title",
    ]
    assert rows["project.view"]["cli"] == "project"
    assert rows["project.view"]["rest"] == "GET /projects"
    assert rows["project.view"]["mcp"] == "project_view"
    assert rows["project.view"]["payload"] == "Project.to_view"
    assert [field["name"] for field in rows["project.view"]["inputs"]] == [
        "path",
        "game",
        "title",
    ]
    assert rows["project.list"]["sdk"] == "registered_projects"
    assert rows["project.list"]["cli"] == "projects"
    assert rows["project.list"]["rest"] == "GET /projects/list"
    assert rows["project.list"]["payload"] == "paradev.sdk.projects.v1"
    assert input_names("project.list") == ["project_paths", "search_roots"]
    assert inputs("project.list")["project_paths"]["default"] == []
    assert inputs("project.list")["search_roots"]["type"] == "array"
    assert input_names("project.inspect") == ["path", "kind"]
    assert inputs("project.inspect")["path"]["default"] == "."
    assert inputs("project.inspect")["kind"]["default"] == "summary"
    assert "modules" in inputs("project.inspect")["kind"]["choices"]
    assert "build-graph" in inputs("project.inspect")["kind"]["choices"]
    assert inputs("project.inspect")["kind"]["description"] == "SDK project inspection kind."
    assert input_names("project.config") == []
    assert rows["project.config"]["sdk"] == "CM_PARADEV"
    assert rows["project.rename"]["status"] == "implemented"
    assert rows["project.rename"]["sdk"] == "Project.rename"
    assert rows["project.rename"]["cli"] == "project-rename"
    assert rows["project.rename"]["rest"] == "PATCH /projects/rename"
    assert rows["project.rename"]["mcp"] == "project_rename"
    project_rename_inputs = inputs("project.rename")
    assert list(project_rename_inputs) == ["title", "path"]
    assert project_rename_inputs["title"]["required"] is True
    assert rows["project.language"]["sdk"] == "Project.set_preferred_language"
    assert rows["project.language"]["cli"] == "project-language"
    assert rows["project.language"]["rest"] == "PATCH /projects/language"
    assert rows["project.language"]["mcp"] == "project_preferred_language"
    project_language_inputs = inputs("project.language")
    assert list(project_language_inputs) == [
        "preferred_language",
        "path",
        "write",
        "plan_hash",
    ]
    assert project_language_inputs["preferred_language"]["choices"] == [
        "en",
        "fr",
        "de",
        "ru",
        "es",
        "pl",
        "pt_br",
        "zh",
        "ja",
        "ko",
    ]
    assert rows["project.activate"]["status"] == "frontend-local"
    assert rows["project.activate"]["inputs"] == [{"name": "project_id", "type": "string", "required": True}]
    assert rows["project.state"]["sdk"] == "desktop_state"
    assert rows["project.state"]["cli"] == "desktop-state"
    assert rows["project.state"]["rest"] == "GET /desktop/state"
    assert rows["project.state"]["payload"] == "paradev.desktop.state.v1"
    assert input_names("project.state") == [
        "project_path",
        "project_paths",
        "search_roots",
    ]
    assert rows["ai.profiles"]["sdk"] == "desktop_chat_profiles"
    assert rows["ai.profiles"]["rest"] == "GET /desktop/ai/profiles"
    assert rows["ai.profiles"]["payload"] == "paradev.desktop.ai-chat-profiles.v1"
    assert input_names("ai.profiles") == ["project_root"]
    assert rows["ai.profile.write"]["sdk"] == "desktop_write_chat_profile"
    assert rows["ai.profile.write"]["rest"] == "PUT /desktop/ai/profiles/{profile_id}"
    assert rows["ai.profile.write"]["payload"] == "paradev.desktop.ai-chat-profiles.v1"
    assert rows["ai.profile.write"]["mutates"] is True
    assert input_names("ai.profile.write") == ["profile_id", "profile", "project_root"]
    assert inputs("ai.profile.write")["profile_id"]["required"] is True
    assert inputs("ai.profile.write")["profile"]["required"] is True
    assert inputs("ai.profile.write")["profile"]["type"] == "object"
    assert rows["ai.profile.reset"]["sdk"] == "desktop_reset_chat_profile"
    assert rows["ai.profile.reset"]["rest"] == "DELETE /desktop/ai/profiles/{profile_id}"
    assert rows["ai.profile.reset"]["payload"] == "paradev.desktop.ai-chat-profiles.v1"
    assert rows["ai.profile.reset"]["mutates"] is True
    assert input_names("ai.profile.reset") == ["profile_id", "project_root"]
    assert inputs("ai.profile.reset")["profile_id"]["required"] is True
    assert rows["ai.chat"]["sdk"] == "desktop_chat"
    assert rows["ai.chat"]["rest"] == "POST /desktop/ai/chat"
    assert rows["ai.chat"]["payload"] == "paradev.desktop.ai-chat.v1"
    assert input_names("ai.chat") == [
        "provider",
        "model",
        "gateway",
        "preset",
        "key_env",
        "base_url",
        "prompt",
        "role",
        "project_root",
        "sources",
    ]
    assert inputs("ai.chat")["provider"]["default"] == "deepseek"
    assert inputs("ai.chat")["model"]["default"] == "deepseek-v4-flash"
    assert inputs("ai.chat")["gateway"]["default"] == "openai"
    assert inputs("ai.chat")["preset"]["default"] == "chat"
    assert inputs("ai.chat")["preset"]["choices"] == [
        "system",
        "chat",
        "reason",
        "coder",
    ]
    assert inputs("ai.chat")["key_env"]["required"] is False
    assert inputs("ai.chat")["base_url"]["required"] is False
    assert inputs("ai.chat")["prompt"]["required"] is True
    assert inputs("ai.chat")["role"]["default"] == "chat"
    assert rows["project.browser"]["sdk"] == "Project.browser"
    assert rows["project.browser"]["cli"] == "project-browser"
    assert rows["project.browser"]["rest"] == "GET /projects/browser"
    assert rows["project.browser"]["mcp"] == "project_browser"
    assert rows["project.browser"]["payload"] == "paradev.sdk.project-browser.v1"
    assert input_names("project.browser") == [
        "path",
        "profile",
        "kind",
        "family",
        "module_id",
        "collection_id",
    ]
    assert inputs("project.browser")["path"]["default"] == "."
    assert inputs("project.browser")["kind"]["choices"] == ["module", "collection"]
    assert rows["project.source_text"]["status"] == "implemented"
    assert rows["project.source_text"]["sdk"] == "Project.read_source_text"
    assert rows["project.source_text"]["rest"] == "GET /projects/{project_id}/sources"
    assert rows["project.source_text"]["payload"] == "paradev.rest.source_text.v1"
    assert input_names("project.source_text") == ["project_id", "path", "source_path"]
    assert inputs("project.source_text")["project_id"]["required"] is True
    assert inputs("project.source_text")["path"]["maps_to"] == "project_root"
    assert inputs("project.source_text")["path"]["default"] == "."
    assert inputs("project.source_text")["source_path"]["maps_to"] == "path"
    assert rows["project.draft_apply"]["status"] == "implemented"
    assert rows["project.draft_apply"]["sdk"] == "Project.apply_source_draft"
    assert rows["project.draft_apply"]["cli"] == "draft-apply"
    assert rows["project.draft_apply"]["rest"] == "POST /projects/{project_id}/drafts/apply"
    assert rows["project.draft_apply"]["payload"] == "paradev.rest.draft_apply.v1"
    assert input_names("project.draft_apply") == [
        "project_id",
        "path",
        "source_edits",
        "source_removals",
        "source_replacements",
        "module_rename",
    ]
    assert inputs("project.draft_apply")["path"]["maps_to"] == "project_root"
    draft_apply_form = get_frontend_api_selection(operation_id="project.draft_apply", form=True)
    draft_apply_fields = {field["name"]: field for field in draft_apply_form["fields"]}
    replacement_description = draft_apply_fields["source_replacements"]["description"]
    assert "content_format=png" in replacement_description
    assert "DDS, TGA, JPEG, WebP, or BMP" in replacement_description
    assert "atomic replacement" in replacement_description
    assert rows["module.list"]["sdk"] == "Project.inspect('modules')"
    assert input_names("module.list") == [
        "path",
        "profile",
        "family",
        "module_id",
        "collection_id",
        "source_slot",
    ]
    assert inputs("module.list")["path"]["default"] == "."
    assert input_names("module.view") == ["path", "module_id", "profile"]
    assert inputs("module.view")["module_id"]["required"] is True
    assert rows["module.templates"]["sdk"] == "Project.templates"
    assert rows["module.templates"]["cli"] == "templates"
    assert rows["module.templates"]["rest"] == "GET /projects/templates"
    assert rows["module.templates"]["mcp"] == "project_templates"
    assert rows["module.templates"]["payload"] == "paradev.sdk.templates.v1"
    assert input_names("module.templates") == [
        "path",
        "template_id",
        "family",
        "kind",
        "source",
        "authoring_ready",
        "diagnostic_code",
    ]
    module_template_inputs = inputs("module.templates")
    assert module_template_inputs["path"]["default"] == "."
    assert module_template_inputs["authoring_ready"]["type"] == "boolean"
    assert module_template_inputs["template_id"]["option_source"]["schema"] == FRONTEND_API_OPTION_SOURCE_SCHEMA
    assert module_template_inputs["template_id"]["option_source"]["operation_id"] == "module.templates"
    assert rows["module.create"]["sdk"] == "Project.scaffold_module"
    assert input_names("module.create") == [
        "path",
        "template_id",
        "object_id",
        "source_root",
        "values",
        "write",
        "force",
    ]
    module_create_inputs = inputs("module.create")
    assert module_create_inputs["template_id"]["required"] is True
    assert module_create_inputs["object_id"]["required"] is True
    assert module_create_inputs["write"]["default"] is False
    assert module_create_inputs["force"]["default"] is False
    assert rows["module.create_batch"]["sdk"] == "Project.create_modules"
    assert rows["module.create_batch"]["cli"] == "module-batch-create"
    assert rows["module.create_batch"]["rest"] == "POST /projects/modules/create-batch"
    assert rows["module.create_batch"]["mcp"] == "project_create_modules"
    assert rows["module.create_batch"]["payload"] == "paradev.sdk.module_batch.v1"
    assert input_names("module.create_batch") == [
        "project_id",
        "path",
        "modules",
        "source_root",
        "write",
        "plan_hash",
    ]
    assert inputs("module.create_batch")["project_id"]["required"] is True
    assert inputs("module.create_batch")["path"]["maps_to"] == "project_root"
    assert inputs("module.create_batch")["modules"]["required"] is True
    assert inputs("module.create_batch")["write"]["default"] is False
    assert inputs("module.create_batch")["plan_hash"]["required"] is False
    assert rows["module.draft"]["status"] == "implemented"
    assert rows["module.draft"]["sdk"] == "Project.create_module_draft"
    assert rows["module.draft"]["rest"] == "POST /projects/{project_id}/modules/{family_id}/drafts"
    assert rows["module.draft"]["payload"] == "paradev.rest.module_draft.v1"
    assert input_names("module.draft") == [
        "project_id",
        "family_id",
        "path",
        "template_id",
        "object_id",
        "values",
        "write",
        "force",
    ]
    assert inputs("module.draft")["family_id"]["required"] is True
    assert inputs("module.draft")["path"]["maps_to"] == "project_root"
    assert inputs("module.draft")["object_id"]["required"] is True
    assert inputs("module.draft")["write"]["default"] is False
    assert input_names("module.authoring_path") == [
        "path",
        "kind",
        "family",
        "target_id",
        "source_root",
    ]
    assert inputs("module.authoring_path")["kind"]["default"] == "module"
    assert input_names("module.authoring_plan") == [
        "path",
        "kind",
        "family",
        "target_id",
        "source_root",
        "profile",
    ]
    assert inputs("module.authoring_plan")["kind"]["default"] == "module"
    assert input_names("module.source_slots") == [
        "path",
        "profile",
        "family",
        "module_id",
        "collection_id",
        "slot",
        "status",
    ]
    assert inputs("module.source_slots")["status"]["choices"] == [
        "satisfied",
        "missing",
        "empty",
        "diagnostic",
    ]
    assert input_names("module.sources") == [
        "path",
        "profile",
        "family",
        "module_id",
        "collection_id",
        "slot",
        "loader",
        "status",
    ]
    assert inputs("module.sources")["status"]["choices"] == ["loaded", "diagnostic"]
    assert rows["module.diagram"]["sdk"] == "Project.module_diagram"
    assert rows["module.diagram"]["cli"] == "module-diagram"
    assert rows["module.diagram"]["rest"] == "GET /projects/modules/diagram"
    assert rows["module.diagram"]["mcp"] == "module_diagram"
    assert rows["module.diagram"]["payload"] == "paradev.sdk.module_diagram.v1"
    assert input_names("module.diagram") == ["path", "family", "profile"]
    assert inputs("module.diagram")["family"]["required"] is True
    assert rows["module.diagram.edit"]["sdk"] == "Project.edit_module_diagram"
    assert rows["module.diagram.edit"]["cli"] == "module-diagram-edit"
    assert rows["module.diagram.edit"]["rest"] == ("POST /projects/modules/diagram/edit")
    assert rows["module.diagram.edit"]["mcp"] == "module_diagram_edit"
    assert rows["module.diagram.edit"]["payload"] == ("paradev.sdk.module_diagram_edit.v1")
    assert input_names("module.diagram.edit") == [
        "path",
        "family",
        "profile",
        "position_intents",
        "edge_intents",
        "node_intents",
        "write",
        "plan_hash",
    ]
    assert inputs("module.diagram.edit")["path"]["maps_to"] == "project_root"
    assert inputs("module.diagram.edit")["position_intents"]["max_items"] == 4096
    assert inputs("module.diagram.edit")["edge_intents"]["max_items"] == 4096
    assert inputs("module.diagram.edit")["node_intents"]["max_items"] == 1
    assert rows["module.file"]["status"] == "implemented"
    assert rows["module.file"]["sdk"] == "Project.read_module_file"
    assert rows["module.file"]["cli"] == "module-file"
    assert rows["module.file"]["rest"] == "GET /projects/modules/file"
    assert rows["module.file"]["mcp"] == "module_file"
    assert input_names("module.file") == [
        "path",
        "module_id",
        "relative_path",
        "source_root",
        "encoding",
    ]
    assert inputs("module.file")["encoding"]["default"] == "utf-8"
    assert rows["module.rename"]["status"] == "implemented"
    assert rows["module.rename"]["sdk"] == "Project.rename_module"
    assert rows["module.rename"]["cli"] == "module-rename"
    assert rows["module.rename"]["rest"] == "PATCH /projects/modules/rename"
    assert rows["module.rename"]["mcp"] == "module_rename"
    assert input_names("module.rename") == [
        "path",
        "module_id",
        "object_id",
        "title",
        "source_root",
    ]
    assert inputs("module.rename")["object_id"]["required"] is True
    assert rows["module.duplicate"]["status"] == "implemented"
    assert rows["module.duplicate"]["sdk"] == "Project.duplicate_module"
    assert rows["module.duplicate"]["cli"] == "module-duplicate"
    assert rows["module.duplicate"]["rest"] == "POST /projects/modules/duplicate"
    assert rows["module.duplicate"]["mcp"] == "module_duplicate"
    assert rows["module.duplicate"]["payload"] == "paradev.sdk.module_duplicate.v1"
    assert input_names("module.duplicate") == [
        "path",
        "module_id",
        "object_id",
        "source_root",
        "destination_source_root",
        "identity",
        "write",
        "plan_hash",
    ]
    assert inputs("module.duplicate")["identity"]["default"] == "rewrite"
    assert inputs("module.duplicate")["identity"]["choices"] == [
        "rewrite",
        "preserve",
    ]
    assert inputs("module.duplicate")["path"]["maps_to"] == "project_root"
    assert inputs("module.duplicate")["module_id"]["required"] is True
    assert inputs("module.duplicate")["object_id"]["required"] is True
    assert inputs("module.duplicate")["write"]["default"] is False
    assert inputs("module.duplicate")["plan_hash"]["required"] is False
    assert rows["module.collection.set"]["status"] == "implemented"
    assert rows["module.collection.set"]["sdk"] == "Project.set_module_collection"
    assert rows["module.collection.set"]["cli"] == "module-collection-set"
    assert rows["module.collection.set"]["rest"] == "POST /projects/modules/collection"
    assert rows["module.collection.set"]["mcp"] == "module_collection_set"
    assert rows["module.collection.set"]["payload"] == "paradev.sdk.module_collection_update.v1"
    assert input_names("module.collection.set") == [
        "path",
        "module_id",
        "collection_id",
        "source_root",
        "write",
        "plan_hash",
    ]
    assert inputs("module.collection.set")["path"]["maps_to"] == "project_root"
    assert inputs("module.collection.set")["module_id"]["required"] is True
    assert inputs("module.collection.set")["write"]["default"] is False
    assert rows["module.activity.set"]["status"] == "implemented"
    assert rows["module.activity.set"]["sdk"] == "Project.set_module_active"
    assert rows["module.activity.set"]["cli"] == "module-activity-set"
    assert rows["module.activity.set"]["rest"] == "POST /projects/modules/activity"
    assert rows["module.activity.set"]["mcp"] == "module_activity_set"
    assert rows["module.activity.set"]["payload"] == "paradev.sdk.module_activity_update.v1"
    assert input_names("module.activity.set") == [
        "path",
        "module_id",
        "active",
        "source_root",
        "write",
        "plan_hash",
    ]
    assert inputs("module.activity.set")["active"]["required"] is True
    assert rows["module.metadata.clean"]["status"] == "implemented"
    assert rows["module.metadata.clean"]["sdk"] == "Project.clean_module_metadata"
    assert rows["module.metadata.clean"]["cli"] == "module-metadata-clean"
    assert rows["module.metadata.clean"]["rest"] == ("POST /projects/modules/metadata/clean")
    assert rows["module.metadata.clean"]["mcp"] == "module_metadata_clean"
    assert rows["module.metadata.clean"]["payload"] == ("paradev.sdk.module_metadata_cleanup.v1")
    assert input_names("module.metadata.clean") == [
        "path",
        "family",
        "module_id",
        "source_root",
        "write",
        "plan_hash",
    ]
    assert inputs("module.metadata.clean")["path"]["maps_to"] == "project_root"
    assert inputs("module.metadata.clean")["write"]["default"] is False
    assert inputs("module.metadata.clean")["plan_hash"]["required"] is False
    assert rows["module.edit"]["status"] == "implemented"
    assert rows["module.edit"]["sdk"] == "Project.write_module_file"
    assert rows["module.edit"]["cli"] == "module-edit"
    assert rows["module.edit"]["rest"] == "PATCH /projects/modules/file"
    assert rows["module.edit"]["mcp"] == "module_edit"
    assert input_names("module.edit") == [
        "path",
        "module_id",
        "relative_path",
        "text",
        "source_root",
        "create",
        "encoding",
    ]
    module_edit_inputs = inputs("module.edit")
    assert module_edit_inputs["text"]["required"] is True
    assert module_edit_inputs["create"]["default"] is False
    assert rows["module.remove"]["status"] == "implemented"
    assert rows["module.remove"]["sdk"] == "Project.remove_module"
    assert rows["module.remove"]["cli"] == "module-remove"
    assert rows["module.remove"]["rest"] == "DELETE /projects/modules/remove"
    assert rows["module.remove"]["mcp"] == "module_remove"
    assert input_names("module.remove") == ["path", "module_id", "source_root", "write"]
    assert inputs("module.remove")["write"]["default"] is False
    assert rows["collection.view"]["sdk"] == "Project.inspect('collections')"
    assert input_names("collection.list") == [
        "path",
        "profile",
        "family",
        "collection_id",
        "module_id",
        "source_slot",
    ]
    assert input_names("collection.view") == ["path", "collection_id", "profile"]
    assert inputs("collection.view")["collection_id"]["required"] is True
    assert input_names("collection.authoring_path") == [
        "path",
        "kind",
        "family",
        "target_id",
        "source_root",
    ]
    assert inputs("collection.authoring_path")["kind"]["default"] == "collection"
    assert input_names("collection.authoring_plan") == [
        "path",
        "kind",
        "family",
        "target_id",
        "source_root",
        "profile",
    ]
    assert inputs("collection.authoring_plan")["kind"]["default"] == "collection"
    assert input_names("collection.source_slots") == [
        "path",
        "profile",
        "family",
        "module_id",
        "collection_id",
        "slot",
        "status",
    ]
    assert rows["collection.sources"]["sdk"] == "Project.inspect('sources')"
    assert input_names("collection.sources") == [
        "path",
        "profile",
        "family",
        "collection_id",
        "slot",
        "loader",
        "status",
        "owner_kind",
    ]
    assert inputs("collection.sources")["owner_kind"]["default"] == "collection"
    assert rows["collection.file"]["status"] == "implemented"
    assert rows["collection.file"]["sdk"] == "Project.read_collection_file"
    assert rows["collection.file"]["cli"] == "collection-file"
    assert rows["collection.file"]["rest"] == "GET /projects/collections/file"
    assert rows["collection.file"]["mcp"] == "collection_file"
    assert input_names("collection.file") == [
        "path",
        "collection_id",
        "relative_path",
        "family",
        "source_root",
        "encoding",
    ]
    assert inputs("collection.file")["encoding"]["default"] == "utf-8"
    assert rows["collection.edit"]["status"] == "implemented"
    assert rows["collection.edit"]["sdk"] == "Project.write_collection_file"
    assert rows["collection.edit"]["cli"] == "collection-edit"
    assert rows["collection.edit"]["rest"] == "PATCH /projects/collections/file"
    assert rows["collection.edit"]["mcp"] == "collection_edit"
    assert input_names("collection.edit") == [
        "path",
        "collection_id",
        "relative_path",
        "text",
        "family",
        "source_root",
        "create",
        "encoding",
    ]
    collection_edit_inputs = inputs("collection.edit")
    assert collection_edit_inputs["text"]["required"] is True
    assert collection_edit_inputs["create"]["default"] is False
    assert rows["collection.scaffold"]["status"] == "implemented"
    assert rows["collection.scaffold"]["sdk"] == "Project.scaffold_collection"
    assert rows["collection.scaffold"]["cli"] == "collection-scaffold"
    assert rows["collection.scaffold"]["rest"] == ("POST /projects/collections/scaffold")
    assert rows["collection.scaffold"]["mcp"] == "collection_scaffold"
    assert input_names("collection.scaffold") == [
        "path",
        "template_id",
        "collection_id",
        "source_root",
        "values",
        "write",
        "force",
        "plan_hash",
    ]
    collection_scaffold_inputs = inputs("collection.scaffold")
    assert collection_scaffold_inputs["template_id"]["required"] is True
    assert collection_scaffold_inputs["collection_id"]["required"] is True
    assert collection_scaffold_inputs["write"]["default"] is False
    assert collection_scaffold_inputs["force"]["default"] is False
    assert rows["collection.create"]["status"] == "implemented"
    assert rows["collection.create"]["sdk"] == "Project.create_collection"
    assert rows["collection.create"]["cli"] == "collection-create"
    assert rows["collection.create"]["rest"] == "POST /projects/collections"
    assert rows["collection.create"]["mcp"] == "collection_create"
    assert input_names("collection.create") == [
        "path",
        "family",
        "collection_id",
        "source_root",
        "metadata",
        "write",
        "force",
    ]
    collection_create_inputs = inputs("collection.create")
    assert collection_create_inputs["family"]["required"] is True
    assert collection_create_inputs["collection_id"]["required"] is True
    assert collection_create_inputs["write"]["default"] is False
    assert collection_create_inputs["force"]["default"] is False
    assert rows["collection.rename"]["status"] == "implemented"
    assert rows["collection.rename"]["sdk"] == "Project.rename_collection"
    assert rows["collection.rename"]["cli"] == "collection-rename"
    assert rows["collection.rename"]["rest"] == "PATCH /projects/collections/rename"
    assert rows["collection.rename"]["mcp"] == "collection_rename"
    assert input_names("collection.rename") == [
        "path",
        "collection_id",
        "target_id",
        "family",
        "source_root",
    ]
    assert inputs("collection.rename")["collection_id"]["required"] is True
    assert inputs("collection.rename")["target_id"]["required"] is True
    assert rows["collection.remove"]["status"] == "implemented"
    assert rows["collection.remove"]["sdk"] == "Project.remove_collection"
    assert rows["collection.remove"]["cli"] == "collection-remove"
    assert rows["collection.remove"]["rest"] == "DELETE /projects/collections"
    assert rows["collection.remove"]["mcp"] == "collection_remove"
    assert input_names("collection.remove") == [
        "path",
        "collection_id",
        "family",
        "source_root",
        "write",
        "plan_hash",
    ]
    assert inputs("collection.remove")["collection_id"]["required"] is True
    assert inputs("collection.remove")["write"]["default"] is False
    assert rows["build.plan"]["status"] == "implemented"
    assert rows["build.plan"]["sdk"] == "Project.build"
    assert rows["build.plan"]["cli"] == "build"
    assert rows["build.plan"]["rest"] == "POST /projects/build"
    assert rows["build.plan"]["payload"] == "BuildResult.to_dict"
    assert input_names("build.plan") == ["path", "profile", "strict_metadata"]
    assert "default" not in inputs("build.plan")["strict_metadata"]
    assert rows["build.emit"]["status"] == "implemented"
    assert rows["build.emit"]["sdk"] == "Project.build"
    assert rows["build.emit"]["cli"] == "build --emit-artifacts/--emit-manifests"
    assert rows["build.emit"]["rest"] == "POST /projects/build?emit_artifacts=true&emit_manifests=true"
    assert rows["build.emit"]["payload"] == "BuildResult.to_dict"
    assert input_names("build.emit") == [
        "path",
        "profile",
        "strict_metadata",
        "emit_artifacts",
        "emit_manifests",
    ]
    assert "default" not in inputs("build.emit")["strict_metadata"]
    assert inputs("build.emit")["emit_artifacts"]["default"] is False
    assert inputs("build.emit")["emit_manifests"]["default"] is False
    assert rows["build.start"]["status"] == "implemented"
    assert rows["build.start"]["sdk"] == "desktop_start_build"
    assert rows["build.start"]["rest"] == "POST /desktop/builds"
    assert rows["build.start"]["payload"] == "paradev.desktop.build-run.v1"
    assert rows["build.start"]["mutates"] is True
    assert input_names("build.start") == [
        "project_root",
        "mode",
        "profile",
        "strict_metadata",
        "parallelism",
        "target",
    ]
    assert inputs("build.start")["project_root"]["required"] is True
    assert inputs("build.start")["mode"]["choices"] == ["cached", "full"]
    assert inputs("build.start")["mode"]["default"] == "cached"
    assert inputs("build.start")["parallelism"]["minimum"] == 1
    assert inputs("build.start")["target"]["type"] == "object"
    assert rows["build.runs"]["status"] == "implemented"
    assert rows["build.runs"]["sdk"] == "desktop_build_runs"
    assert rows["build.runs"]["rest"] == "GET /desktop/builds"
    assert rows["build.runs"]["payload"] == "paradev.desktop.build-runs.v1"
    assert input_names("build.runs") == ["project_root"]
    assert rows["build.status"]["status"] == "implemented"
    assert rows["build.status"]["sdk"] == "desktop_build_status"
    assert rows["build.status"]["rest"] == "GET /desktop/builds/status"
    assert rows["build.status"]["payload"] == "paradev.desktop.build-run.v1"
    assert input_names("build.status") == ["run_id"]
    assert inputs("build.status")["run_id"]["required"] is True
    assert rows["build.interrupt"]["status"] == "implemented"
    assert rows["build.interrupt"]["sdk"] == "desktop_interrupt_build"
    assert rows["build.interrupt"]["rest"] == "POST /desktop/builds/interrupt"
    assert rows["build.interrupt"]["payload"] == "paradev.desktop.build-run.v1"
    assert rows["build.interrupt"]["mutates"] is True
    assert input_names("build.interrupt") == ["run_id"]
    assert inputs("build.interrupt")["run_id"]["required"] is True
    assert input_names("build.summary") == ["path", "profile"]
    assert input_names("build.manifests") == ["path", "profile"]
    assert input_names("build.artifacts") == [
        "path",
        "profile",
        "artifact_type",
        "target_root",
        "owner",
        "artifact_path",
        "mode",
        "module_id",
        "collection_id",
    ]
    assert inputs("build.artifacts")["artifact_path"]["maps_to"] == "path"
    assert input_names("build.localization") == [
        "path",
        "profile",
        "language",
        "key",
        "key_prefix",
        "module_id",
        "collection_id",
    ]
    assert rows["build.assets"]["sdk"] == "Project.inspect('assets')"
    assert rows["build.assets"]["cli"] == "assets"
    assert input_names("build.assets") == [
        "path",
        "profile",
        "module_id",
        "collection_id",
        "family",
        "slot",
        "file_format",
    ]
    assert rows["build.sprites"]["sdk"] == "Project.inspect('sprites')"
    assert rows["build.sprites"]["cli"] == "sprites"
    assert input_names("build.sprites") == [
        "path",
        "profile",
        "module_id",
        "collection_id",
        "family",
        "slot",
        "name",
    ]
    assert input_names("build.diagnostics") == [
        "path",
        "profile",
        "severity",
        "code",
        "family",
        "owner",
        "target_root",
        "module_id",
        "collection_id",
        "source_path",
        "slot",
        "strict_metadata",
        "published",
    ]
    assert "default" not in inputs("build.diagnostics")["strict_metadata"]
    assert inputs("build.diagnostics")["severity"]["choices"] == ["error", "warning"]
    assert inputs("build.diagnostics")["target_root"]["choices"] == ["output", "build"]
    assert input_names("build.source_map") == [
        "path",
        "profile",
        "module_id",
        "collection_id",
        "family",
        "slot",
        "artifact_type",
        "target_root",
    ]
    assert inputs("build.source_map")["target_root"]["choices"] == ["output", "build"]
    assert input_names("build.dependencies") == [
        "path",
        "profile",
        "source",
        "target",
        "kind",
        "module_id",
    ]
    assert input_names("build.graph") == [
        "path",
        "profile",
        "module_id",
        "collection_id",
        "family",
        "slot",
        "artifact_type",
        "target_root",
        "edge_kind",
    ]
    assert inputs("build.graph")["target_root"]["choices"] == ["output", "build"]
    assert input_names("build.explain") == [
        "path",
        "module_id",
        "collection_id",
        "source_path",
        "artifact_path",
        "diagnostic_code",
        "target_root",
        "profile",
    ]
    assert input_names("build.families") == [
        "path",
        "profile",
        "family",
        "kind",
        "source_slot",
        "collection_source_slot",
        "sprite_slot",
        "route",
        "artifact_type",
    ]
    inspection_rows = {
        "module.list": ("modules", "paradev.build.modules.v1"),
        "module.view": ("build-explain", "paradev.build.explain.v1"),
        "module.sources": ("sources", "paradev.build.sources.v1"),
        "collection.list": ("collections", "paradev.build.collections.v1"),
        "collection.view": ("collections", "paradev.build.collections.v1"),
        "collection.source_slots": ("source-slots", "paradev.build.source-slots.v1"),
        "collection.sources": ("sources", "paradev.build.sources.v1"),
        "build.summary": ("summary", "paradev.build.summary.v1"),
        "build.manifests": ("manifests", "paradev.build.manifests.v1"),
        "build.artifacts": ("artifacts", "paradev.build.artifacts.v1"),
        "build.localization": ("localization", "paradev.build.localization.v1"),
        "build.assets": ("assets", "paradev.build.assets.v1"),
        "build.sprites": ("sprites", "paradev.build.sprites.v1"),
        "build.diagnostics": ("diagnostics", "paradev.build.diagnostics.v1"),
        "build.source_map": ("source-map", "paradev.build.source-map.v1"),
        "build.dependencies": ("dependencies", "paradev.build.dependencies.v1"),
        "build.graph": ("build-graph", "paradev.build.graph.v1"),
        "build.explain": ("build-explain", "paradev.build.explain.v1"),
        "build.families": ("families", "paradev.build.families.v1"),
        "catalog.preview": ("catalog-preview", "paradev.hb.catalog-preview.v1"),
        "catalog.query": ("catalog-query", "paradev.hb.catalog-query.v1"),
    }
    for operation_id, (kind, payload) in inspection_rows.items():
        assert rows[operation_id]["rest"] == f"GET /projects/inspect?kind={kind}"
        assert rows[operation_id]["mcp"] == "project_inspect"
        assert rows[operation_id]["payload"] == payload
    assert rows["collection.authoring_path"]["payload"] == "paradev.sdk.authoring_path.v1"
    assert rows["collection.authoring_plan"]["payload"] == "paradev.sdk.authoring_plan.v1"
    assert rows["pdx.parse"]["rest"] == "GET /pdx/parse"
    assert input_names("pdx.parse") == ["path", "include_dump", "include_tokens"]
    assert inputs("pdx.parse")["path"]["required"] is True
    assert inputs("pdx.parse")["include_dump"]["default"] is False
    assert inputs("pdx.parse")["include_tokens"]["default"] is False
    assert rows["pdx.tokens"]["sdk"] == "parse_pdx_file(..., include_tokens=True)"
    assert input_names("pdx.tokens") == ["path", "include_tokens"]
    assert inputs("pdx.tokens")["include_tokens"]["default"] is True
    assert input_names("pdx.dump") == ["path", "include_dump"]
    assert inputs("pdx.dump")["include_dump"]["default"] is True
    assert rows["pdx.format"]["status"] == "implemented"
    assert rows["pdx.format"]["sdk"] == "format_pdx_file"
    assert rows["pdx.format"]["cli"] == "format"
    assert rows["pdx.format"]["rest"] == "POST /pdx/format"
    assert rows["pdx.format"]["mcp"] == "pdx_format"
    assert input_names("pdx.format") == ["path", "indent", "comments", "write"]
    pdx_format_inputs = inputs("pdx.format")
    assert pdx_format_inputs["path"]["required"] is True
    assert pdx_format_inputs["indent"]["default"] == "\t"
    assert pdx_format_inputs["comments"]["default"] is True
    assert pdx_format_inputs["write"]["default"] is False
    assert rows["lsp.diagnostics"]["status"] == "implemented"
    assert rows["lsp.diagnostics"]["sdk"] == "diagnose_pdx_lsp_text"
    assert rows["lsp.diagnostics"]["rest"] == "POST /lsp/diagnostics"
    assert rows["lsp.diagnostics"]["lsp"] == "textDocument/publishDiagnostics"
    assert rows["lsp.diagnostics"]["payload"] == "paradev.lsp.diagnostics.v1"
    assert input_names("lsp.diagnostics") == ["text", "uri", "path"]
    assert inputs("lsp.diagnostics")["text"]["required"] is True
    assert rows["lsp.symbols"]["status"] == "implemented"
    assert rows["lsp.symbols"]["sdk"] == "document_symbols_pdx_lsp_text"
    assert rows["lsp.symbols"]["rest"] == "POST /lsp/symbols"
    assert rows["lsp.symbols"]["lsp"] == "textDocument/documentSymbol"
    assert rows["lsp.symbols"]["payload"] == "paradev.lsp.symbols.v1"
    assert input_names("lsp.symbols") == ["text", "uri", "path"]
    assert inputs("lsp.symbols")["text"]["required"] is True
    assert rows["lsp.hover"]["status"] == "implemented"
    assert rows["lsp.hover"]["sdk"] == "hover_pdx_lsp_text"
    assert rows["lsp.hover"]["rest"] == "POST /lsp/hover"
    assert rows["lsp.hover"]["lsp"] == "textDocument/hover"
    assert rows["lsp.hover"]["payload"] == "paradev.lsp.hover.v1"
    assert input_names("lsp.hover") == ["text", "line", "character", "uri", "path"]
    lsp_hover_inputs = inputs("lsp.hover")
    assert lsp_hover_inputs["text"]["required"] is True
    assert lsp_hover_inputs["line"]["required"] is True
    assert lsp_hover_inputs["line"]["minimum"] == 0
    assert lsp_hover_inputs["character"]["required"] is True
    assert lsp_hover_inputs["character"]["minimum"] == 0
    assert rows["lsp.formatting"]["status"] == "implemented"
    assert rows["lsp.formatting"]["sdk"] == "format_pdx_lsp_text"
    assert rows["lsp.formatting"]["rest"] == "POST /lsp/formatting"
    assert rows["lsp.formatting"]["lsp"] == "textDocument/formatting"
    assert rows["lsp.formatting"]["payload"] == "paradev.lsp.formatting.v1"
    assert input_names("lsp.formatting") == [
        "text",
        "uri",
        "path",
        "indent",
        "comments",
    ]
    lsp_formatting_inputs = inputs("lsp.formatting")
    assert lsp_formatting_inputs["text"]["required"] is True
    assert lsp_formatting_inputs["indent"]["default"] == "\t"
    assert lsp_formatting_inputs["comments"]["default"] is True
    assert rows["lsp.completion"]["status"] == "implemented"
    assert rows["lsp.completion"]["sdk"] == "complete_pdx_lsp_text"
    assert rows["lsp.completion"]["rest"] == "POST /lsp/completion"
    assert rows["lsp.completion"]["lsp"] == "textDocument/completion"
    assert rows["lsp.completion"]["payload"] == "paradev.lsp.completion.v1"
    assert input_names("lsp.completion") == [
        "text",
        "line",
        "character",
        "offset",
        "uri",
        "path",
        "project_path",
        "database",
        "game_root",
        "limit",
    ]
    lsp_completion_inputs = inputs("lsp.completion")
    assert lsp_completion_inputs["text"]["required"] is True
    assert lsp_completion_inputs["line"]["minimum"] == 0
    assert lsp_completion_inputs["character"]["minimum"] == 0
    assert lsp_completion_inputs["offset"]["minimum"] == 0
    assert lsp_completion_inputs["limit"]["default"] == 100
    assert rows["lsp.semantic_tokens"]["status"] == "implemented"
    assert rows["lsp.semantic_tokens"]["sdk"] == "semantic_tokens_pdx_lsp_text"
    assert rows["lsp.semantic_tokens"]["rest"] == "POST /lsp/semantic-tokens"
    assert rows["lsp.semantic_tokens"]["lsp"] == "textDocument/semanticTokens/full"
    assert rows["lsp.semantic_tokens"]["payload"] == "paradev.lsp.semantic-tokens.v1"
    assert input_names("lsp.semantic_tokens") == ["text", "uri", "path"]
    assert inputs("lsp.semantic_tokens")["text"]["required"] is True
    assert rows["lsp.keywords"]["status"] == "implemented"
    assert rows["lsp.keywords"]["sdk"] == "hoi4_keyword_dataset"
    assert rows["lsp.keywords"]["cli"] == "lsp keywords"
    assert rows["lsp.keywords"]["rest"] == "GET /lsp/keywords"
    assert rows["lsp.keywords"]["payload"] == "paradev.hoi4.keyword-dataset.v1"
    assert input_names("lsp.keywords") == ["game_root"]
    assert input_names("catalog.preview") == ["path", "profile"]
    assert rows["catalog.write"]["rest"] == "POST /projects/catalog"
    assert input_names("catalog.write") == ["path", "profile", "database"]
    assert rows["catalog.refresh"]["rest"] == "PUT /projects/catalog"
    assert input_names("catalog.refresh") == ["path", "profile", "database"]
    assert input_names("catalog.query") == [
        "path",
        "database",
        "entity",
        "target_id",
        "name",
        "tag",
        "limit",
        "offset",
        "include_data",
    ]
    catalog_query_inputs = inputs("catalog.query")
    assert catalog_query_inputs["limit"]["default"] == 100
    assert catalog_query_inputs["limit"]["minimum"] == 1
    assert catalog_query_inputs["limit"]["maximum"] == 200
    assert catalog_query_inputs["offset"]["default"] == 0
    assert catalog_query_inputs["include_data"]["default"] is False
    assert rows["surface.frontend_api"]["sdk"] == "get_frontend_api_selection"
    assert rows["surface.frontend_api"]["selectors"] == list(FRONTEND_API_SELECTORS)
    assert input_names("surface.frontend_api") == [*FRONTEND_API_SELECTORS, "form"]
    assert inputs("surface.frontend_api")["form"]["default"] is False
    assert rows["surface.frontend_api.workspace"]["sdk"] == "get_frontend_api_workspace"
    assert rows["surface.frontend_api.workspace"]["cli"] == "frontend-api --workspace"
    assert rows["surface.frontend_api.workspace"]["rest"] == "GET /frontend-api/workspace"
    assert rows["surface.frontend_api.workspace"]["payload"] == FRONTEND_API_WORKSPACE_SCHEMA
    assert input_names("surface.frontend_api.workspace") == []
    assert rows["surface.frontend_api.action"]["sdk"] == "get_frontend_api_action"
    assert rows["surface.frontend_api.action"]["cli"] == "frontend-api --operation --action"
    assert rows["surface.frontend_api.action"]["rest"] == "GET /frontend-api/action"
    assert rows["surface.frontend_api.action"]["payload"] == FRONTEND_API_ACTION_DETAIL_SCHEMA
    assert input_names("surface.frontend_api.action") == ["operation_id"]
    assert inputs("surface.frontend_api.action")["operation_id"]["required"] is True
    assert rows["surface.frontend_api.normalize"]["sdk"] == "normalize_frontend_api_inputs"
    assert rows["surface.frontend_api.normalize"]["cli"] == "frontend-api --operation --values-json"
    assert rows["surface.frontend_api.normalize"]["rest"] == "POST /frontend-api/normalize"
    assert rows["surface.frontend_api.normalize"]["payload"] == "paradev.sdk.frontend-api.inputs.v1"
    assert input_names("surface.frontend_api.normalize") == ["operation_id", "values"]
    assert inputs("surface.frontend_api.normalize")["operation_id"]["required"] is True
    assert inputs("surface.frontend_api.normalize")["values"]["default"] == {}
    assert rows["surface.frontend_api.rest_request"]["sdk"] == "plan_frontend_api_rest_request"
    assert rows["surface.frontend_api.rest_request"]["cli"] == "frontend-api --operation --values-json --rest-request"
    assert rows["surface.frontend_api.rest_request"]["rest"] == "POST /frontend-api/rest-request"
    assert rows["surface.frontend_api.rest_request"]["payload"] == "paradev.sdk.frontend-api.rest-request.v1"
    assert input_names("surface.frontend_api.rest_request") == [
        "operation_id",
        "values",
    ]
    assert inputs("surface.frontend_api.rest_request")["operation_id"]["required"] is True
    assert inputs("surface.frontend_api.rest_request")["values"]["default"] == {}
    assert rows["surface.frontend_api.options"]["sdk"] == "resolve_frontend_api_options"
    assert rows["surface.frontend_api.options"]["cli"] == "frontend-api --operation --option-field --values-json"
    assert rows["surface.frontend_api.options"]["rest"] == "POST /frontend-api/options"
    assert rows["surface.frontend_api.options"]["payload"] == FRONTEND_API_OPTIONS_SCHEMA
    assert input_names("surface.frontend_api.options") == [
        "operation_id",
        "field_name",
        "values",
    ]
    assert inputs("surface.frontend_api.options")["operation_id"]["required"] is True
    assert inputs("surface.frontend_api.options")["field_name"]["required"] is True
    assert inputs("surface.frontend_api.options")["values"]["default"] == {}
    assert rows["surface.frontend_api.binding_lookup"]["sdk"] == "get_frontend_api_binding_lookup"
    assert rows["surface.frontend_api.binding_lookup"]["cli"] == "frontend-api --binding-surface --binding-key"
    assert rows["surface.frontend_api.binding_lookup"]["rest"] == "GET /frontend-api/binding"
    assert rows["surface.frontend_api.binding_lookup"]["payload"] == FRONTEND_API_BINDING_LOOKUP_SCHEMA
    assert input_names("surface.frontend_api.binding_lookup") == [
        "binding_surface",
        "binding_key",
    ]
    assert inputs("surface.frontend_api.binding_lookup")["binding_surface"]["choices"] == list(FRONTEND_API_BINDING_SURFACES)
    assert inputs("surface.frontend_api.binding_lookup")["binding_key"]["required"] is True
    assert input_names("surface.architecture") == []
    assert input_names("surface.openapi") == []
    assert input_names("surface.cli_contract") == []
    assert input_names("surface.mcp_contract") == []
    assert input_names("surface.lsp_contract") == []
    rest_backed_without_input_contract = [row["id"] for row in rows.values() if "rest" in row and "inputs" not in row]
    assert rest_backed_without_input_contract == []
    implemented_without_input_contract = [row["id"] for row in rows.values() if row["status"] == "implemented" and "inputs" not in row]
    assert implemented_without_input_contract == []
    assert "module.list" in contract["index"]["group"]["modules"]
    assert "project.list" in contract["index"]["group"]["projects"]
    assert "build.emit" in contract["index"]["group"]["build"]
    assert "pdx.parse" in contract["index"]["status"]["implemented"]
    assert "project.find" in contract["index"]["mode"]["read"]
    assert "module.list" in contract["index"]["mode"]["read"]
    assert "project.create" in contract["index"]["mode"]["write"]
    assert "build.emit" in contract["index"]["mode"]["write"]
    assert "lsp.formatting" in contract["index"]["status"]["implemented"]
    assert "lsp.diagnostics" in contract["index"]["status"]["implemented"]
    assert "lsp.symbols" in contract["index"]["status"]["implemented"]
    assert "lsp.hover" in contract["index"]["status"]["implemented"]
    assert get_frontend_api_selection(index_name="mode", key="write") == contract["index"]["mode"]["write"]
    assert get_frontend_api_selection(index_name="surface", key="lsp") == contract["index"]["surface"]["lsp"]
    assert get_frontend_api_selection(index_name="payload", key="Project.to_view") == [
        "project.open",
        "project.view",
    ]
    assert get_frontend_api_selection(index_name="workspace_section", key="catalog") == [
        "catalog.preview",
        "catalog.write",
        "catalog.refresh",
        "catalog.query",
    ]
    assert "modules" in contract["inspection_contract"]["index"]["kind"]
    json.dumps(contract)


def test_frontend_api_typescript_renderer_matches_desktop_contract_file() -> None:
    from paradev.sdk import get_frontend_api_contract, render_frontend_api_typescript

    contract = get_frontend_api_contract()
    source = render_frontend_api_typescript()

    assert source.startswith("/* Generated by `rtk uv run paradev frontend-api --typescript`; do not edit by hand. */")
    assert 'export const PARADEV_FRONTEND_API_SCHEMA = "paradev.sdk.frontend-api.v1" as const;' in source
    assert "export type ParaDevFrontendApiOperationId = (typeof PARADEV_FRONTEND_API_OPERATION_IDS)[number];" in source
    assert "export type ParaDevFrontendApiMode = (typeof PARADEV_FRONTEND_API_MODE_VALUES)[number];" in source
    assert "export const PARADEV_FRONTEND_API_MODE_VALUES = [" in source
    assert '  "read",' in source
    assert '  "write"' in source
    assert "readonly summary: ParaDevJsonObject;" in source
    assert "export const PARADEV_FRONTEND_API_CONTRACT = " in source
    assert "as const satisfies ParaDevFrontendApiContract;" in source
    assert '"project.create",' in source
    assert '"module.create",' in source
    assert '"pdx.format",' in source
    assert '"lsp.hover",' in source
    for row in contract["operations"]:
        assert f'"{row["id"]}"' in source

    generated = Path("apps/desktop/src/generated/frontendApi.ts").read_text(encoding="utf-8")
    assert generated == source


def test_desktop_frontend_api_helper_consumes_generated_contract() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert 'from "../generated/frontendApi"' in helper
    assert "PARADEV_FRONTEND_API_CONTRACT" in helper
    assert "export type FrontendApiSummary" in helper
    assert "export type FrontendApiGroupCount" in helper
    assert "export type FrontendApiSurfaceCount" in helper
    assert "export type FrontendApiGroupIndex" in helper
    assert "export type FrontendApiStatusIndex" in helper
    assert "export type FrontendApiModeIndex" in helper
    assert "export type FrontendApiSurfaceIndex" in helper
    assert "export type FrontendApiPayloadIndex" in helper
    assert "export type FrontendApiWorkspaceSectionIndex" in helper
    assert "export const frontendApiOperations" in helper
    assert "export const frontendApiSummary = PARADEV_FRONTEND_API_CONTRACT.summary as unknown as FrontendApiSummary" in helper
    assert "export const frontendApiGroupIndex = PARADEV_FRONTEND_API_CONTRACT.index.group" in helper
    assert "export const frontendApiStatusIndex = PARADEV_FRONTEND_API_CONTRACT.index.status" in helper
    assert "export const frontendApiModeIndex = PARADEV_FRONTEND_API_CONTRACT.index.mode" in helper
    assert "export const frontendApiSurfaceIndex = PARADEV_FRONTEND_API_CONTRACT.index.surface" in helper
    assert "export const frontendApiPayloadIndex = PARADEV_FRONTEND_API_CONTRACT.index.payload" in helper
    assert "export const frontendApiWorkspaceSectionIndex = PARADEV_FRONTEND_API_CONTRACT.index.workspace_section" in helper
    assert "operationCount: frontendApiOperations.length" not in helper
    assert "export function getFrontendApiOperation" in helper
    assert "export function getFrontendApiGroupOperationIds" in helper
    assert "export function getFrontendApiStatusOperationIds" in helper
    assert "export function getFrontendApiModeOperationIds" in helper
    assert "export function getFrontendApiGroupOperations" in helper
    assert "export function getFrontendApiSectionOperations" in helper
    assert "export function getFrontendApiWorkspaceSectionOperationIds" in helper


def test_desktop_frontend_api_helper_exposes_workspace_actions() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export type FrontendApiAction" in helper
    assert "export type FrontendApiActionExecutionConfirmation" in helper
    assert "export type FrontendApiActionConfirmationStates" in helper
    assert "export type FrontendApiActionRunState" in helper
    assert "readonly confirmation: FrontendApiActionExecutionConfirmation;" in helper
    assert "readonly operation_id: ParaDevFrontendApiOperationId;" in helper
    assert "readonly execution: FrontendApiActionExecution;" in helper
    assert "export const frontendApiWorkspaceActions" in helper
    assert "const actionsByOperationId" in helper
    assert "export function getFrontendApiAction" in helper
    assert "export function getFrontendApiSectionActions" in helper
    assert "export function getFrontendApiDefaultSectionAction" in helper
    assert "export function isFrontendApiActionConfirmationSatisfied" in helper
    assert "export function getFrontendApiActionRunState" in helper
    assert "confirmation.required !== true || confirmationStates[operationId] === true" in helper
    assert "confirmation_satisfied: confirmationSatisfied" in helper
    assert 'restPlanResult?.error ?? "REST plan not ready"' in helper
    assert "section.default_operation_id" in helper


def test_desktop_shell_derives_workspace_navigation_from_frontend_api_sections() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "frontendApiWorkspaceSections" in helper
    assert "getFrontendApiDefaultSectionAction" in helper
    assert "frontendApiWorkspaceActions = frontendApiWorkspaceSections.flatMap((section) => section.actions)" in helper
    assert "ParaDevFrontendApiWorkspaceSectionId" in helper
    assert "readonly operation_ids: readonly ParaDevFrontendApiOperationId[]" in helper
    assert "readonly actions: readonly FrontendApiAction[]" in helper
    assert "section.default_operation_id" in helper


def test_desktop_workspace_renders_selected_section_actions_from_frontend_api_helper() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "getFrontendApiSectionActions" in helper
    assert "getFrontendApiDefaultSectionAction" in helper
    assert "getFrontendApiRequiredInputNames" in helper
    assert "readonly default_surface: string;" in helper
    assert "section.default_operation_id" in helper


def test_desktop_frontend_api_helper_exposes_surface_bindings() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export type FrontendApiRestBinding" in helper
    assert "export type FrontendApiBindings" in helper
    assert "readonly bindings?: FrontendApiBindings;" in helper
    assert "export const frontendApiRestOperations" in helper
    assert "export function getFrontendApiBindings" in helper
    assert "export function getFrontendApiRestBinding" in helper
    assert "operation.bindings?.rest" in helper
    assert "does not expose a REST binding" in helper


def test_desktop_frontend_api_helper_exposes_input_metadata() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export type FrontendApiOptionSource" in helper
    assert "readonly option_source?: FrontendApiOptionSource;" in helper
    assert "export const frontendApiInputOperations" in helper
    assert "export function getFrontendApiInputs" in helper
    assert "export function getFrontendApiRequiredInputNames" in helper
    assert "export function getFrontendApiDefaultValues" in helper
    assert "export function getFrontendApiOptionSourceInputs" in helper
    assert "input.required === true" in helper
    assert 'Object.prototype.hasOwnProperty.call(input, "default")' in helper


def test_desktop_frontend_api_helper_exposes_selected_action_detail() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export function getFrontendApiActionDetail" in helper
    assert "const operation = getFrontendApiOperation(operationId)" in helper
    assert "const action = getFrontendApiAction(operationId)" in helper
    assert "frontendApiWorkspaceSections.filter((section) => section.operation_ids.includes(operationId))" in helper
    assert 'schema: "paradev.sdk.frontend-api.action-detail.v1"' in helper
    assert 'schema: "paradev.sdk.frontend-api.form.v1"' in helper
    assert "fields: getFrontendApiInputs(operationId)" in helper
    assert "required: getFrontendApiRequiredInputNames(operationId)" in helper
    assert "defaults: getFrontendApiDefaultValues(operationId)" in helper
    assert "option_fields: getFrontendApiOptionSourceInputs(operationId).map((input) => input.name)" in helper
    assert "bindings: operation.bindings" in helper
    assert "execution: action.execution" in helper


def test_desktop_frontend_api_helper_exposes_selected_action_panel_state() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export type FrontendApiActionPanelStateInput" in helper
    assert "export type FrontendApiActionPanelState" in helper
    assert "export function getFrontendApiActionPanelState" in helper
    assert "readonly values_with_defaults: FrontendApiSubmittedValues;" in helper
    assert "readonly normalize_request: FrontendApiJsonRequestInit;" in helper
    assert "readonly rest_plan_request: FrontendApiJsonRequestInit;" in helper
    assert "readonly option_request_key: string;" in helper
    assert "readonly execution_request_key: string;" in helper
    assert "readonly run_state: FrontendApiActionRunState;" in helper
    assert "const valuesWithDefaults = getFrontendApiFormValuesWithDefaults(operationId, values)" in helper
    assert "const optionRequests = getFrontendApiFormOptionRequests(operationId, values)" in helper
    assert "option_request_key: JSON.stringify(" in helper
    assert "execution_request_key: JSON.stringify({" in helper
    assert "run_state: getFrontendApiActionRunState(" in helper
    assert "default_count: Object.keys(detail.form?.defaults ?? {}).length" in helper


def test_desktop_workspace_uses_generated_form_controls_for_selected_action() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export type FrontendApiFormControlKind" in helper
    assert "export type FrontendApiFormControl" in helper
    assert "export function getFrontendApiFormControlKind" in helper
    assert "export function getFrontendApiFormControls" in helper
    assert "input.choices?.length" in helper
    assert "input.option_source" in helper
    assert 'input.type === "boolean"' in helper
    assert 'input.type === "object" || input.type === "array"' in helper
    assert "const missingRequirements = (input.option_source?.requires ?? []).filter" in helper
    assert 'disabled_reason: missingRequirements.length ? `Requires ${missingRequirements.join(", ")}` : undefined' in helper
    assert "value_preview: formatFrontendApiControlValue(value)" in helper


def test_desktop_workspace_plans_option_requests_from_local_form_state() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export type FrontendApiFormOptionRequest" in helper
    assert "export function getFrontendApiFormValuesWithDefaults" in helper
    assert "export function getFrontendApiFormOptionRequests" in helper
    assert "const valuesWithDefaults = getFrontendApiFormValuesWithDefaults(operationId, values)" in helper
    assert "available: missingRequirements.length === 0" in helper
    assert "missing_requirements: missingRequirements" in helper
    assert "buildFrontendApiOptionsRequest(operationId, input.name, valuesWithDefaults)" in helper


def test_desktop_workspace_executes_option_requests_through_sdk_endpoint_helper() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export type FrontendApiFetch" in helper
    assert "export type FrontendApiFormOptionResultStatus" in helper
    assert "export type FrontendApiFormOptionResult" in helper
    assert "export async function resolveFrontendApiFormOptionRequest" in helper
    assert "fetcher: FrontendApiFetch = fetch" in helper
    assert "const response = await fetcher(optionRequest.request.url, optionRequest.request.init)" in helper
    assert "const payload = (await response.json()) as FrontendApiOptionPayload" in helper
    assert 'status: payload.available ? "ready" : "unavailable"' in helper
    assert 'status: "error"' in helper


def test_desktop_workspace_binds_option_results_to_generated_form_controls() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export type FrontendApiFormControlOptionSource" in helper
    assert "export type FrontendApiFormControlOption" in helper
    assert "readonly options: readonly FrontendApiFormControlOption[];" in helper
    assert "readonly option_status?: FrontendApiFormOptionResultStatus;" in helper
    assert "export type FrontendApiFormOptionResults" in helper
    assert "function getFrontendApiStaticControlOptions" in helper
    assert "function getFrontendApiOptionPayloadControlOptions" in helper
    assert 'source: "option-source"' in helper
    assert "optionResults: FrontendApiFormOptionResults = {}" in helper
    assert "const optionResult = optionResults[input.name]" in helper
    assert "option_status: optionResult?.status" in helper
    assert (
        "options: optionResult?.payload ? getFrontendApiOptionPayloadControlOptions(optionResult.payload) : getFrontendApiStaticControlOptions(input.choices)"
        in helper
    )


def test_desktop_frontend_api_helper_exposes_rest_endpoint_helpers() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export const frontendApiEndpointPaths" in helper
    assert 'action: "/frontend-api/action"' in helper
    assert 'options: "/frontend-api/options"' in helper
    assert 'binding: "/frontend-api/binding"' in helper
    assert "export type FrontendApiActionDetail" in helper
    assert "export type FrontendApiOptionPayload" in helper
    assert "export type FrontendApiNormalizedInputs" in helper
    assert "export type FrontendApiRestRequestPlan" in helper
    assert "export function buildFrontendApiDiscoveryUrl" in helper
    assert "export function buildFrontendApiActionUrl" in helper
    assert "export function buildFrontendApiOptionsUrl" in helper
    assert "export function buildFrontendApiNormalizeUrl" in helper
    assert "export function buildFrontendApiRestRequestUrl" in helper
    assert "export function buildFrontendApiBindingLookupUrl" in helper
    assert "new URLSearchParams" in helper
    assert "operation_id" in helper
    assert "field_name" in helper
    assert "binding_surface" in helper
    assert "binding_key" in helper


def test_desktop_frontend_api_helper_exposes_json_request_helpers() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export type FrontendApiSubmittedValues" in helper
    assert "export type FrontendApiJsonRequestInit" in helper
    assert "export function buildFrontendApiJsonRequestInit" in helper
    assert "export function buildFrontendApiOptionsRequest" in helper
    assert "export function buildFrontendApiNormalizeRequest" in helper
    assert "export function buildFrontendApiRestPlanRequest" in helper
    assert 'method: "POST"' in helper
    assert '"Content-Type": "application/json"' in helper
    assert "JSON.stringify(values)" in helper
    assert "buildFrontendApiOptionsUrl(operationId, fieldName)" in helper
    assert "buildFrontendApiNormalizeUrl(operationId)" in helper
    assert "buildFrontendApiRestRequestUrl(operationId)" in helper


def test_desktop_workspace_executes_normalize_and_rest_plan_requests_from_selected_action() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export type FrontendApiMetaRequestResultStatus" in helper
    assert "export type FrontendApiNormalizeResult" in helper
    assert "export type FrontendApiRestPlanResult" in helper
    assert "export async function resolveFrontendApiNormalizeRequest" in helper
    assert "export async function resolveFrontendApiRestPlanRequest" in helper
    assert "function isFrontendApiMetaEndpointAvailable(request: FrontendApiJsonRequestInit): boolean" in helper
    assert "import.meta.env.DEV" in helper
    assert "Frontend API bridge unavailable" in helper
    assert "if (!isFrontendApiMetaEndpointAvailable(request))" in helper
    assert "const response = await fetcher(request.url, request.init)" in helper
    assert "const payload = (await response.json()) as FrontendApiNormalizedInputs" in helper
    assert "const payload = (await response.json()) as FrontendApiRestRequestPlan" in helper
    assert 'status: "ready"' in helper
    assert 'status: "error"' in helper


def test_desktop_workspace_executes_ready_rest_plan_through_helper() -> None:
    helper = Path("apps/desktop/src/data/frontendApi.ts").read_text(encoding="utf-8")

    assert "export type FrontendApiRestExecutionResultStatus" in helper
    assert "export type FrontendApiRestExecutionResult" in helper
    assert "export function buildFrontendApiRestExecutionRequest" in helper
    assert "export async function resolveFrontendApiRestExecutionRequest" in helper
    assert "plan: FrontendApiRestRequestPlan" in helper
    assert "buildFrontendApiUrl(plan.path" in helper
    assert "Object.fromEntries(" in helper
    assert "Object.entries(plan.query)" in helper
    assert "Object.keys(plan.body).length" in helper
    assert "const response = await fetcher(request.url, request.init)" in helper
    assert "const payload = await response.json()" in helper
    assert "Frontend API bridge unavailable" in helper
    assert "Requires confirmation" in helper


def test_frontend_api_workspace_projection_groups_gui_actions() -> None:
    from paradev.sdk import (
        FRONTEND_API_ACTION_SCHEMA,
        FRONTEND_API_WORKSPACE_SCHEMA,
        get_frontend_api_contract,
        get_frontend_api_workspace,
    )

    contract = get_frontend_api_contract()
    rows = {row["id"]: row for row in contract["operations"]}
    workspace = get_frontend_api_workspace()

    assert workspace == contract["workspace"]
    assert workspace["schema"] == FRONTEND_API_WORKSPACE_SCHEMA
    assert workspace["contract_schema"] == "paradev.sdk.frontend-api.v1"
    assert workspace["sdk_owned"] is True
    assert [section["id"] for section in workspace["sections"]] == [
        "project-switcher",
        "project-browser",
        "authoring",
        "source-editor",
        "build",
        "catalog",
        "ai-chat",
        "surface-contracts",
    ]

    sections = {section["id"]: section for section in workspace["sections"]}
    assert sections["project-switcher"]["default_operation_id"] == "project.state"
    assert sections["project-switcher"]["operation_ids"] == [
        "project.state",
        "project.list",
        "project.find",
        "project.open",
        "project.create",
        "project.rename",
        "project.language",
        "project.activate",
    ]
    assert sections["authoring"]["operation_ids"] == [
        "module.authoring_path",
        "module.authoring_plan",
        "module.templates",
        "module.diagram",
        "module.diagram.edit",
        "module.create",
        "module.create_batch",
        "module.draft",
        "module.rename",
        "module.collection.set",
        "module.activity.set",
        "module.metadata.clean",
        "module.remove",
        "collection.authoring_path",
        "collection.authoring_plan",
        "collection.scaffold",
        "collection.create",
        "collection.rename",
        "collection.remove",
        "localization.workspace",
        "localization.plan",
    ]
    assert sections["source-editor"]["operation_ids"] == [
        "project.source_text",
        "project.source_form",
        "module.file",
        "module.edit",
        "collection.file",
        "collection.edit",
        "project.draft_apply",
        "pdx.parse",
        "pdx.format",
        "lsp.diagnostics",
        "lsp.symbols",
        "lsp.hover",
        "lsp.formatting",
        "lsp.completion",
        "lsp.semantic_tokens",
        "lsp.keywords",
    ]
    assert "build.graph" in sections["build"]["operation_ids"]
    assert "catalog.query" in sections["catalog"]["operation_ids"]
    assert sections["ai-chat"]["default_operation_id"] == "ai.chat"
    assert sections["ai-chat"]["operation_ids"] == [
        "ai.profiles",
        "ai.profile.write",
        "ai.profile.reset",
        "ai.chat",
    ]
    assert "surface.frontend_api.workspace" in sections["surface-contracts"]["operation_ids"]
    assert "surface.frontend_api.action" in sections["surface-contracts"]["operation_ids"]
    assert "surface.frontend_api.options" in sections["surface-contracts"]["operation_ids"]
    assert "surface.frontend_api.binding_lookup" in sections["surface-contracts"]["operation_ids"]

    edit_action = next(action for action in sections["source-editor"]["actions"] if action["operation_id"] == "module.edit")
    expected_edit_action = {
        "operation_id": "module.edit",
        "title": "Module Edit",
        "group": "modules",
        "status": "implemented",
        "read_only": False,
        "mutates": True,
        "form": True,
        "summary": rows["module.edit"]["summary"],
    }
    assert {key: edit_action[key] for key in expected_edit_action} == expected_edit_action
    assert edit_action["schema"] == FRONTEND_API_ACTION_SCHEMA
    assert workspace["index"]["section"]["source-editor"] == sections["source-editor"]["operation_ids"]
    assert workspace["index"]["operation_id"]["pdx.format"] == ["source-editor"]
    assert workspace["index"]["operation_id"]["surface.frontend_api.workspace"] == ["surface-contracts"]
    assert workspace["index"]["operation_id"]["surface.frontend_api.action"] == ["surface-contracts"]
    assert workspace["index"]["operation_id"]["surface.frontend_api.options"] == ["surface-contracts"]
    assert workspace["index"]["operation_id"]["surface.frontend_api.binding_lookup"] == ["surface-contracts"]

    for section in workspace["sections"]:
        for operation_id in section["operation_ids"]:
            assert operation_id in rows


def test_frontend_api_action_detail_combines_operation_form_and_workspace_context() -> None:
    from paradev.sdk import (
        FRONTEND_API_ACTION_DETAIL_SCHEMA,
        FRONTEND_API_ACTION_SCHEMA,
        FRONTEND_API_FORM_SCHEMA,
        get_frontend_api_action,
    )

    detail = get_frontend_api_action("module.create")

    assert detail["schema"] == FRONTEND_API_ACTION_DETAIL_SCHEMA
    assert detail["operation_id"] == "module.create"
    assert detail["sections"] == ["authoring"]
    assert detail["action"]["schema"] == FRONTEND_API_ACTION_SCHEMA
    assert detail["action"]["execution"]["default_surface"] == "rest"
    assert detail["form"]["schema"] == FRONTEND_API_FORM_SCHEMA
    assert detail["form"]["required"] == ["template_id", "object_id"]
    assert detail["option_fields"] == ["template_id", "source_root"]
    assert detail["option_sources"]["template_id"]["operation_id"] == "module.templates"
    assert detail["bindings"]["rest"] == {
        "method": "POST",
        "path": "/projects/scaffold",
        "query": {},
    }

    openapi = get_frontend_api_action("surface.openapi")

    assert openapi["sections"] == ["surface-contracts"]
    assert openapi["form"] is None
    assert openapi["option_fields"] == []
    assert openapi["action"]["execution"]["default_surface"] == "sdk"

    with pytest.raises(ValueError, match="Unknown frontend API operation: nope"):
        get_frontend_api_action("nope")


def test_frontend_api_workspace_actions_expose_execution_hints() -> None:
    from paradev.sdk import (
        FRONTEND_API_ACTION_SCHEMA,
        FRONTEND_API_CONFIRMATION_SCHEMA,
        FRONTEND_API_FORM_SCHEMA,
        FRONTEND_API_INPUTS_SCHEMA,
        FRONTEND_API_REST_REQUEST_SCHEMA,
        get_frontend_api_contract,
        get_frontend_api_workspace,
    )

    rows = {row["id"]: row for row in get_frontend_api_contract()["operations"]}
    sections = {section["id"]: section for section in get_frontend_api_workspace()["sections"]}

    module_edit = next(action for action in sections["source-editor"]["actions"] if action["operation_id"] == "module.edit")
    assert module_edit["schema"] == FRONTEND_API_ACTION_SCHEMA
    assert module_edit["payload"] == "paradev.module.file.v1"
    assert module_edit["form_schema"] == FRONTEND_API_FORM_SCHEMA
    assert module_edit["bindings"] == rows["module.edit"]["bindings"]
    assert module_edit["execution"] == {
        "kind": "adapter",
        "default_surface": "rest",
        "available_surfaces": ["sdk", "cli", "rest", "mcp"],
        "binding": {"method": "PATCH", "path": "/projects/modules/file", "query": {}},
        "requires_values": True,
        "normalizer_schema": FRONTEND_API_INPUTS_SCHEMA,
        "rest_request_schema": FRONTEND_API_REST_REQUEST_SCHEMA,
        "confirmation": {
            "schema": FRONTEND_API_CONFIRMATION_SCHEMA,
            "required": True,
            "scope": "project-files",
            "style": "write",
            "title": "Confirm Module Edit",
            "summary": "Write one text source file inside a module.",
            "confirm_fields": ["create"],
            "default_confirmed": False,
        },
    }

    project_activate = next(action for action in sections["project-switcher"]["actions"] if action["operation_id"] == "project.activate")
    assert "bindings" not in project_activate
    assert project_activate["form_schema"] == FRONTEND_API_FORM_SCHEMA
    assert project_activate["execution"] == {
        "kind": "frontend-local",
        "default_surface": "frontend-local",
        "available_surfaces": [],
        "binding": {},
        "requires_values": True,
        "state_scope": "workspace",
        "normalizer_schema": FRONTEND_API_INPUTS_SCHEMA,
        "confirmation": {
            "schema": FRONTEND_API_CONFIRMATION_SCHEMA,
            "required": False,
            "scope": "workspace-state",
            "style": "state",
            "title": "Project Activate",
            "summary": "Select the active project in a frontend workspace.",
            "confirm_fields": [],
            "default_confirmed": True,
        },
    }

    openapi = next(action for action in sections["surface-contracts"]["actions"] if action["operation_id"] == "surface.openapi")
    assert openapi["execution"] == {
        "kind": "adapter",
        "default_surface": "sdk",
        "available_surfaces": ["sdk"],
        "binding": {"call": "get_openapi_seed"},
        "requires_values": False,
        "confirmation": {
            "schema": FRONTEND_API_CONFIRMATION_SCHEMA,
            "required": False,
            "scope": "none",
            "style": "none",
            "title": "Surface Openapi",
            "summary": "Return the local REST/OpenAPI seed.",
            "confirm_fields": [],
            "default_confirmed": True,
        },
    }


def test_frontend_api_action_detail_exposes_confirmation_policy() -> None:
    from paradev.sdk import FRONTEND_API_CONFIRMATION_SCHEMA, get_frontend_api_action

    module_remove = get_frontend_api_action("module.remove")
    confirmation = module_remove["execution"]["confirmation"]

    assert confirmation["schema"] == FRONTEND_API_CONFIRMATION_SCHEMA
    assert confirmation["required"] is True
    assert confirmation["scope"] == "project-files"
    assert confirmation["style"] == "destructive"
    assert confirmation["confirm_fields"] == ["write"]
    assert confirmation["default_confirmed"] is False
    assert module_remove["action"]["execution"]["confirmation"] == confirmation

    project_state = get_frontend_api_action("project.state")
    assert project_state["execution"]["confirmation"]["required"] is False
    assert project_state["execution"]["confirmation"]["scope"] == "none"


def test_frontend_api_reference_manual_matches_sdk_renderer() -> None:
    from paradev.sdk import (
        get_frontend_api_contract,
        render_frontend_api_reference_markdown,
    )

    reference = render_frontend_api_reference_markdown()
    operations = get_frontend_api_contract()["operations"]

    assert reference.startswith("# Frontend API Reference\n")
    assert "## English" in reference
    assert "## 中文" in reference
    assert "### Index Catalog / Index 目录" in reference
    assert "### Surface Index / Surface 索引" in reference
    assert "### Surface Coverage / Surface 覆盖" in reference
    assert "### REST Route Index / REST Route 索引" in reference
    assert "### REST Request Planner Index / REST Request Planner 索引" in reference
    assert "### Workspace Section REST Summary Index / Workspace Section REST Summary 索引" in reference
    assert "### Group REST Summary Index / Group REST Summary 索引" in reference
    assert "### REST Static Query Index / REST Static Query 索引" in reference
    assert "### REST Dynamic Query Field Index / REST Dynamic Query Field 索引" in reference
    assert "### REST Path Parameter Index / REST Path Parameter 索引" in reference
    assert "### REST Body Field Index / REST Body Field 索引" in reference
    assert "### SDK Call Index / SDK Call 索引" in reference
    assert "### SDK Call Input Index / SDK Call Input 索引" in reference
    assert "### MCP Tool Index / MCP Tool 索引" in reference
    assert "### MCP Tool Input Index / MCP Tool Input 索引" in reference
    assert "### CLI Command Index / CLI Command 索引" in reference
    assert "### CLI Command Input Index / CLI Command Input 索引" in reference
    assert "### LSP Method Index / LSP Method 索引" in reference
    assert "### LSP Method Input Index / LSP Method Input 索引" in reference
    assert "### Binding Index / Binding 索引" in reference
    assert "### Group Binding Summary Index / Group Binding Summary 索引" in reference
    assert "### Payload Index / Payload 索引" in reference
    assert "### Workspace Section Index / Workspace Section 索引" in reference
    assert "### Workspace Section Mode Status Index / Workspace Section Mode Status 索引" in reference
    assert "### Group Mode Status Index / Group Mode Status 索引" in reference
    assert "### Workspace Section Payload Coverage Index / Workspace Section Payload Coverage 索引" in reference
    assert "### Group Payload Coverage Index / Group Payload Coverage 索引" in reference
    assert "### Workspace Section Surface Coverage Index / Workspace Section Surface Coverage 索引" in reference
    assert "### Workspace Section Binding Summary Index / Workspace Section Binding Summary 索引" in reference
    assert "### Workspace Section Form Summary Index / Workspace Section Form Summary 索引" in reference
    assert "### Workspace Section Control Summary Index / Workspace Section Control Summary 索引" in reference
    assert "### Group Control Summary Index / Group Control Summary 索引" in reference
    assert "### Workspace Section Option Source Summary Index / Workspace Section Option Source Summary 索引" in reference
    assert "### Workspace Section Input Target Summary Index / Workspace Section Input Target Summary 索引" in reference
    assert "### Group Input Target Summary Index / Group Input Target Summary 索引" in reference
    assert "### Workspace Section Validation Summary Index / Workspace Section Validation Summary 索引" in reference
    assert "### Group Validation Summary Index / Group Validation Summary 索引" in reference
    assert "### Workspace Section Default Summary Index / Workspace Section Default Summary 索引" in reference
    assert "### Group Default Summary Index / Group Default Summary 索引" in reference
    assert "### Workspace Section Required Summary Index / Workspace Section Required Summary 索引" in reference
    assert "### Group Required Summary Index / Group Required Summary 索引" in reference
    assert "### Workspace Section Alias Summary Index / Workspace Section Alias Summary 索引" in reference
    assert "### Group Alias Summary Index / Group Alias Summary 索引" in reference
    assert "### Group Execution Summary Index / Group Execution Summary 索引" in reference
    assert "### Workspace Section Execution Summary Index / Workspace Section Execution Summary 索引" in reference
    assert "### Workspace Action Execution Index / Workspace Action Execution 索引" in reference
    assert "### Group Confirmation Summary Index / Group Confirmation Summary 索引" in reference
    assert "### Workspace Section Confirmation Summary Index / Workspace Section Confirmation Summary 索引" in reference
    assert "### Confirmation Index / Confirmation 索引" in reference
    assert "### Group Option Source Summary Index / Group Option Source Summary 索引" in reference
    assert "### Option Source Index / Option Source 索引" in reference
    assert "### Option Provider Index / Option Provider 索引" in reference
    assert "### Input Field Index / Input Field 索引" in reference
    assert "### Group Form Summary Index / Group Form Summary 索引" in reference
    assert "### Operation Form Summary Index / Operation Form Summary 索引" in reference
    assert "### Form Control Index / Form Control 索引" in reference
    assert "### Required Input Index / Required Input 索引" in reference
    assert "### Input Default Index / Input Default 索引" in reference
    assert "### Input Constraint Index / Input Constraint 索引" in reference
    assert "### Input Target Index / Input Target 索引" in reference
    assert "### Input Alias Index / Input Alias 索引" in reference
    assert "Generated from `paradev.sdk.get_frontend_api_contract()`." in reference
    assert "由 `paradev.sdk.get_frontend_api_contract()` 生成。" in reference
    assert "| `projects` | 15 | 14 | 12 | 13 | 9 | 0 | 1 |" in reference
    assert "| `lsp` | 7 | 7 | 1 | 7 | 0 | 6 | 0 |" in reference
    assert (
        '| `group` | `contract["index"]["group"][group_id]` | `get_frontend_api_group_operation_ids(group_id)` | `getFrontendApiGroupOperationIds(groupId)` | Group id to operation ids. |'
        in reference
    )
    assert (
        '| `binding` | `contract["index"]["binding"][surface][key]` | `get_frontend_api_binding_operation_ids(surface, key)` | `getFrontendApiBindingOperationIds(surface, key)` | Surface call key to operation ids. |'
        in reference
    )
    assert (
        '| `workspace_section` | `contract["index"]["workspace_section"][section_id]` | `get_frontend_api_workspace_section_operation_ids(section_id)` | `getFrontendApiWorkspaceSectionOperationIds(sectionId)` | Workspace section id to operation ids. |'
        in reference
    )
    assert "| `rest` | 92 | `project.create`, `project.find`, `project.open`, `project.view`, `project.list`, `project.inspect`," in reference
    assert "| `lsp` | 6 | `lsp.diagnostics`, `lsp.symbols`, `lsp.hover`, `lsp.formatting`, `lsp.completion`, `lsp.semantic_tokens` |" in reference
    assert "| `unbound` | 1 | `project.activate` |" in reference
    assert "| `GET` | `/projects` |  | 2 | `project.open`, `project.view` |" in reference
    assert "| `GET` | `/projects/inspect` | `kind=modules` | 1 | `module.list` |" in reference
    assert "| `POST` | `/projects/build` | `emit_artifacts=true&emit_manifests=true` | 1 | `build.emit` |" in reference
    assert "| `POST` | `/projects/build` | `emit_artifacts=true&emit_manifests=true` |  |  | `build.emit` |" in reference
    assert (
        "| `project-switcher` | 8 | 7 | 7 | `GET:4`, `PATCH:2`, `POST:1` |  |  |  | `force`, `game`, `path`, `plan_hash`, `preferred_language`, `project_id`, `project_path`, `project_paths`, `search_roots`, `title`, `write` |"
        in reference
    )
    assert (
        "| `source-editor` | 16 | 16 | 16 | `GET:5`, `PATCH:2`, `POST:9` |  | `project_id` | `character`, `comments`, `database`, `game_root`, `indent`, `limit`, `line`, `module_rename`, `offset`, `path`, `project_path`, `project_root`, `query`, `source_edits`, `source_removals`, `source_replacements`, `text`, `uri` |"
        in reference
    )
    assert (
        "| `projects` | 15 | 13 | 12 | `GET:8`, `PATCH:2`, `POST:3` |  | `project_id` | `module_rename`, `path`, `project_root`, `query`, `source_edits`, `source_removals`, `source_replacements`, `text` |"
        in reference
    )
    assert (
        "| `lsp` | 7 | 7 | 7 | `GET:1`, `POST:6` |  |  | `character`, `comments`, `database`, `game_root`, `indent`, `limit`, `line`, `offset`, `path`, `project_path`, `text`, `uri` | `game_root` |"
        in reference
    )
    assert "| `kind` | `modules` | `module.list` | `GET` | `/projects/inspect` | `string` |" in reference
    assert "| `emit_artifacts` | `true` | `build.emit` | `POST` | `/projects/build` | `boolean` |" in reference
    assert "| `include_tokens` | `true` | `pdx.tokens` | `GET` | `/pdx/parse` | `boolean` |" in reference
    assert "| `path` | `project.create` | `POST` | `/projects` | `path` | `path` | yes | `parameters` |  |" in reference
    assert "| `profile` | `module.list` | `GET` | `/projects/inspect` | `profile` | `string` | no | `parameters` |  |" in reference
    assert "| `emit_artifacts` | `build.emit` | `POST` | `/projects/build` | `emit_artifacts` | `boolean` | no | `parameters` | `true` |" in reference
    assert "| `include_tokens` | `pdx.tokens` | `GET` | `/pdx/parse` | `include_tokens` | `boolean` | no | `parameters` | `true` |" in reference
    assert (
        "| `POST` | `/projects/{project_id}/modules/{family_id}/drafts` |  | `project_id`, `family_id` | `force`, `object_id`, `project_root`, `template_id`, `values`, `write` | `module.draft` |"
        in reference
    )
    assert (
        "| `POST` | `/projects/{project_id}/drafts/apply` |  | `project_id` | `module_rename`, `project_root`, `source_edits`, `source_removals`, `source_replacements` | `project.draft_apply` |"
        in reference
    )
    assert "| `POST` | `/frontend-api/rest-request` |  |  | `values` | `surface.frontend_api.rest_request` |" in reference
    assert "| `project_id` | `project.source_text` | `GET` | `/projects/{project_id}/sources` | `project_id` | `string` | yes | `parameters` |" in reference
    assert (
        "| `project_id` | `project.draft_apply` | `POST` | `/projects/{project_id}/drafts/apply` | `project_id` | `string` | yes | `parameters` |" in reference
    )
    assert (
        "| `family_id` | `module.draft` | `POST` | `/projects/{project_id}/modules/{family_id}/drafts` | `family_id` | `string` | yes | `parameters` |"
        in reference
    )
    assert "| `project_root` | `project.draft_apply` | `POST` | `/projects/{project_id}/drafts/apply` | `path` | `path` | no | `parameters` |" in reference
    assert "| `project_root` | `module.draft` | `POST` | `/projects/{project_id}/modules/{family_id}/drafts` | `path` | `path` | no | `project` |" in reference
    assert "| `text` | `lsp.hover` | `POST` | `/lsp/hover` | `text` | `text` | yes | `parameters` |" in reference
    assert "| `values` | `surface.frontend_api.rest_request` | `POST` | `/frontend-api/rest-request` | `values` | `object` | no | `parameters` |" in reference
    assert "| `Project.build` | 2 | `build.plan`, `build.emit` |" in reference
    assert "| `Project.inspect('build-explain')` | 2 | `module.view`, `build.explain` |" in reference
    assert "| `get_frontend_api_selection` | 1 | `surface.frontend_api` |" in reference
    assert "| `project_authoring_path` | 2 | `module.authoring_path`, `collection.authoring_path` |" in reference
    assert "| `Project.create` | `project.create` | `path` | `path` | yes |  | `parameters` |  |" in reference
    assert "| `Project.create` | `project.create` | `game` | `string` | no | `hoi4` | `parameters` |  |" in reference
    assert "| `Project.inspect('modules')` | `module.list` | `profile` | `string` | no |  | `parameters` |  |" in reference
    assert "| `Project.build` | `build.emit` | `emit_artifacts` | `boolean` | no | `false` | `parameters` |  |" in reference
    assert "| `parse_pdx_file` | `pdx.parse` | `include_tokens` | `boolean` | no | `false` | `parameters` |  |" in reference
    assert "| `project_inspect` | 23 | `project.inspect`, `module.list`, `module.view`," in reference
    assert "| `project_create` | `project.create` | `path` | `path` | yes |  | `parameters` |  |" in reference
    assert "| `project_create` | `project.create` | `game` | `string` | no | `hoi4` | `parameters` |  |" in reference
    assert "| `project_inspect` | `module.list` | `profile` | `string` | no |  | `parameters` |  |" in reference
    assert "| `pdx_parse` | `pdx.parse` | `include_tokens` | `boolean` | no | `false` | `parameters` |  |" in reference
    assert "| `frontend_api` | 1 | `surface.frontend_api` |" in reference
    assert "| `frontend-api --binding-surface --binding-key` | 1 | `surface.frontend_api.binding_lookup` |" in reference
    assert "| `new` | `project.create` | `path` | `path` | yes |  | `parameters` |  |" in reference
    assert "| `new` | `project.create` | `game` | `string` | no | `hoi4` | `parameters` |  |" in reference
    assert "| `modules` | `module.list` | `profile` | `string` | no |  | `parameters` |  |" in reference
    assert "| `build --emit-artifacts/--emit-manifests` | `build.emit` | `emit_artifacts` | `boolean` | no | `false` | `parameters` |  |" in reference
    assert "| `parse` | `pdx.parse` | `include_tokens` | `boolean` | no | `false` | `parameters` |  |" in reference
    assert "| `project` | 2 | `project.open`, `project.view` |" in reference
    assert "| `source-slots` | 2 | `module.source_slots`, `collection.source_slots` |" in reference
    assert "| `textDocument/completion` | 1 | `lsp.completion` |" in reference
    assert "| `textDocument/publishDiagnostics` | 1 | `lsp.diagnostics` |" in reference
    assert "| `textDocument/semanticTokens/full` | 1 | `lsp.semantic_tokens` |" in reference
    assert "| `textDocument/hover` | `lsp.hover` | `line` | `integer` | yes |  | `parameters` |  |" in reference
    assert "| `textDocument/completion` | `lsp.completion` | `limit` | `integer` | no | `100` | `parameters` |  |" in reference
    assert "| `textDocument/formatting` | `lsp.formatting` | `comments` | `boolean` | no | `true` | `parameters` |  |" in reference
    assert "| `textDocument/semanticTokens/full` | `lsp.semantic_tokens` | `text` | `text` | yes |  | `parameters` |  |" in reference
    assert "| `cli` | `frontend-api --binding-surface --binding-key` | 1 | `surface.frontend_api.binding_lookup` |" in reference
    assert "| `rest` | `GET /projects/inspect?kind=modules` | 1 | `module.list` |" in reference
    assert "| `mcp` | `project_inspect` | 23 |" in reference
    assert (
        "| `projects` | 15 | 14 | `CM_PARADEV`, `Project.apply_source_draft`, `Project.browser`, `Project.create`, `Project.find`, `Project.inspect`, `Project.load`, `Project.read_source_text`, `Project.rename`, `Project.set_preferred_language`, `Project.source_form`, `Project.to_view`, `desktop_state`, `registered_projects` | `config`, `desktop-state`, `draft-apply`, `inspections and inspection commands`, `new`, `project`, `project-browser`, `project-find`, `project-language`, `project-rename`, `projects` |"
        in reference
    )
    assert (
        "| `lsp` | 7 | 7 | `complete_pdx_lsp_text`, `diagnose_pdx_lsp_text`, `document_symbols_pdx_lsp_text`, `format_pdx_lsp_text`, `hoi4_keyword_dataset`, `hover_pdx_lsp_text`, `semantic_tokens_pdx_lsp_text` | `lsp keywords` |"
        in reference
    )
    assert "| `Project.to_view` | 2 | `project.open`, `project.view` |" in reference
    assert "| `untyped` | 11 |" in reference
    assert (
        "| `projects` | 15 | 12 | 2 | `Project inspection payload:1`, `Project.to_view:2`, `paradev.desktop.state.v1:1`, `paradev.project.create.v1:1`, `paradev.project.find.v1:1`, `paradev.project.preferred-language.v1:1`, `paradev.project.rename.v1:1`, `paradev.rest.draft_apply.v1:1`, `paradev.rest.source_text.v1:1`, `paradev.sdk.project-browser.v1:1`, `paradev.sdk.projects.v1:1`, `paradev.source-form.v1:1` |"
        in reference
    )
    assert (
        "| `surfaces` | 12 | 7 | 5 | `paradev.sdk.frontend-api.action-detail.v1:1`, `paradev.sdk.frontend-api.binding-lookup.v1:1`, `paradev.sdk.frontend-api.inputs.v1:1`, `paradev.sdk.frontend-api.options.v1:1`, `paradev.sdk.frontend-api.rest-request.v1:1`, `paradev.sdk.frontend-api.v1:1`, `paradev.sdk.frontend-api.workspace.v1:1` |"
        in reference
    )
    assert (
        "| `project-switcher` | 8 | `project.state` | `project.state`, `project.list`, `project.find`, `project.open`, `project.create`, `project.rename`, `project.language`, `project.activate` |"
        in reference
    )
    assert "| `projects` | 15 | 9 | 6 | 14 | 0 | 1 |" in reference
    assert "| `surfaces` | 12 | 12 | 0 | 12 | 0 | 0 |" in reference
    assert "| `project-switcher` | 8 | 4 | 4 | 7 | 0 | 1 |" in reference
    assert "| `authoring` | 21 | 8 | 13 | 21 | 0 | 0 |" in reference
    assert "| `surface-contracts` | 12 | 12 | 0 | 12 | 0 | 0 |" in reference
    assert (
        "| `project-switcher` | 8 | 7 | 1 | `Project.to_view:1`, `paradev.desktop.state.v1:1`, `paradev.project.create.v1:1`, `paradev.project.find.v1:1`, `paradev.project.preferred-language.v1:1`, `paradev.project.rename.v1:1`, `paradev.sdk.projects.v1:1` |"
        in reference
    )
    assert "| `catalog` | 4 | 2 | 2 | `paradev.hb.catalog-preview.v1:1`, `paradev.hb.catalog-query.v1:1` |" in reference
    assert (
        "| `surface-contracts` | 12 | 7 | 5 | `paradev.sdk.frontend-api.action-detail.v1:1`, `paradev.sdk.frontend-api.binding-lookup.v1:1`, `paradev.sdk.frontend-api.inputs.v1:1`, `paradev.sdk.frontend-api.options.v1:1`, `paradev.sdk.frontend-api.rest-request.v1:1`, `paradev.sdk.frontend-api.v1:1`, `paradev.sdk.frontend-api.workspace.v1:1` |"
        in reference
    )
    assert (
        "| `projects` | 15 | 12 | `adapter:11`, `frontend-local:1` | `frontend-local:1`, `rest:11` | `cli:9`, `mcp:7`, `rest:11`, `sdk:11` | 12 | 4 | `workspace:1` | 12 | 11 |"
        in reference
    )
    assert "| `surfaces` | 12 | 12 | `adapter:12` | `rest:8`, `sdk:4` | `cli:8`, `mcp:2`, `rest:8`, `sdk:12` | 6 | 0 |  | 6 | 8 |" in reference
    assert (
        "| `modules` | 20 | 19 | 10 | `project-files:10` | `destructive:1`, `write:9` | `create:1`, `force:2`, `write:8` | `module.diagram.edit`, `module.create`, `module.create_batch`, `module.draft`, `module.rename`, `module.collection.set`, `module.activity.set`, `module.metadata.clean`, `module.remove`, `module.edit` |"
        in reference
    )
    assert "| `catalog` | 4 | 4 | 2 | `catalog:2` | `write:2` |  | `catalog.write`, `catalog.refresh` |" in reference
    assert (
        "| `modules` | 20 | 45 | 20 | 6 | `build.diagnostics`, `build.families`, `collection.list`, `module.list`, `module.sources`, `module.templates` | `collections`, `diagnostics`, `families`, `modules`, `source_roots`, `sources`, `templates` | `module_id`, `path` |"
        in reference
    )
    assert (
        "| `projects` | 15 | 5 | 3 | 4 | `build.families`, `collection.list`, `module.list`, `module.sources` | `collections`, `families`, `modules`, `sources` | `path` |"
        in reference
    )
    assert (
        "| `modules` | 20 | 121 | 27 | `parameters:101`, `project:20` | `active`, `authoring_ready`, `collection_id`, `create`, `destination_source_root`, `diagnostic_code`, `edge_intents`, `encoding`, `family`, `family_id`,"
        in reference
    )
    assert (
        "| `surfaces` | 12 | 13 | 7 | `parameters:3`, `projections:1`, `selectors:9` | `values` |  | `binding_key`, `binding_surface`, `field_name`, `group_id`, `operation_id` | `form` |  |"
        in reference
    )
    assert "| `lsp` | 7 | 30 | 6 | 0 | 6 | `lsp.completion`, `lsp.hover` |  | `character`, `limit`, `line`, `offset` |" in reference
    assert "| `surfaces` | 12 | 13 | 1 | 1 | 0 | `surface.frontend_api.binding_lookup` | `binding_surface` |  |" in reference
    assert (
        "| `catalog` | 4 | 17 | 7 | 0 | `catalog.preview`, `catalog.query`, `catalog.refresh`, `catalog.write` | "
        '`include_data`, `limit`, `offset`, `path` | `include_data=false`, `limit=100`, `offset=0`, `path="."` |' in reference
    )
    assert (
        "| `surfaces` | 12 | 13 | 4 | 0 | `surface.frontend_api`, `surface.frontend_api.normalize`, `surface.frontend_api.options`, `surface.frontend_api.rest_request` | `form`, `values` | `form=false`, `values={}` |"
        in reference
    )
    assert (
        "| `modules` | 20 | 121 | 27 | `module.activity.set`, `module.authoring_path`, `module.authoring_plan`, `module.collection.set`, `module.create`, `module.create_batch`, `module.diagram`, `module.diagram.edit`, `module.draft`, `module.duplicate`, `module.edit`, `module.file`, `module.remove`, `module.rename`, `module.view` | `active`, `family`, `family_id`, `module_id`, `modules`, `object_id`, `project_id`, `relative_path`, `target_id`, `template_id`, `text` | `parameters:27` | `build.families`, `module.list`, `module.sources`, `module.templates` |  |"
        in reference
    )
    assert (
        "| `surfaces` | 12 | 13 | 7 | `surface.frontend_api.action`, `surface.frontend_api.binding_lookup`, `surface.frontend_api.normalize`, `surface.frontend_api.options`, `surface.frontend_api.rest_request` | `binding_key`, `binding_surface`, `field_name`, `operation_id` | `selectors:7` |  |  |"
        in reference
    )
    assert (
        "| `projects` | 15 | 46 | 5 | `project.draft_apply`, `project.source_form`, `project.source_text` | `path`, `source_path` | `parameters` | `module.sources` | `path->project_root`, `source_path->path` |"
        in reference
    )
    assert "| `build` | 18 | 104 | 1 | `build.artifacts` | `artifact_path` | `parameters` | `build.artifacts` | `artifact_path->path` |" in reference
    assert "| `project-switcher` | 8 | 7 | 7 | 7 | 5 | 0 | 1 | 0 | `frontend-local:1`, `rest:7` |" in reference
    assert "| `source-editor` | 16 | 16 | 8 | 16 | 7 | 6 | 0 | 0 | `rest:16` |" in reference
    assert "| `surface-contracts` | 12 | 12 | 8 | 8 | 2 | 0 | 0 | 0 | `rest:8`, `sdk:4` |" in reference
    assert (
        "| `project-switcher` | 8 | 8 | `adapter:7`, `frontend-local:1` | `frontend-local:1`, `rest:7` | `cli:7`, `mcp:5`, `rest:7`, `sdk:7` | 8 | 3 | `workspace:1` | 8 | 7 |"
        in reference
    )
    assert "| `source-editor` | 16 | 16 | `adapter:16` | `rest:16` | `cli:8`, `lsp:6`, `mcp:7`, `rest:16`, `sdk:16` | 16 | 5 |  | 16 | 16 |" in reference
    assert (
        "| `project-switcher` | 8 | 7 | `Project.create`, `Project.find`, `Project.load`, `Project.rename`, `Project.set_preferred_language`, `desktop_state`, `registered_projects` | `desktop-state`, `new`, `project`, `project-find`, `project-language`, `project-rename`, `projects` | `GET /desktop/state`, `GET /projects`, `GET /projects/find`, `GET /projects/list`, `PATCH /projects/language`, `PATCH /projects/rename`, `POST /projects` | `project_create`, `project_find`, `project_open`, `project_preferred_language`, `project_rename` |  | `project.activate` |"
        in reference
    )
    assert "| `project-switcher` | Project Switcher | 8 | 21 | 4 | 11 | 0 | 0 | 1 | `checkbox:2`, `json:4`, `path:6`, `select:1`, `text:8` |" in reference
    assert (
        "| `source-editor` | Source Editor | 16 | 77 | 28 | 21 | 5 | 16 | 6 | `checkbox:7`, `combobox:16`, `json:4`, `number:6`, `path:19`, `text:16`, `textarea:9` |"
        in reference
    )
    assert "| `surface-contracts` | Surface Contracts | 12 | 13 | 7 | 4 | 0 | 0 | 1 | `checkbox:1`, `json:3`, `select:1`, `text:8` |" in reference
    assert (
        "| `source-editor` | 16 | 77 | 7 | 16 | 0 | `checkbox:7`, `combobox:16`, `json:4`, `number:6`, `path:19`, `text:16`, `textarea:9` | `collection_id`, `family`, `module_id`, `relative_path`, `source_path`, `source_root` |  | `text` |"
        in reference
    )
    assert "| `surface-contracts` | 12 | 13 | 4 | 0 | 1 | `checkbox:1`, `json:3`, `select:1`, `text:8` |  | `binding_surface` |  |" in reference
    assert (
        "| `projects` | 15 | 46 | 7 | 5 | 3 | `checkbox:2`, `combobox:5`, `json:8`, `path:12`, `select:3`, `text:15`, `textarea:1` | `collection_id`, `family`, `module_id`, `source_path` | `kind`, `preferred_language` | `text` |"
        in reference
    )
    assert (
        "| `build` | 18 | 104 | 7 | 33 | 7 | `checkbox:7`, `combobox:33`, `json:1`, `number:1`, `path:16`, `select:7`, `text:39` | `artifact_path`, `artifact_type`, `code`, `collection_id`, `diagnostic_code`, `family`, `module_id`, `source_path` | `mode`, `severity`, `target_root` |  |"
        in reference
    )
    assert (
        "| `project-browser` | 9 | 22 | 9 | 3 | `build.families`, `collection.list`, `module.list` | `collections`, `families`, `modules` | `path` | `collection_id`, `family`, `module_id`, `path`, `profile` |  |"
        in reference
    )
    assert (
        "| `authoring` | 21 | 40 | 19 | 5 | `build.diagnostics`, `build.families`, `collection.list`, `module.list`, `module.templates` | `collections`, `diagnostics`, `families`, `modules`, `source_roots`, `templates` | `path` | `collection_id`, `family`, `module_id`, `path`, `profile`, `severity`, `slot`, `source_path`, `strict_metadata` | `authoring_ready=true` |"
        in reference
    )
    assert (
        "| `source-editor` | 16 | 16 | 6 | 6 | `build.families`, `collection.list`, `collection.sources`, `module.list`, `module.sources`, `module.templates` | `collections`, `families`, `modules`, `source_roots`, `sources` | `collection_id`, `module_id`, `path` | `collection_id`, `family`, `loader`, `module_id`, `path`, `profile`, `slot`, `status` |  |"
        in reference
    )
    assert (
        "| `project-browser` | 9 | 54 | 2 | `parameters:46`, `project:8` | `collection_id`, `family`, `kind`, `loader`, `module_id`, `owner_kind`, `path`, `profile`, `slot`, `source_slot`, `status` | `path` |  |  |  |"
        in reference
    )
    assert (
        "| `authoring` | 21 | 131 | 37 | `parameters:112`, `project:19` | `active`, `authoring_ready`, `collection_id`, `diagnostic_code`, `drafts`, `edge_intents`, `family`, `family_id`, `force`, `kind`, `limit`, `metadata`, `module_id`, `modules`, `node_intents`, `object_id`, `operation`, `path`, `plan_hash`, `position_intents`, `profile`, `project_id`, `source`, `source_root`, `target_id`, `target_kind`, `template_id`, `title`, `values`, `write` | `path` |  |  | `path->project_root` |"
        in reference
    )
    assert (
        "| `source-editor` | 16 | 77 | 28 | `parameters:73`, `project:4` | `character`, `collection_id`, `comments`, `create`, `database`, `encoding`, `family`, `game_root`, `include_dump`, `include_tokens`, `indent`, `limit`, `line`, `module_id`, `module_rename`, `offset`, `path`, `project_id`, `project_path`, `query`, `relative_path`, `source_edits`, `source_path`, `source_removals`, `source_replacements`, `source_root`, `text`, `uri`, `write` | `path` |  |  | `path->project_root`, `source_path->path` |"
        in reference
    )
    assert (
        "| `project-browser` | 9 | 54 | 6 | 6 | 0 | `collection.source_slots`, `collection.sources`, `module.source_slots`, `module.sources`, `project.browser` | `kind`, `owner_kind`, `status` |  |"
        in reference
    )
    assert (
        "| `authoring` | 21 | 131 | 7 | 7 | 0 | `collection.authoring_path`, `collection.authoring_plan`, `localization.plan`, `localization.workspace`, `module.authoring_path`, `module.authoring_plan`, `module.templates` | `kind`, `target_kind` |  |"
        in reference
    )
    assert "| `source-editor` | 16 | 77 | 6 | 0 | 6 | `lsp.completion`, `lsp.hover` |  | `character`, `limit`, `line`, `offset` |" in reference
    assert (
        '| `project-switcher` | 8 | 21 | 11 | 0 | `project.create`, `project.find`, `project.language`, `project.list`, `project.open`, `project.rename`, `project.state` | `force`, `game`, `path`, `project_paths`, `search_roots`, `write` | `force=false`, `game="hoi4"`, `path="."`, `project_paths=[]`, `search_roots=[]`, `write=false` |'
        in reference
    )
    assert (
        "| `source-editor` | 16 | 77 | 21 | 0 | `collection.edit`, `collection.file`, `lsp.completion`, `lsp.formatting`, `module.edit`, `module.file`, `pdx.format`, `pdx.parse`, `project.draft_apply`, `project.source_form`, `project.source_text` | `comments`, `create`, `encoding`, `include_dump`, `include_tokens`, `indent`, `limit`, `path`, `write` |"
        in reference
    )
    assert (
        "| `surface-contracts` | 12 | 13 | 4 | 0 | `surface.frontend_api`, `surface.frontend_api.normalize`, `surface.frontend_api.options`, `surface.frontend_api.rest_request` | `form`, `values` | `form=false`, `values={}` |"
        in reference
    )
    assert (
        "| `authoring` | 21 | 131 | 37 | `collection.authoring_path`, `collection.authoring_plan`, `collection.create`, `collection.remove`, `collection.rename`, `collection.scaffold`, `localization.plan`, `localization.workspace`, `module.activity.set`, `module.authoring_path`, `module.authoring_plan`, `module.collection.set`, `module.create`, `module.create_batch`, `module.diagram`, `module.diagram.edit`, `module.draft`, `module.remove`, `module.rename` | `active`, `collection_id`, `family`, `family_id`, `module_id`, `modules`, `object_id`, `operation`, `project_id`, `target_id`, `target_kind`, `template_id` | `parameters:37` | `build.families`, `collection.list`, `module.list`, `module.templates` |  |"
        in reference
    )
    assert (
        "| `source-editor` | 16 | 77 | 28 | `collection.edit`, `collection.file`, `lsp.completion`, `lsp.diagnostics`, `lsp.formatting`, `lsp.hover`, `lsp.semantic_tokens`, `lsp.symbols`, `module.edit`, `module.file`, `pdx.format`, `pdx.parse`, `project.draft_apply`, `project.source_form`, `project.source_text` | `character`, `collection_id`, `line`, `module_id`, `path`, `project_id`, `relative_path`, `source_path`, `text` | `parameters:28` | `collection.list`, `collection.sources`, `module.list`, `module.sources` | `source_path->path` |"
        in reference
    )
    assert (
        "| `surface-contracts` | 12 | 13 | 7 | `surface.frontend_api.action`, `surface.frontend_api.binding_lookup`, `surface.frontend_api.normalize`, `surface.frontend_api.options`, `surface.frontend_api.rest_request` | `binding_key`, `binding_surface`, `field_name`, `operation_id` | `selectors:7` |  |  |"
        in reference
    )
    assert (
        "| `authoring` | 21 | 131 | 8 | `localization.plan`, `localization.workspace`, `module.activity.set`, `module.collection.set`, `module.create_batch`, `module.diagram.edit`, `module.draft`, `module.metadata.clean` | `path` | `parameters`, `project` |  | `path->project_root` |"
        in reference
    )
    assert (
        "| `source-editor` | 16 | 77 | 5 | `project.draft_apply`, `project.source_form`, `project.source_text` | `path`, `source_path` | `parameters` | `module.sources` | `path->project_root`, `source_path->path` |"
        in reference
    )
    assert (
        "| `project-switcher` | `project.state` | `adapter` | `rest` | `sdk`, `cli`, `rest` | yes |  | `paradev.sdk.frontend-api.inputs.v1` | `paradev.sdk.frontend-api.rest-request.v1` |"
        in reference
    )
    assert (
        "| `project-switcher` | `project.activate` | `frontend-local` | `frontend-local` |  | yes | `workspace` | `paradev.sdk.frontend-api.inputs.v1` |  |"
        in reference
    )
    assert (
        "| `surface-contracts` | `surface.frontend_api.workspace` | `adapter` | `rest` | `sdk`, `cli`, `rest` | no |  |  | `paradev.sdk.frontend-api.rest-request.v1` |"
        in reference
    )
    assert (
        "| `project-switcher` | 8 | 3 | `project-files:3` | `write:3` | `force:1`, `write:1` | `project.create`, `project.rename`, `project.language` |"
        in reference
    )
    assert (
        "| `authoring` | 21 | 13 | `project-files:13` | `destructive:2`, `write:11` | `force:4`, `write:11` | `module.diagram.edit`, `module.create`, `module.create_batch`, `module.draft`, `module.rename`, `module.collection.set`, `module.activity.set`, `module.metadata.clean`, `module.remove`, `collection.scaffold`, `collection.create`, `collection.rename`, `collection.remove` |"
        in reference
    )
    assert (
        "| `source-editor` | 16 | 5 | `project-files:5` | `write:5` | `create:2`, `write:1` | `module.edit`, `collection.edit`, `project.draft_apply`, `pdx.format`, `lsp.formatting` |"
        in reference
    )
    assert "| `project-switcher` | `project-files` | `write` | `force` | `project.create` | Confirm Project Create |" in reference
    assert "| `authoring` | `project-files` | `destructive` | `write` | `module.remove` | Confirm Module Remove |" in reference
    assert "| `build` | `project-files` | `write` | `emit_artifacts`, `emit_manifests` | `build.emit` | Confirm Build Emit |" in reference
    assert "| `catalog` | `catalog` | `write` |  | `catalog.refresh` | Confirm Catalog Refresh |" in reference
    assert "| `module.create` | `template_id` | `templates` | `module.templates` | `path` | `path` | `authoring_ready=true` |" in reference
    assert (
        "| `collection.sources` | 2 | `collection.file.relative_path`, `collection.edit.relative_path` | `collection.edit`, `collection.file` | `sources` | `collection_id`, `path` | `collection_id`, `family`, `loader`, `path`, `profile`, `slot`, `status` |  |"
        in reference
    )
    assert (
        "| `build.artifacts` | 6 | `build.artifacts.artifact_type`, `build.artifacts.artifact_path`, `build.source_map.artifact_type`, `build.graph.artifact_type`, `build.explain.artifact_path`, `build.families.artifact_type` | `build.artifacts`, `build.explain`, `build.families`, `build.graph`, `build.source_map` | `artifacts` | `path` | `artifact_type`, `collection_id`, `mode`, `module_id`, `owner`, `path`, `profile`, `target_root` |  |"
        in reference
    )
    assert "| `module.templates` | 25 |" in reference
    assert "`authoring_ready=true` |" in reference
    assert (
        "| `module.edit` | `relative_path` | `sources` | `module.sources` | `path`, `module_id` | `path`, `profile`, `module_id`, `family`, `collection_id`, `slot`, `loader`, `status` |  |"
        in reference
    )
    assert (
        "| `build.diagnostics` | `code` | `diagnostics` | `build.diagnostics` | `path` | `path`, `profile`, `severity`, `family`, `module_id`, `collection_id`, `source_path`, `slot`, `strict_metadata` |  |"
        in reference
    )
    assert "| `path` | `module.create` | `path` | no | `.` |  |  |  |" in reference
    assert "| `template_id` | `module.create` | `string` | yes |  |  |  | `module.templates` |" in reference
    assert "| `write` | `module.create` | `boolean` | no | `false` |  |  |  |" in reference
    assert "| `severity` | `build.diagnostics` | `string` | no |  | `error`, `warning` |  |  |" in reference
    assert "| `artifact_path` | `build.artifacts` | `path` | no |  |  | `path` | `build.artifacts` |" in reference
    assert "| `line` | `lsp.hover` | `integer` | yes |  |  |  |  |" in reference
    assert (
        "| `projects` | Projects | 15 | 46 | 10 | 18 | 5 | 5 | 3 | `checkbox:2`, `combobox:5`, `json:8`, `path:12`, `select:3`, `text:15`, `textarea:1` |"
        in reference
    )
    assert (
        "| `modules` | Modules | 20 | 121 | 27 | 40 | 7 | 45 | 6 | `checkbox:14`, `combobox:45`, `json:6`, `path:20`, `select:6`, `text:29`, `textarea:1` |"
        in reference
    )
    assert (
        "| `build` | Build | 18 | 104 | 3 | 18 | 1 | 33 | 10 | `checkbox:7`, `combobox:33`, `json:1`, `number:1`, `path:16`, `select:7`, `text:39` |"
        in reference
    )
    assert "| `lsp` | LSP | 7 | 30 | 10 | 3 | 0 | 0 | 6 | `checkbox:1`, `number:6`, `path:10`, `text:7`, `textarea:6` |" in reference
    assert "| `project.create` | 5 | 1 | 2 | 0 | 0 | 0 | `checkbox`, `path`, `text` |" in reference
    assert "| `module.create` | 7 | 2 | 3 | 0 | 2 | 0 | `checkbox`, `combobox`, `json`, `path`, `text` |" in reference
    assert "| `build.artifacts` | 9 | 0 | 1 | 1 | 4 | 1 | `combobox`, `path`, `select`, `text` |" in reference
    assert "| `lsp.hover` | 5 | 3 | 0 | 0 | 0 | 2 | `number`, `path`, `text`, `textarea` |" in reference
    assert "| `template_id` | `module.create` | `combobox` | `string` | yes | `module.templates` |  |" in reference
    assert "| `kind` | `project.browser` | `select` | `string` | no |  | `module`, `collection` |" in reference
    assert "| `text` | `module.edit` | `textarea` | `text` | yes |  |  |" in reference
    assert "| `project_paths` | `project.list` | `json` | `array` | no |  |  |" in reference
    assert "| `line` | `lsp.hover` | `number` | `integer` | yes |  |  |" in reference
    assert "| `force` | `project.create` | `checkbox` | `boolean` | no |  |  |" in reference
    assert "| `artifact_path` | `build.artifacts` | `combobox` | `path` | no | `build.artifacts` |  |" in reference
    assert "| `path` | `project.create` | `path` | `parameters` |  |  |" in reference
    assert "| `template_id` | `module.create` | `string` | `parameters` |  | `module.templates` |" in reference
    assert "| `source_path` | `project.source_text` | `path` | `parameters` | `path` | `module.sources` |" in reference
    assert "| `line` | `lsp.hover` | `integer` | `parameters` |  |  |" in reference
    assert "| `operation_id` | `surface.frontend_api.action` | `string` | `selectors` |  |  |" in reference
    assert "| `binding_surface` | `surface.frontend_api.binding_lookup` | `string` | `selectors` |  |  |" in reference
    assert "| `path` | `project.find` | `path` | `.` | `parameters` |  | no |" in reference
    assert "| `force` | `project.create` | `boolean` | `false` | `parameters` |  | no |" in reference
    assert "| `project_paths` | `project.list` | `array` | `[]` | `parameters` |  | no |" in reference
    assert "| `path` | `project.source_text` | `path` | `.` | `parameters` | `project_root` | no |" in reference
    assert "| `form` | `surface.frontend_api` | `boolean` | `false` | `projections` |  | no |" in reference
    assert "| `kind` | `project.browser` | `string` | `module`, `collection` |  |  | no | no |" in reference
    assert "| `target_root` | `build.artifacts` | `string` | `output`, `build` |  |  | no | no |" in reference
    assert "| `severity` | `build.diagnostics` | `string` | `error`, `warning` |  |  | no | no |" in reference
    assert "| `run_id` | `build.status` | `string` |  |  |  | yes | yes |" in reference
    assert "| `run_id` | `build.interrupt` | `string` |  |  |  | yes | yes |" in reference
    assert "| `line` | `lsp.hover` | `integer` |  | `0` |  | no | yes |" in reference
    assert "| `offset` | `lsp.completion` | `integer` |  | `0` |  | no | no |" in reference
    assert "| `limit` | `catalog.query` | `integer` |  | `1` | `200` | no | no |" in reference
    assert "| `project` | `path` | `module.create` |  | `path` | no |" in reference
    assert "| `parameters` | `path` | `project.source_text` | `project_root` | `path` | no |" in reference
    assert "| `parameters` | `source_path` | `project.source_text` | `path` | `path` | yes |" in reference
    assert "| `selectors` | `operation_id` | `surface.frontend_api` |  | `string` | no |" in reference
    assert "| `projections` | `form` | `surface.frontend_api` |  | `boolean` | no |" in reference
    assert "| `parameters` | `artifact_path` | `build.artifacts` | `path` | `path` | no |" in reference
    assert "| `path` | `project.source_text` | `path` | `parameters` | `project_root` | no |  |" in reference
    assert "| `source_path` | `project.source_text` | `path` | `parameters` | `path` | yes | `module.sources` |" in reference
    assert "| `path` | `module.draft` | `path` | `project` | `project_root` | no |  |" in reference
    assert "| `artifact_path` | `build.artifacts` | `path` | `parameters` | `path` | no | `build.artifacts` |" in reference
    for operation in operations:
        marker = f"| `{operation['id']}` | `{operation['group']}` |"
        assert reference.count(f"\n{marker}") == 1

    manual = Path("docs/user-manual/frontend-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference


def test_frontend_api_sdk_cli_reference_manual_matches_sdk_renderer() -> None:
    from paradev.sdk import (
        get_frontend_api_contract,
        render_frontend_api_sdk_cli_markdown,
    )

    reference = render_frontend_api_sdk_cli_markdown()
    operations = get_frontend_api_contract()["operations"]

    assert reference.startswith("# SDK And CLI API Reference\n")
    assert "Generated from `paradev.sdk.get_frontend_api_contract()`." in reference
    assert "## 中文" in reference
    assert "## Feature Summary / 功能汇总" in reference
    assert "Operation Matrix / 操作矩阵" in reference
    assert "| `modules` | Modules | 20 | 20 | 19 | 9 | 11 |" in reference
    assert "| `localization` | Localization | 2 | 2 | 0 | 2 | 0 |" in reference
    assert "| `lsp` | LSP | 7 | 7 | 1 | 6 | 1 |" in reference
    assert "| `surfaces` | Surfaces | 12 | 12 | 8 | 12 | 0 |" in reference
    for operation in operations:
        marker = f"| `{operation['id']}` |"
        assert reference.count(marker) == 1

    manual = Path("docs/user-manual/sdk-cli-reference.md").read_text(encoding="utf-8")
    assert manual == reference


def test_frontend_api_lookup_helpers_return_canonical_rows() -> None:
    from paradev.sdk import (
        get_frontend_api_contract,
        get_frontend_api_group,
        get_frontend_api_operation,
    )

    contract = get_frontend_api_contract()
    rows = {row["id"]: row for row in contract["operations"]}

    module_list = get_frontend_api_operation("module.list")
    assert module_list == rows["module.list"]
    assert module_list["rest"] == "GET /projects/inspect?kind=modules"

    module_group = get_frontend_api_group("modules")
    assert module_group["schema"] == "paradev.sdk.frontend-api.v1"
    assert module_group["sdk_owned"] is True
    assert module_group["group"]["id"] == "modules"
    assert module_group["operation_ids"] == contract["index"]["group"]["modules"]
    assert [row["id"] for row in module_group["operations"]] == contract["index"]["group"]["modules"]
    assert "module.edit" in module_group["index"]["status"]["implemented"]

    contract["groups"][0]["id"] = "changed"
    module_list["summary"] = "changed"
    assert get_frontend_api_group("projects")["group"]["id"] == "projects"
    assert get_frontend_api_operation("module.list")["summary"] == rows["module.list"]["summary"]

    with pytest.raises(ValueError, match="Unknown frontend API operation: nope"):
        get_frontend_api_operation("nope")
    with pytest.raises(ValueError, match="Unknown frontend API group: nope"):
        get_frontend_api_group("nope")


def test_frontend_api_surface_bindings_are_machine_readable() -> None:
    from paradev.sdk import get_frontend_api_contract

    rows = {row["id"]: row for row in get_frontend_api_contract()["operations"]}

    for row in rows.values():
        expected = {key for key in ("sdk", "cli", "rest", "mcp", "lsp") if key in row}
        if expected:
            assert set(row["bindings"]) == expected
        else:
            assert "bindings" not in row

    assert rows["module.list"]["bindings"] == {
        "sdk": {"call": "Project.inspect('modules')"},
        "cli": {"command": "modules"},
        "rest": {
            "method": "GET",
            "path": "/projects/inspect",
            "query": {"kind": "modules"},
        },
        "mcp": {"tool": "project_inspect"},
    }
    assert rows["project.list"]["bindings"] == {
        "sdk": {"call": "registered_projects"},
        "cli": {"command": "projects"},
        "rest": {"method": "GET", "path": "/projects/list", "query": {}},
    }
    assert rows["project.state"]["bindings"] == {
        "sdk": {"call": "desktop_state"},
        "cli": {"command": "desktop-state"},
        "rest": {"method": "GET", "path": "/desktop/state", "query": {}},
    }
    assert rows["project.browser"]["bindings"] == {
        "sdk": {"call": "Project.browser"},
        "cli": {"command": "project-browser"},
        "rest": {"method": "GET", "path": "/projects/browser", "query": {}},
        "mcp": {"tool": "project_browser"},
    }
    assert rows["build.emit"]["bindings"]["rest"] == {
        "method": "POST",
        "path": "/projects/build",
        "query": {"emit_artifacts": True, "emit_manifests": True},
    }
    assert rows["build.start"]["bindings"] == {
        "sdk": {"call": "desktop_start_build"},
        "rest": {"method": "POST", "path": "/desktop/builds", "query": {}},
    }
    assert rows["build.runs"]["bindings"] == {
        "sdk": {"call": "desktop_build_runs"},
        "rest": {"method": "GET", "path": "/desktop/builds", "query": {}},
    }
    assert rows["build.status"]["bindings"] == {
        "sdk": {"call": "desktop_build_status"},
        "rest": {"method": "GET", "path": "/desktop/builds/status", "query": {}},
    }
    assert rows["build.interrupt"]["bindings"] == {
        "sdk": {"call": "desktop_interrupt_build"},
        "rest": {"method": "POST", "path": "/desktop/builds/interrupt", "query": {}},
    }
    assert rows["lsp.hover"]["bindings"]["lsp"] == {"method": "textDocument/hover"}
    assert rows["lsp.completion"]["bindings"]["lsp"] == {"method": "textDocument/completion"}
    assert rows["lsp.semantic_tokens"]["bindings"]["lsp"] == {"method": "textDocument/semanticTokens/full"}
    assert rows["lsp.keywords"]["bindings"] == {
        "sdk": {"call": "hoi4_keyword_dataset"},
        "cli": {"command": "lsp keywords"},
        "rest": {"method": "GET", "path": "/lsp/keywords", "query": {}},
    }
    assert rows["surface.frontend_api.normalize"]["bindings"]["rest"] == {
        "method": "POST",
        "path": "/frontend-api/normalize",
        "query": {},
    }
    assert rows["surface.frontend_api.rest_request"]["bindings"]["rest"] == {
        "method": "POST",
        "path": "/frontend-api/rest-request",
        "query": {},
    }
    assert rows["catalog.write"]["bindings"] == {
        "sdk": {"call": "paradev.hb.catalog_write"},
        "cli": {"command": "hb catalog-write"},
        "rest": {"method": "POST", "path": "/projects/catalog", "query": {}},
    }
    assert rows["catalog.refresh"]["bindings"] == {
        "sdk": {"call": "paradev.hb.catalog_refresh"},
        "cli": {"command": "hb catalog-refresh"},
        "rest": {"method": "PUT", "path": "/projects/catalog", "query": {}},
    }
    assert "bindings" not in rows["project.activate"]


def test_frontend_api_binding_index_maps_surface_calls_to_operation_ids() -> None:
    from paradev.sdk import get_frontend_api_contract

    contract = get_frontend_api_contract()
    binding_index = contract["index"]["binding"]

    assert binding_index["cli"]["project"] == ["project.open", "project.view"]
    assert binding_index["cli"]["projects"] == ["project.list"]
    assert binding_index["cli"]["desktop-state"] == ["project.state"]
    assert binding_index["cli"]["project-browser"] == ["project.browser"]
    assert binding_index["cli"]["templates"] == ["module.templates"]
    assert binding_index["cli"]["draft-apply"] == ["project.draft_apply"]
    assert binding_index["cli"]["frontend-api --workspace"] == ["surface.frontend_api.workspace"]
    assert binding_index["cli"]["frontend-api --operation --action"] == ["surface.frontend_api.action"]
    assert binding_index["cli"]["frontend-api --operation --values-json --rest-request"] == ["surface.frontend_api.rest_request"]
    assert binding_index["cli"]["frontend-api --operation --option-field --values-json"] == ["surface.frontend_api.options"]
    assert binding_index["cli"]["frontend-api --binding-surface --binding-key"] == ["surface.frontend_api.binding_lookup"]
    assert binding_index["mcp"]["project_inspect"][:5] == [
        "project.inspect",
        "module.list",
        "module.view",
        "module.source_slots",
        "module.sources",
    ]
    assert binding_index["mcp"]["project_browser"] == ["project.browser"]
    assert binding_index["mcp"]["project_templates"] == ["module.templates"]
    assert "catalog.query" in binding_index["mcp"]["project_inspect"]
    assert binding_index["rest"]["GET /projects"] == ["project.open", "project.view"]
    assert binding_index["rest"]["GET /projects/list"] == ["project.list"]
    assert binding_index["rest"]["GET /desktop/state"] == ["project.state"]
    assert binding_index["rest"]["GET /projects/browser"] == ["project.browser"]
    assert binding_index["rest"]["GET /projects/{project_id}/sources"] == ["project.source_text"]
    assert binding_index["rest"]["POST /projects/{project_id}/drafts/apply"] == ["project.draft_apply"]
    assert binding_index["rest"]["GET /projects/templates"] == ["module.templates"]
    assert binding_index["rest"]["POST /projects/{project_id}/modules/{family_id}/drafts"] == ["module.draft"]
    assert binding_index["rest"]["GET /frontend-api/workspace"] == ["surface.frontend_api.workspace"]
    assert binding_index["rest"]["GET /frontend-api/action"] == ["surface.frontend_api.action"]
    assert binding_index["rest"]["POST /frontend-api/options"] == ["surface.frontend_api.options"]
    assert binding_index["rest"]["GET /frontend-api/binding"] == ["surface.frontend_api.binding_lookup"]
    assert binding_index["rest"]["GET /lsp/keywords"] == ["lsp.keywords"]
    assert binding_index["rest"]["GET /projects/inspect?kind=modules"] == ["module.list"]
    assert binding_index["rest"]["GET /projects/inspect?kind=assets"] == ["build.assets"]
    assert binding_index["rest"]["GET /projects/inspect?kind=sprites"] == ["build.sprites"]
    assert binding_index["rest"]["POST /projects/catalog"] == ["catalog.write"]
    assert binding_index["cli"]["lsp keywords"] == ["lsp.keywords"]
    assert binding_index["lsp"]["textDocument/hover"] == ["lsp.hover"]
    assert binding_index["lsp"]["textDocument/completion"] == ["lsp.completion"]
    assert binding_index["lsp"]["textDocument/semanticTokens/full"] == ["lsp.semantic_tokens"]


def test_frontend_api_binding_lookup_helpers_return_operation_ids() -> None:
    from paradev.sdk import (
        build_frontend_api_rest_index_key,
        get_frontend_api_binding_index,
        get_frontend_api_binding_lookup,
        get_frontend_api_binding_operation_ids,
        get_frontend_api_contract,
        get_frontend_api_group_operation_ids,
        get_frontend_api_mode_operation_ids,
        get_frontend_api_payload_operation_ids,
        get_frontend_api_rest_operation_ids,
        get_frontend_api_status_operation_ids,
        get_frontend_api_surface_operation_ids,
        get_frontend_api_workspace_section_operation_ids,
        plan_frontend_api_rest_request,
    )

    contract = get_frontend_api_contract()

    assert get_frontend_api_binding_operation_ids("cli", "project") == [
        "project.open",
        "project.view",
    ]
    assert get_frontend_api_binding_operation_ids("mcp", "project_templates") == ["module.templates"]
    assert get_frontend_api_binding_operation_ids("cli", "lsp keywords") == ["lsp.keywords"]
    assert get_frontend_api_binding_operation_ids("lsp", "textDocument/formatting") == ["lsp.formatting"]
    assert get_frontend_api_binding_operation_ids("lsp", "textDocument/completion") == ["lsp.completion"]
    assert get_frontend_api_binding_operation_ids("rest", "GET /lsp/keywords") == ["lsp.keywords"]
    assert get_frontend_api_binding_operation_ids("rest", "GET /projects/inspect?kind=modules") == ["module.list"]
    assert get_frontend_api_binding_operation_ids("rest", "GET /missing") == []
    assert get_frontend_api_binding_index("cli")["project"] == [
        "project.open",
        "project.view",
    ]
    assert get_frontend_api_binding_index("mcp")["project_templates"] == ["module.templates"]
    assert get_frontend_api_group_operation_ids("lsp") == [
        "lsp.diagnostics",
        "lsp.symbols",
        "lsp.hover",
        "lsp.formatting",
        "lsp.completion",
        "lsp.semantic_tokens",
        "lsp.keywords",
    ]
    assert get_frontend_api_status_operation_ids("frontend-local") == ["project.activate"]
    assert get_frontend_api_mode_operation_ids("write")[:6] == [
        "project.create",
        "project.config",
        "project.rename",
        "project.language",
        "project.activate",
        "project.draft_apply",
    ]
    assert get_frontend_api_surface_operation_ids("unbound") == ["project.activate"]
    assert get_frontend_api_surface_operation_ids("lsp") == [
        "lsp.diagnostics",
        "lsp.symbols",
        "lsp.hover",
        "lsp.formatting",
        "lsp.completion",
        "lsp.semantic_tokens",
    ]
    assert get_frontend_api_payload_operation_ids("Project.to_view") == [
        "project.open",
        "project.view",
    ]
    assert get_frontend_api_payload_operation_ids("missing.payload") == []
    assert get_frontend_api_workspace_section_operation_ids("catalog") == [
        "catalog.preview",
        "catalog.write",
        "catalog.refresh",
        "catalog.query",
    ]
    assert get_frontend_api_binding_lookup("rest", "GET /projects/inspect?kind=modules") == {
        "schema": "paradev.sdk.frontend-api.binding-lookup.v1",
        "surface": "rest",
        "key": "GET /projects/inspect?kind=modules",
        "operation_ids": ["module.list"],
        "count": 1,
    }
    binding_plan = plan_frontend_api_rest_request(
        "surface.frontend_api.binding_lookup",
        {
            "binding_surface": "rest",
            "binding_key": "GET /projects/inspect?kind=modules",
        },
    )
    assert binding_plan["schema"] == "paradev.sdk.frontend-api.rest-request.v1"
    assert binding_plan["operation_id"] == "surface.frontend_api.binding_lookup"
    assert binding_plan["method"] == "GET"
    assert binding_plan["path"] == "/frontend-api/binding"
    assert binding_plan["query"] == {
        "binding_surface": "rest",
        "binding_key": "GET /projects/inspect?kind=modules",
    }
    assert binding_plan["body"] == {}
    assert binding_plan["binding"] == {
        "method": "GET",
        "path": "/frontend-api/binding",
        "query": {},
    }
    assert binding_plan["normalized"]["selectors"] == {
        "binding_surface": "rest",
        "binding_key": "GET /projects/inspect?kind=modules",
    }
    assert binding_plan["normalized"]["parameters"] == {}

    rest_key = build_frontend_api_rest_index_key(
        "POST",
        "/projects/build",
        {"emit_manifests": True, "emit_artifacts": True},
    )
    assert rest_key == "POST /projects/build?emit_artifacts=true&emit_manifests=true"
    assert get_frontend_api_rest_operation_ids(
        "POST",
        "/projects/build",
        {"emit_manifests": True, "emit_artifacts": True},
    ) == ["build.emit"]

    result = get_frontend_api_binding_operation_ids("rest", "GET /projects")
    result.append("changed")
    assert contract["index"]["binding"]["rest"]["GET /projects"] == [
        "project.open",
        "project.view",
    ]
    result_index = get_frontend_api_binding_index("cli")
    result_index["project"].append("changed")
    result_index["__changed__"] = ["changed"]
    assert contract["index"]["binding"]["cli"]["project"] == [
        "project.open",
        "project.view",
    ]
    assert "__changed__" not in contract["index"]["binding"]["cli"]
    result = get_frontend_api_group_operation_ids("projects")
    result.append("changed")
    assert contract["index"]["group"]["projects"][:3] == [
        "project.create",
        "project.find",
        "project.open",
    ]
    result = get_frontend_api_status_operation_ids("frontend-local")
    result.append("changed")
    assert contract["index"]["status"]["frontend-local"] == ["project.activate"]
    result = get_frontend_api_mode_operation_ids("write")
    result.append("changed")
    assert contract["index"]["mode"]["write"][:3] == [
        "project.create",
        "project.config",
        "project.rename",
    ]
    result = get_frontend_api_workspace_section_operation_ids("catalog")
    result.append("changed")
    assert contract["index"]["workspace_section"]["catalog"] == [
        "catalog.preview",
        "catalog.write",
        "catalog.refresh",
        "catalog.query",
    ]

    with pytest.raises(ValueError, match="Unsupported frontend API binding surface: gui"):
        get_frontend_api_binding_operation_ids("gui", "project")
    with pytest.raises(ValueError, match="Unsupported frontend API binding surface: gui"):
        get_frontend_api_binding_index("gui")
    with pytest.raises(ValueError, match="Unsupported frontend API surface: gui"):
        get_frontend_api_surface_operation_ids("gui")
    with pytest.raises(ValueError, match="Unknown frontend API group: nope"):
        get_frontend_api_group_operation_ids("nope")
    with pytest.raises(ValueError, match="Unknown frontend API status: deferred"):
        get_frontend_api_status_operation_ids("deferred")
    with pytest.raises(ValueError, match="Unknown frontend API mode: maybe"):
        get_frontend_api_mode_operation_ids("maybe")
    with pytest.raises(ValueError, match="Unknown frontend API workspace section: nope"):
        get_frontend_api_workspace_section_operation_ids("nope")


def test_frontend_api_index_catalog_documents_lookup_helpers() -> None:
    from paradev.sdk import get_frontend_api_index_catalog

    catalog = get_frontend_api_index_catalog()
    rows = {str(row["id"]): row for row in catalog}

    assert [row["id"] for row in catalog] == [
        "group",
        "status",
        "mode",
        "surface",
        "binding",
        "payload",
        "workspace_section",
    ]
    assert rows["group"] == {
        "id": "group",
        "contract_path": 'contract["index"]["group"][group_id]',
        "python_helper": "get_frontend_api_group_operation_ids(group_id)",
        "typescript_helper": "getFrontendApiGroupOperationIds(groupId)",
        "usage": "Group id to operation ids.",
    }
    assert rows["binding"] == {
        "id": "binding",
        "contract_path": 'contract["index"]["binding"][surface][key]',
        "python_helper": "get_frontend_api_binding_operation_ids(surface, key)",
        "typescript_helper": "getFrontendApiBindingOperationIds(surface, key)",
        "usage": "Surface call key to operation ids.",
    }
    assert rows["workspace_section"] == {
        "id": "workspace_section",
        "contract_path": 'contract["index"]["workspace_section"][section_id]',
        "python_helper": "get_frontend_api_workspace_section_operation_ids(section_id)",
        "typescript_helper": "getFrontendApiWorkspaceSectionOperationIds(sectionId)",
        "usage": "Workspace section id to operation ids.",
    }

    result = get_frontend_api_index_catalog()
    result[0]["id"] = "changed"
    assert get_frontend_api_index_catalog()[0]["id"] == "group"


def test_frontend_api_contract_indexes_every_surface_binding_and_openapi_annotation() -> None:
    from paradev.sdk import get_frontend_api_contract
    from paradev.surfaces.rest import get_openapi_seed

    contract = get_frontend_api_contract()
    operations = [row for row in contract["operations"] if isinstance(row, dict)]
    binding_index = contract["index"]["binding"]
    payload_index = contract["index"]["payload"]
    workspace_section_index = contract["index"]["workspace_section"]

    for section in contract["workspace"]["sections"]:
        assert workspace_section_index[section["id"]] == section["operation_ids"]

    def binding_key(surface: str, binding: dict[str, object]) -> str:
        if surface == "sdk":
            return str(binding["call"])
        if surface == "cli":
            return str(binding["command"])
        if surface == "mcp":
            return str(binding["tool"])
        if surface == "lsp":
            return str(binding["method"])
        if surface == "rest":
            method = str(binding["method"])
            path = str(binding["path"])
            query = binding.get("query", {})
            if not isinstance(query, dict) or not query:
                return f"{method} {path}"
            parts = []
            for key in sorted(query):
                value = query[key]
                parts.append(f"{key}={str(value).lower() if isinstance(value, bool) else value}")
            query_string = "&".join(parts)
            return f"{method} {path}?{query_string}"
        raise AssertionError(f"Unexpected frontend API surface: {surface}")

    for operation in operations:
        for surface, binding in operation.get("bindings", {}).items():
            assert isinstance(binding, dict)
            key = binding_key(str(surface), binding)
            assert operation["id"] in binding_index[str(surface)][key]
        payload = str(operation["payload"]) if operation.get("payload") else "untyped"
        assert operation["id"] in payload_index[payload]

    expected_rest_ids: dict[tuple[str, str], list[str]] = {}
    for operation in operations:
        rest = operation.get("bindings", {}).get("rest")
        if not isinstance(rest, dict):
            continue
        expected_rest_ids.setdefault((str(rest["path"]), str(rest["method"]).lower()), []).append(str(operation["id"]))

    seed = get_openapi_seed()
    for (path, method), operation_ids in expected_rest_ids.items():
        path_item = seed["paths"].get(path)
        assert isinstance(path_item, dict), path
        operation = path_item.get(method)
        assert isinstance(operation, dict), f"{method.upper()} {path}"
        assert operation["x-paradev-frontend-api-operation-ids"] == operation_ids


def test_frontend_api_form_contract_is_derived_from_operation_inputs() -> None:
    from paradev.sdk import get_frontend_api_form, get_frontend_api_operation

    build_artifacts = get_frontend_api_form("build.artifacts")

    assert build_artifacts["schema"] == "paradev.sdk.frontend-api.form.v1"
    assert build_artifacts["operation_id"] == "build.artifacts"
    assert build_artifacts["group"] == "build"
    assert build_artifacts["action"] == "artifacts"
    assert build_artifacts["read_only"] is True
    assert [field["name"] for field in build_artifacts["fields"]] == [
        "path",
        "profile",
        "artifact_type",
        "target_root",
        "owner",
        "artifact_path",
        "mode",
        "module_id",
        "collection_id",
    ]
    assert build_artifacts["required"] == []
    assert build_artifacts["defaults"] == {"path": "."}
    assert build_artifacts["aliases"] == {"artifact_path": "path"}
    assert build_artifacts["fields"][0]["label"] == "Path"
    assert "Project root" in build_artifacts["fields"][0]["description"]
    assert build_artifacts["fields"][0]["control"] == "path"
    assert build_artifacts["fields"][0]["target"] == "project"
    assert build_artifacts["fields"][3]["choices"] == ["output", "build"]
    assert build_artifacts["fields"][5]["label"] == "Artifact Path"
    assert "artifact" in build_artifacts["fields"][5]["description"].lower()
    assert build_artifacts["fields"][5]["maps_to"] == "path"
    assert build_artifacts["fields"][5]["target"] == "parameters"
    assert build_artifacts["json_schema"]["properties"]["path"] == {
        "type": "string",
        "format": "path",
        "default": ".",
    }
    assert build_artifacts["json_schema"]["properties"]["target_root"] == {
        "type": "string",
        "enum": ["output", "build"],
    }
    artifact_path_schema = build_artifacts["json_schema"]["properties"]["artifact_path"]
    assert {key: artifact_path_schema[key] for key in ("type", "format")} == {
        "type": "string",
        "format": "path",
    }
    assert artifact_path_schema["x-paradev-option-source"]["operation_id"] == "build.artifacts"
    assert build_artifacts["fields"][5]["control"] == "combobox"
    assert build_artifacts["json_schema"]["additionalProperties"] is False

    module_edit = get_frontend_api_form("module.edit")
    assert module_edit["operation"] == get_frontend_api_operation("module.edit")
    assert module_edit["mutates"] is True
    assert module_edit["required"] == ["module_id", "relative_path", "text"]
    assert module_edit["defaults"] == {
        "path": ".",
        "create": False,
        "encoding": "utf-8",
    }
    assert module_edit["fields"][0]["target"] == "project"
    assert module_edit["fields"][3]["label"] == "Text"
    assert "source file" in module_edit["fields"][3]["description"]
    assert module_edit["fields"][3]["control"] == "textarea"
    assert module_edit["json_schema"]["required"] == [
        "module_id",
        "relative_path",
        "text",
    ]

    lsp_hover = get_frontend_api_form("lsp.hover")
    assert lsp_hover["required"] == ["text", "line", "character"]
    assert lsp_hover["json_schema"]["properties"]["line"] == {
        "type": "integer",
        "minimum": 0,
    }
    assert lsp_hover["json_schema"]["properties"]["character"] == {
        "type": "integer",
        "minimum": 0,
    }
    assert lsp_hover["fields"][0]["control"] == "textarea"
    assert lsp_hover["fields"][1]["label"] == "Line"
    assert "Zero-based" in lsp_hover["fields"][1]["description"]
    assert lsp_hover["fields"][4]["target"] == "parameters"

    project_browser = get_frontend_api_form("project.browser")
    assert project_browser["fields"][2]["name"] == "kind"
    assert project_browser["fields"][2]["label"] == "Kind"
    assert "module or collection" in project_browser["fields"][2]["description"]
    assert project_browser["fields"][2]["control"] == "select"
    assert project_browser["fields"][2]["choices"] == ["module", "collection"]
    assert project_browser["json_schema"]["properties"]["kind"]["enum"] == [
        "module",
        "collection",
    ]

    project_state = get_frontend_api_form("project.state")
    assert project_state["defaults"] == {"project_paths": [], "search_roots": []}
    assert project_state["fields"][1]["control"] == "json"
    assert project_state["json_schema"]["properties"]["project_paths"] == {
        "type": "array",
        "items": {"type": "string"},
        "default": [],
    }

    module_create = get_frontend_api_form("module.create")
    module_create_fields = {field["name"]: field for field in module_create["fields"]}
    assert module_create_fields["template_id"]["control"] == "combobox"
    assert module_create_fields["template_id"]["option_source"]["operation_id"] == "module.templates"

    surface_form = get_frontend_api_form("surface.frontend_api")
    assert surface_form["fields"][0]["target"] == "selectors"
    assert surface_form["fields"][0]["label"] == "Operation ID"
    assert surface_form["fields"][1]["target"] == "selectors"
    assert surface_form["fields"][2]["target"] == "projections"

    with pytest.raises(ValueError, match="Unknown frontend API operation: nope"):
        get_frontend_api_form("nope")


def test_frontend_api_form_fields_expose_sdk_owned_option_sources() -> None:
    from paradev.sdk import FRONTEND_API_OPTION_SOURCE_SCHEMA, get_frontend_api_form

    module_create = get_frontend_api_form("module.create")
    module_create_fields = {field["name"]: field for field in module_create["fields"]}
    template_source = module_create_fields["template_id"]["option_source"]
    assert template_source == {
        "schema": FRONTEND_API_OPTION_SOURCE_SCHEMA,
        "operation_id": "module.templates",
        "values_path": ["templates"],
        "value_field": "id",
        "label_field": "title",
        "detail_fields": ["family", "source"],
        "requires": ["path"],
        "forward": ["path"],
        "filters": {"authoring_ready": True},
    }
    assert module_create["json_schema"]["properties"]["template_id"]["x-paradev-option-source"] == template_source
    assert module_create_fields["source_root"]["option_source"] == {
        "schema": FRONTEND_API_OPTION_SOURCE_SCHEMA,
        "operation_id": "module.templates",
        "values_path": ["source_roots"],
        "value_field": "relative_path",
        "label_field": "relative_path",
        "detail_fields": ["path"],
        "requires": ["path"],
        "forward": ["path"],
    }

    module_view = get_frontend_api_form("module.view")
    module_id_source = {field["name"]: field for field in module_view["fields"]}["module_id"]["option_source"]
    assert module_id_source["operation_id"] == "module.list"
    assert module_id_source["values_path"] == ["modules"]
    assert module_id_source["value_field"] == "module_id"
    assert module_id_source["detail_fields"] == ["family", "collection_id"]
    assert module_id_source["requires"] == ["path"]

    collection_view = get_frontend_api_form("collection.view")
    collection_id_source = {field["name"]: field for field in collection_view["fields"]}["collection_id"]["option_source"]
    assert collection_id_source["operation_id"] == "collection.list"
    assert collection_id_source["values_path"] == ["collections"]
    assert collection_id_source["value_field"] == "collection_id"

    build_artifacts = get_frontend_api_form("build.artifacts")
    artifact_fields = {field["name"]: field for field in build_artifacts["fields"]}
    assert artifact_fields["artifact_path"]["option_source"]["operation_id"] == "build.artifacts"
    assert artifact_fields["artifact_path"]["option_source"]["value_field"] == "path"
    assert artifact_fields["artifact_type"]["option_source"]["value_field"] == "type"

    build_explain = get_frontend_api_form("build.explain")
    explain_fields = {field["name"]: field for field in build_explain["fields"]}
    assert explain_fields["source_path"]["option_source"]["operation_id"] == "module.sources"
    assert explain_fields["diagnostic_code"]["option_source"]["operation_id"] == "build.diagnostics"


def test_frontend_api_option_sources_reference_canonical_operations() -> None:
    from paradev.sdk import FRONTEND_API_OPTION_SOURCE_SCHEMA, get_frontend_api_contract

    contract = get_frontend_api_contract()
    rows = {str(row["id"]): row for row in contract["operations"]}

    for operation in rows.values():
        for field in operation.get("inputs", []):
            if not isinstance(field, dict) or "option_source" not in field:
                continue
            option_source = field["option_source"]
            assert option_source["schema"] == FRONTEND_API_OPTION_SOURCE_SCHEMA
            assert option_source["operation_id"] in rows
            assert option_source["values_path"]
            assert option_source["value_field"]
            assert option_source["label_field"]


def test_frontend_api_form_fields_have_sdk_owned_user_text() -> None:
    from paradev.sdk import get_frontend_api_contract, get_frontend_api_form

    contract = get_frontend_api_contract()

    for operation in contract["operations"]:
        if not isinstance(operation, dict) or not operation.get("inputs"):
            continue
        form = get_frontend_api_form(str(operation["id"]))
        for field in form["fields"]:
            assert field["label"]
            assert field["description"]


def test_frontend_api_input_normalizer_maps_form_values_to_adapter_buckets() -> None:
    from paradev.sdk import normalize_frontend_api_inputs

    module_edit = normalize_frontend_api_inputs(
        "module.edit",
        {
            "module_id": "modifier/test_modifier",
            "relative_path": "def.pdx",
            "text": "modifier = { value = 1 }",
        },
    )

    assert module_edit["schema"] == "paradev.sdk.frontend-api.inputs.v1"
    assert module_edit["operation_id"] == "module.edit"
    assert module_edit["values"]["path"] == "."
    assert module_edit["values"]["create"] is False
    assert module_edit["project"] == {"path": "."}
    assert module_edit["parameters"] == {
        "module_id": "modifier/test_modifier",
        "relative_path": "def.pdx",
        "text": "modifier = { value = 1 }",
        "create": False,
        "encoding": "utf-8",
    }
    assert module_edit["selectors"] == {}
    assert module_edit["projections"] == {}

    artifacts = normalize_frontend_api_inputs(
        "build.artifacts",
        {
            "path": "/workspace/mod",
            "artifact_path": "common/modifiers/test.txt",
            "module_id": "modifier/test_modifier",
        },
    )
    assert artifacts["project"] == {"path": "/workspace/mod"}
    assert artifacts["parameters"] == {
        "path": "common/modifiers/test.txt",
        "module_id": "modifier/test_modifier",
    }
    assert artifacts["aliases"] == {"artifact_path": "path"}

    surface = normalize_frontend_api_inputs("surface.frontend_api", {"operation_id": "module.edit", "form": True})
    assert surface["selectors"] == {"operation_id": "module.edit"}
    assert surface["projections"] == {"form": True}
    assert surface["parameters"] == {}

    with pytest.raises(ValueError, match="Missing required frontend API inputs for module.edit: text"):
        normalize_frontend_api_inputs(
            "module.edit",
            {"module_id": "modifier/test_modifier", "relative_path": "def.pdx"},
        )
    with pytest.raises(ValueError, match="Unsupported frontend API inputs for module.edit: nope"):
        normalize_frontend_api_inputs("module.edit", {"nope": "value"})
    with pytest.raises(
        ValueError,
        match="Invalid frontend API input for project.browser: kind must be one of module, collection\\.",
    ):
        normalize_frontend_api_inputs("project.browser", {"kind": "asset"})
    with pytest.raises(
        ValueError,
        match="Invalid frontend API input for lsp.hover: line must be >= 0\\.",
    ):
        normalize_frontend_api_inputs("lsp.hover", {"text": "focus = {}", "line": -1, "character": 0})
    with pytest.raises(
        ValueError,
        match="Invalid frontend API input for catalog.query: limit must be <= 200\\.",
    ):
        normalize_frontend_api_inputs("catalog.query", {"limit": 201})
    with pytest.raises(ValueError, match="Catalog query hydrated requests must use limit 1\\."):
        normalize_frontend_api_inputs("catalog.query", {"include_data": True})

    hydrated_catalog = normalize_frontend_api_inputs("catalog.query", {"limit": 1, "include_data": True})
    assert hydrated_catalog["parameters"]["limit"] == 1
    assert hydrated_catalog["parameters"]["include_data"] is True


def test_frontend_api_option_resolver_executes_sdk_owned_provider_rows() -> None:
    from paradev.sdk import FRONTEND_API_OPTIONS_SCHEMA, resolve_frontend_api_options

    project_path = "demos/assets/projects/minimal"

    templates = resolve_frontend_api_options("module.create", "template_id", {"path": project_path})

    assert templates["schema"] == FRONTEND_API_OPTIONS_SCHEMA
    assert templates["operation_id"] == "module.create"
    assert templates["field_name"] == "template_id"
    assert templates["available"] is True
    assert templates["missing_requirements"] == []
    assert templates["provider_operation_id"] == "module.templates"
    assert templates["provider_values"] == {
        "authoring_ready": True,
        "path": project_path,
    }
    assert templates["provider_payload_schema"] == "paradev.sdk.templates.v1"
    assert templates["options"][0]["value"] == "hoi4:idea/basic"
    assert templates["options"][0]["label"] == "Basic HoI4 Idea"
    assert templates["options"][0]["details"] == {"family": "idea", "source": "builtin"}

    source_roots = resolve_frontend_api_options("module.create", "source_root", {"path": project_path})

    assert source_roots["provider_operation_id"] == "module.templates"
    assert source_roots["options"][0]["value"] == "src"
    assert source_roots["options"][0]["label"] == "src"

    modules = resolve_frontend_api_options("module.view", "module_id", {"path": project_path})

    assert modules["provider_operation_id"] == "module.list"
    assert modules["provider_payload_schema"] == "paradev.build.modules.v1"
    assert modules["options"][0]["value"] == "focus/GER_sample"
    assert modules["options"][0]["details"]["family"] == "focus"

    missing = resolve_frontend_api_options("module.file", "relative_path", {"path": project_path})

    assert missing["available"] is False
    assert missing["missing_requirements"] == ["module_id"]
    assert missing["options"] == []

    with pytest.raises(ValueError, match="does not expose option_source"):
        resolve_frontend_api_options("module.create", "object_id", {"path": project_path})


def test_frontend_api_option_resolver_rest_route_output_json() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())
    response = client.post(
        "/frontend-api/options",
        params={"operation_id": "module.create", "field_name": "template_id"},
        json={"path": "demos/assets/projects/minimal"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["schema"] == "paradev.sdk.frontend-api.options.v1"
    assert payload["provider_operation_id"] == "module.templates"
    assert payload["options"][0]["value"] == "hoi4:idea/basic"


def test_frontend_api_action_detail_rest_route_output_json() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())
    response = client.get("/frontend-api/action", params={"operation_id": "module.create"})

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["schema"] == "paradev.sdk.frontend-api.action-detail.v1"
    assert payload["operation_id"] == "module.create"
    assert payload["sections"] == ["authoring"]
    assert payload["option_fields"] == ["template_id", "source_root"]


def test_frontend_api_binding_lookup_rest_route_output_json() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())
    response = client.get(
        "/frontend-api/binding",
        params={
            "binding_surface": "rest",
            "binding_key": "GET /projects/inspect?kind=modules",
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload == {
        "schema": "paradev.sdk.frontend-api.binding-lookup.v1",
        "surface": "rest",
        "key": "GET /projects/inspect?kind=modules",
        "operation_ids": ["module.list"],
        "count": 1,
    }

    invalid = client.get(
        "/frontend-api/binding",
        params={"binding_surface": "gui", "binding_key": "project"},
    )

    assert invalid.status_code == 400
    assert "Unsupported frontend API binding surface: gui" in invalid.json()["detail"]


def test_api_catalog_rest_route_outputs_table_reference_and_index_json() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())

    table_response = client.get("/api-catalog")
    reference_response = client.get("/api-catalog", params={"reference_id": "frontend-api"})
    index_response = client.get("/api-catalog", params={"index_name": "surface", "key": "rest"})

    assert table_response.status_code == 200, table_response.text
    assert table_response.json()["schema"] == "paradev.api-catalog.v1"
    assert reference_response.status_code == 200, reference_response.text
    reference_payload = reference_response.json()
    assert reference_payload["id"] == "frontend-api"
    assert reference_payload["schema"] == "paradev.sdk.frontend-api.v1"
    assert index_response.status_code == 200, index_response.text
    assert index_response.json() == [
        "api-catalog",
        "surfaces-api",
        "frontend-api",
        "project-inspection-reference",
        "architecture-api",
        "pdx-api",
        "lsp-api",
        "catalog-api",
        "rest-api",
        "rest-facade-api",
        "cli-api",
        "surface-contract-reference",
    ]


def test_api_catalog_rest_route_rejects_invalid_selectors() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())

    ambiguous = client.get(
        "/api-catalog",
        params={"reference_id": "frontend-api", "index_name": "surface", "key": "rest"},
    )
    incomplete = client.get("/api-catalog", params={"index_name": "surface"})
    unknown = client.get("/api-catalog", params={"reference_id": "missing-api"})

    assert ambiguous.status_code == 400
    assert "Pass only one API catalog selector" in ambiguous.json()["detail"]
    assert incomplete.status_code == 400
    assert "index_name requires key" in incomplete.json()["detail"]
    assert unknown.status_code == 400
    assert "unknown ParaDev API catalog reference 'missing-api'" in unknown.json()["detail"]


def test_surface_contracts_rest_route_outputs_summary_contract_and_status_json() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())

    table_response = client.get("/surface-contracts")
    contract_response = client.get("/surface-contracts", params={"identifier": "openapi"})
    status_response = client.get("/surface-contracts", params={"status": "implemented"})

    assert table_response.status_code == 200, table_response.text
    assert table_response.json()["schema"] == "paradev.surface-contract-summary.v1"
    assert contract_response.status_code == 200, contract_response.text
    contract_payload = contract_response.json()
    assert contract_payload["openapi"] == "3.1.0"
    assert "/api-catalog" in contract_payload["paths"]
    assert status_response.status_code == 200, status_response.text
    assert status_response.json() == ["bundle", "lsp", "openapi"]


def test_surface_contracts_rest_route_rejects_invalid_selectors() -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app

    client = testclient.TestClient(build_app())

    ambiguous = client.get("/surface-contracts", params={"identifier": "openapi", "status": "implemented"})
    unknown_identifier = client.get("/surface-contracts", params={"identifier": "missing"})
    unknown_status = client.get("/surface-contracts", params={"status": "retired"})

    assert ambiguous.status_code == 400
    assert "Pass only one surface contract selector" in ambiguous.json()["detail"]
    assert unknown_identifier.status_code == 400
    assert "unknown ParaDev surface contract 'missing'" in unknown_identifier.json()["detail"]
    assert unknown_status.status_code == 400
    assert "unknown ParaDev surface contract status 'retired'" in unknown_status.json()["detail"]


def test_frontend_api_rest_request_planner_maps_values_to_query_and_body() -> None:
    from paradev.sdk import plan_frontend_api_rest_request

    module_edit = plan_frontend_api_rest_request(
        "module.edit",
        {
            "path": "/workspace/mod",
            "module_id": "modifier/test_modifier",
            "relative_path": "def.pdx",
            "text": "modifier = { value = 1 }",
        },
    )

    assert module_edit["schema"] == "paradev.sdk.frontend-api.rest-request.v1"
    assert module_edit["operation_id"] == "module.edit"
    assert module_edit["method"] == "PATCH"
    assert module_edit["path"] == "/projects/modules/file"
    assert module_edit["query"] == {
        "path": "/workspace/mod",
        "module_id": "modifier/test_modifier",
        "relative_path": "def.pdx",
        "create": False,
        "encoding": "utf-8",
    }
    assert module_edit["body"] == {"text": "modifier = { value = 1 }"}
    assert module_edit["normalized"]["project"] == {"path": "/workspace/mod"}

    source_text = plan_frontend_api_rest_request(
        "project.source_text",
        {
            "project_id": "demo_mod",
            "path": "/workspace/mod",
            "source_path": "src/modules/focus/GER_sample/def.pdx",
        },
    )
    assert source_text["method"] == "GET"
    assert source_text["path"] == "/projects/demo_mod/sources"
    assert source_text["query"] == {
        "path": "src/modules/focus/GER_sample/def.pdx",
        "project_root": "/workspace/mod",
    }
    assert source_text["body"] == {}

    module_draft = plan_frontend_api_rest_request(
        "module.draft",
        {
            "project_id": "demo_mod",
            "family_id": "ideas",
            "path": "/workspace/mod",
            "object_id": "IDEA_DEMO",
            "values": {"title": "Demo Idea"},
        },
    )
    assert module_draft["method"] == "POST"
    assert module_draft["path"] == "/projects/demo_mod/modules/ideas/drafts"
    assert module_draft["query"] == {}
    assert module_draft["body"] == {
        "project_root": "/workspace/mod",
        "object_id": "IDEA_DEMO",
        "values": {"title": "Demo Idea"},
        "write": False,
        "force": False,
    }

    draft_apply = plan_frontend_api_rest_request(
        "project.draft_apply",
        {
            "project_id": "demo_mod",
            "path": "/workspace/mod",
            "source_edits": [{"path": "src/modules/idea/IDEA_DEMO/def.pdx", "text": "ideas = {}"}],
        },
    )
    assert draft_apply["method"] == "POST"
    assert draft_apply["path"] == "/projects/demo_mod/drafts/apply"
    assert draft_apply["query"] == {}
    assert draft_apply["body"] == {
        "project_root": "/workspace/mod",
        "source_edits": [{"path": "src/modules/idea/IDEA_DEMO/def.pdx", "text": "ideas = {}"}],
    }

    ai_profile_write = plan_frontend_api_rest_request(
        "ai.profile.write",
        {
            "profile_id": "explain",
            "profile": {
                "prompt": "Prefer editable SDK prompts.",
                "sourceKinds": ["project", "selection"],
            },
            "project_root": "/workspace/mod",
        },
    )
    assert ai_profile_write["method"] == "PUT"
    assert ai_profile_write["path"] == "/desktop/ai/profiles/explain"
    assert ai_profile_write["query"] == {}
    assert ai_profile_write["body"] == {
        "profile": {
            "prompt": "Prefer editable SDK prompts.",
            "sourceKinds": ["project", "selection"],
        },
        "project_root": "/workspace/mod",
    }

    ai_chat = plan_frontend_api_rest_request(
        "ai.chat",
        {
            "provider": "deepseek",
            "model": "deepseek-v4-flash",
            "gateway": "openai",
            "preset": "reason",
            "prompt": "Explain this focus.",
            "role": "explain",
            "project_root": "/workspace/mod",
            "sources": [{"kind": "source", "path": "src/modules/focus_tree/C01_MAIN/info.json"}],
        },
    )
    assert ai_chat["method"] == "POST"
    assert ai_chat["path"] == "/desktop/ai/chat"
    assert ai_chat["query"] == {}
    assert ai_chat["body"] == {
        "provider": "deepseek",
        "model": "deepseek-v4-flash",
        "gateway": "openai",
        "preset": "reason",
        "prompt": "Explain this focus.",
        "role": "explain",
        "project_root": "/workspace/mod",
        "sources": [{"kind": "source", "path": "src/modules/focus_tree/C01_MAIN/info.json"}],
    }

    ai_profiles = plan_frontend_api_rest_request("ai.profiles", {"project_root": "/workspace/mod"})
    assert ai_profiles["method"] == "GET"
    assert ai_profiles["path"] == "/desktop/ai/profiles"
    assert ai_profiles["query"] == {"project_root": "/workspace/mod"}
    assert ai_profiles["body"] == {}

    ai_profile_reset = plan_frontend_api_rest_request(
        "ai.profile.reset",
        {"profile_id": "explain", "project_root": "/workspace/mod"},
    )
    assert ai_profile_reset["method"] == "DELETE"
    assert ai_profile_reset["path"] == "/desktop/ai/profiles/explain"
    assert ai_profile_reset["query"] == {"project_root": "/workspace/mod"}
    assert ai_profile_reset["body"] == {}

    build_start = plan_frontend_api_rest_request(
        "build.start",
        {
            "project_root": "/workspace/mod",
            "mode": "full",
            "profile": "hoi4",
            "strict_metadata": True,
            "parallelism": 4,
            "target": {"kind": "module", "id": "focus_tree/GER_main"},
        },
    )
    assert build_start["method"] == "POST"
    assert build_start["path"] == "/desktop/builds"
    assert build_start["query"] == {}
    assert build_start["body"] == {
        "project_root": "/workspace/mod",
        "mode": "full",
        "profile": "hoi4",
        "strict_metadata": True,
        "parallelism": 4,
        "target": {"kind": "module", "id": "focus_tree/GER_main"},
    }

    build_runs = plan_frontend_api_rest_request("build.runs", {"project_root": "/workspace/mod"})
    assert build_runs["method"] == "GET"
    assert build_runs["path"] == "/desktop/builds"
    assert build_runs["query"] == {"project_root": "/workspace/mod"}
    assert build_runs["body"] == {}

    build_status = plan_frontend_api_rest_request("build.status", {"run_id": "build-1"})
    assert build_status["method"] == "GET"
    assert build_status["path"] == "/desktop/builds/status"
    assert build_status["query"] == {"run_id": "build-1"}
    assert build_status["body"] == {}

    build_interrupt = plan_frontend_api_rest_request("build.interrupt", {"run_id": "build-1"})
    assert build_interrupt["method"] == "POST"
    assert build_interrupt["path"] == "/desktop/builds/interrupt"
    assert build_interrupt["query"] == {}
    assert build_interrupt["body"] == {"run_id": "build-1"}
    with pytest.raises(
        ValueError,
        match=r"Missing required frontend API inputs for build\.status: run_id\.",
    ):
        plan_frontend_api_rest_request("build.status", {})
    with pytest.raises(
        ValueError,
        match=r"Missing required frontend API inputs for build\.interrupt: run_id\.",
    ):
        plan_frontend_api_rest_request("build.interrupt", {})
    for operation_id in ("build.status", "build.interrupt"):
        for invalid_run_id in ("", "   "):
            with pytest.raises(
                ValueError,
                match=rf"Invalid frontend API input for {operation_id}: run_id must be a nonblank string\.",
            ):
                plan_frontend_api_rest_request(operation_id, {"run_id": invalid_run_id})

    lsp_hover = plan_frontend_api_rest_request("lsp.hover", {"text": "focus = { id = GER_test }", "line": 0, "character": 1})
    assert lsp_hover["method"] == "POST"
    assert lsp_hover["path"] == "/lsp/hover"
    assert lsp_hover["query"] == {}
    assert lsp_hover["body"] == {
        "text": "focus = { id = GER_test }",
        "line": 0,
        "character": 1,
    }

    lsp_completion = plan_frontend_api_rest_request(
        "lsp.completion",
        {
            "text": "focus = { id = GER }",
            "line": 0,
            "character": 18,
            "project_path": "/workspace/mod",
            "limit": 50,
        },
    )
    assert lsp_completion["method"] == "POST"
    assert lsp_completion["path"] == "/lsp/completion"
    assert lsp_completion["query"] == {}
    assert lsp_completion["body"] == {
        "text": "focus = { id = GER }",
        "line": 0,
        "character": 18,
        "project_path": "/workspace/mod",
        "limit": 50,
    }
    lsp_keywords = plan_frontend_api_rest_request("lsp.keywords", {"game_root": "/games/hoi4"})
    assert lsp_keywords["method"] == "GET"
    assert lsp_keywords["path"] == "/lsp/keywords"
    assert lsp_keywords["query"] == {"game_root": "/games/hoi4"}
    assert lsp_keywords["body"] == {}

    modules = plan_frontend_api_rest_request("module.list", {"path": "/workspace/mod", "family": "focus"})
    assert modules["query"] == {
        "kind": "modules",
        "path": "/workspace/mod",
        "family": "focus",
    }
    assert modules["body"] == {}

    build_emit = plan_frontend_api_rest_request("build.emit", {"path": "/workspace/mod"})
    assert build_emit["query"] == {
        "emit_artifacts": True,
        "emit_manifests": True,
        "path": "/workspace/mod",
    }
    assert build_emit["body"] == {}

    catalog_write = plan_frontend_api_rest_request(
        "catalog.write",
        {
            "path": "/workspace/mod",
            "profile": "hoi4",
            "database": "/workspace/mod/.paradev/.cache/hb/custom.sqlite",
        },
    )
    assert catalog_write["method"] == "POST"
    assert catalog_write["path"] == "/projects/catalog"
    assert catalog_write["query"] == {
        "path": "/workspace/mod",
        "profile": "hoi4",
        "database": "/workspace/mod/.paradev/.cache/hb/custom.sqlite",
    }
    assert catalog_write["body"] == {}

    catalog_refresh = plan_frontend_api_rest_request("catalog.refresh", {"path": "/workspace/mod"})
    assert catalog_refresh["method"] == "PUT"
    assert catalog_refresh["path"] == "/projects/catalog"
    assert catalog_refresh["query"] == {"path": "/workspace/mod"}
    assert catalog_refresh["body"] == {}

    with pytest.raises(ValueError, match="does not expose a REST binding"):
        plan_frontend_api_rest_request("surface.openapi", {})
    with pytest.raises(ValueError, match="frontend-local operation"):
        plan_frontend_api_rest_request("project.activate", {"project_id": "active"})


def test_cli_surface_contract_lists_sdk_owned_adapter_commands() -> None:
    from paradev.sdk import get_frontend_api_binding_index
    from paradev.surfaces.cli import get_cli_contract

    contract = get_cli_contract()

    assert contract["identifier"] == "cli"
    assert contract["sdk_owned"] is True
    assert "frontend-api" in contract["commands"]
    assert "api-catalog" in contract["commands"]
    assert "package-api" in contract["commands"]
    assert "sdk-api" in contract["commands"]
    assert "project-api" in contract["commands"]
    assert "project-facade-api" in contract["commands"]
    assert "localization-api" in contract["commands"]
    assert "build-api" in contract["commands"]
    assert "pdx-api" in contract["commands"]
    assert "pdx-core-api" in contract["commands"]
    assert "lsp-api" in contract["commands"]
    assert "lsp-server-api" in contract["commands"]
    assert "catalog-api" in contract["commands"]
    assert "hb-api" in contract["commands"]
    assert "rest-api" in contract["commands"]
    assert "rest-facade-api" in contract["commands"]
    assert "mcp-api" in contract["commands"]
    assert "cli-api" in contract["commands"]
    assert "new" in contract["commands"]
    assert "projects" in contract["commands"]
    assert "desktop-state" in contract["commands"]
    assert "project-browser" in contract["commands"]
    assert "project-find" in contract["commands"]
    assert "project-rename" in contract["commands"]
    assert "module-rename" in contract["commands"]
    assert "module-remove" in contract["commands"]
    assert "module-file" in contract["commands"]
    assert "module-edit" in contract["commands"]
    assert "module-batch-edit" in contract["commands"]
    assert "module-batch-request" in contract["commands"]
    assert "collection-file" in contract["commands"]
    assert "collection-edit" in contract["commands"]
    assert "collection-create" in contract["commands"]
    assert "collection-rename" in contract["commands"]
    assert "collection-remove" in contract["commands"]
    assert "inspections" in contract["commands"]
    assert "parse" in contract["commands"]
    assert "format" in contract["commands"]
    assert "sources" in contract["commands"]
    assert "draft-apply" in contract["commands"]
    assert "source-slots" in contract["commands"]
    assert "build-explain" in contract["commands"]
    assert "mcp" in contract["commands"]
    assert "mcp serve" in contract["commands"]
    assert "lsp" in contract["commands"]
    assert "config-api" in contract["commands"]
    assert "gui-api" in contract["commands"]
    assert "desktop-api" in contract["commands"]
    assert "config get" in contract["commands"]
    assert "hb catalog-write" in contract["commands"]
    assert "lsp completion" in contract["commands"]
    assert contract["adapters"]["inspections"] == "get_project_inspection_selection"
    assert contract["adapters"]["inspections --kind"] == "get_project_inspection_selection"
    assert contract["adapters"]["inspections --index --key"] == "get_project_inspection_selection"
    assert contract["adapters"]["inspections --markdown"] == "render_project_inspection_reference_markdown"
    assert contract["adapters"]["mcp serve"] == "serve_authoring_mcp_stdio"
    assert contract["adapters"]["lsp serve"] == "serve_pdx_lsp_stdio"
    assert contract["adapters"]["lsp keywords"] == "hoi4_keyword_dataset"
    assert contract["adapters"]["architecture"] == "get_architecture_spec"
    assert contract["adapters"]["architecture --api-table"] == "get_architecture_api_selection"
    assert contract["adapters"]["architecture --api-table-markdown"] == "render_architecture_api_reference_markdown"
    assert contract["adapters"]["architecture --surface-contract"] == "get_surface_contract_selection"
    assert contract["adapters"]["architecture --surface-contracts"] == "get_surface_contract_selection"
    assert contract["adapters"]["architecture --surface-contracts-markdown"] == "render_surface_contract_reference_markdown"
    assert contract["adapters"]["frontend-api"] == "get_frontend_api_selection"
    assert contract["adapters"]["frontend-api --operation"] == "get_frontend_api_selection"
    assert contract["adapters"]["frontend-api --group"] == "get_frontend_api_selection"
    assert contract["adapters"]["frontend-api --operation --form"] == "get_frontend_api_selection"
    assert contract["adapters"]["frontend-api --index --key"] == "get_frontend_api_selection"
    assert contract["adapters"]["api-catalog"] == "get_api_catalog_selection"
    assert contract["adapters"]["api-catalog --reference"] == "get_api_catalog_selection"
    assert contract["adapters"]["api-catalog --index --key"] == "get_api_catalog_selection"
    assert contract["adapters"]["api-catalog --markdown"] == "render_api_catalog_reference_markdown"
    standard_api_selectors = [
        (
            "package-api",
            "get_package_api_selection",
            "render_package_api_reference_markdown",
        ),
        (
            "config-api",
            "get_config_api_selection",
            "render_config_api_reference_markdown",
        ),
        ("gui-api", "get_gui_api_selection", "render_gui_api_reference_markdown"),
        (
            "desktop-api",
            "get_desktop_api_selection",
            "render_desktop_api_reference_markdown",
        ),
        ("games-api", "get_games_api_selection", "render_games_api_reference_markdown"),
        (
            "surfaces-api",
            "get_surfaces_api_selection",
            "render_surfaces_api_reference_markdown",
        ),
        ("pdx-api", "get_pdx_api_selection", "render_pdx_api_reference_markdown"),
        (
            "pdx-core-api",
            "get_pdx_core_api_selection",
            "render_pdx_core_api_reference_markdown",
        ),
        ("lsp-api", "get_lsp_api_selection", "render_lsp_api_reference_markdown"),
        (
            "lsp-server-api",
            "get_lsp_server_api_selection",
            "render_lsp_server_api_reference_markdown",
        ),
        (
            "catalog-api",
            "get_catalog_api_selection",
            "render_catalog_api_reference_markdown",
        ),
        ("hb-api", "get_hb_api_selection", "render_hb_api_reference_markdown"),
        ("rest-api", "get_rest_api_selection", "render_rest_api_reference_markdown"),
        (
            "rest-facade-api",
            "get_rest_facade_api_selection",
            "render_rest_facade_api_reference_markdown",
        ),
        ("mcp-api", "get_mcp_api_selection", "render_mcp_api_reference_markdown"),
        ("cli-api", "get_cli_api_selection", "render_cli_api_reference_markdown"),
        ("sdk-api", "get_sdk_api_selection", "render_sdk_api_reference_markdown"),
        (
            "project-api",
            "get_project_api_selection",
            "render_project_api_reference_markdown",
        ),
        (
            "templates-api",
            "get_templates_api_selection",
            "render_templates_api_reference_markdown",
        ),
        (
            "copy-roots-api",
            "get_copy_roots_api_selection",
            "render_copy_roots_api_reference_markdown",
        ),
        (
            "project-facade-api",
            "get_project_facade_api_selection",
            "render_project_facade_api_reference_markdown",
        ),
        (
            "localization-api",
            "get_localization_api_selection",
            "render_localization_api_reference_markdown",
        ),
        ("build-api", "get_build_api_selection", "render_build_api_reference_markdown"),
    ]
    for command_key, selector_helper, markdown_helper in standard_api_selectors:
        assert contract["adapters"][command_key] == selector_helper
        assert contract["adapters"][f"{command_key} --symbol"] == selector_helper
        assert contract["adapters"][f"{command_key} --index --key"] == selector_helper
        assert contract["adapters"][f"{command_key} --markdown"] == markdown_helper
    assert contract["adapters"]["frontend-api --operation --action"] == "get_frontend_api_action"
    assert contract["adapters"]["summary"] == "Project.inspect('summary')"
    assert contract["adapters"]["manifests"] == "Project.inspect('manifests')"
    assert contract["adapters"]["collections"] == "Project.inspect('collections')"
    assert contract["adapters"]["artifacts"] == "Project.inspect('artifacts')"
    assert contract["adapters"]["localization"] == "Project.inspect('localization')"
    assert contract["adapters"]["diagnostics"] == "Project.inspect('diagnostics')"
    assert contract["adapters"]["source-map"] == "Project.inspect('source-map')"
    assert contract["adapters"]["dependencies"] == "Project.inspect('dependencies')"
    assert contract["adapters"]["hb catalog-write"] == "catalog_write"
    assert contract["adapters"]["hb catalog-refresh"] == "catalog_refresh"
    assert contract["adapters"]["lsp completion"] == "complete_pdx_lsp_text"
    assert contract["adapters"]["config get"] == "config_get"
    assert contract["adapters"]["setup"] == "CM_PARADEV.setup"
    assert "modules" in contract["inspection_contract"]["index"]["filter"]["module_id"]
    assert contract["adapters"]["templates"] == "Project.templates"
    assert contract["filters"]["api-catalog"] == ["reference_id", "index_name", "key"]
    assert contract["filters"]["templates"] == [
        "template_id",
        "family",
        "source",
        "authoring_ready",
        "diagnostic_code",
    ]
    assert contract["filters"]["frontend-api"] == [
        "operation_id",
        "group_id",
        "index_name",
        "key",
    ]
    assert contract["filters"]["architecture --api-table"] == [
        "symbol",
        "index_name",
        "key",
    ]
    assert contract["filters"]["inspections"] == ["kind", "index_name", "key"]
    for command_key, _, _ in standard_api_selectors:
        assert contract["filters"][command_key] == ["symbol", "index_name", "key"]
    assert contract["projections"]["architecture"] == [
        "api-table",
        "api-table-markdown",
        "surface-contract",
        "surface-contracts",
        "surface-contracts-markdown",
    ]
    assert contract["projections"]["frontend-api"] == [
        "form",
        "index",
        "key",
        "action",
        "values-json",
        "option-field",
        "binding-surface",
        "binding-key",
        "rest-request",
        "workspace",
        "markdown",
        "sdk-cli-markdown",
        "typescript",
    ]
    assert contract["projections"]["api-catalog"] == [
        "reference",
        "index",
        "key",
        "markdown",
    ]
    for command_key, _, _ in standard_api_selectors:
        assert contract["projections"][command_key] == [
            "symbol",
            "index",
            "key",
            "markdown",
        ]
    assert contract["projections"]["inspections"] == [
        "kind",
        "index",
        "key",
        "markdown",
    ]
    assert contract["frontend_operation_ids"] == get_frontend_api_binding_index("cli")
    assert contract["frontend_operation_ids"]["project"] == [
        "project.open",
        "project.view",
    ]
    assert contract["frontend_operation_ids"]["projects"] == ["project.list"]
    assert contract["frontend_operation_ids"]["desktop-state"] == ["project.state"]
    assert contract["frontend_operation_ids"]["project-browser"] == ["project.browser"]
    assert contract["frontend_operation_ids"]["draft-apply"] == ["project.draft_apply"]
    assert contract["frontend_operation_ids"]["frontend-api"] == ["surface.frontend_api"]
    assert contract["frontend_operation_ids"]["frontend-api --workspace"] == ["surface.frontend_api.workspace"]
    assert contract["frontend_operation_ids"]["frontend-api --operation --action"] == ["surface.frontend_api.action"]
    assert contract["frontend_operation_ids"]["frontend-api --operation --values-json --rest-request"] == ["surface.frontend_api.rest_request"]
    assert contract["frontend_operation_ids"]["frontend-api --binding-surface --binding-key"] == ["surface.frontend_api.binding_lookup"]
    assert contract["frontend_operation_ids"]["lsp keywords"] == ["lsp.keywords"]
    assert contract["frontend_operation_ids"]["collection-rename"] == ["collection.rename"]
    assert contract["frontend_operation_ids"]["collection-remove"] == ["collection.remove"]
    assert contract["frontend_operation_ids"]["sources --owner-kind collection"] == ["collection.sources"]
    assert contract["frontend_operation_ids"]["assets"] == ["build.assets"]
    assert contract["frontend_operation_ids"]["sprites"] == ["build.sprites"]
    assert contract["adapters"]["authoring-path"] == "Project.authoring_path"
    assert contract["adapters"]["authoring-plan"] == "Project.authoring_plan"
    assert contract["adapters"]["sources"] == "Project.inspect('sources')"
    assert contract["adapters"]["draft-apply"] == "Project.apply_source_draft"
    assert contract["adapters"]["source-slots"] == "Project.inspect('source-slots')"
    assert contract["adapters"]["assets"] == "Project.inspect('assets')"
    assert contract["adapters"]["sprites"] == "Project.inspect('sprites')"
    assert contract["adapters"]["hb catalog-preview"] == "Project.inspect('catalog-preview')"
    assert contract["adapters"]["hb catalog-query"] == "Project.inspect('catalog-query')"
    assert contract["adapters"]["parse"] == "parse_pdx_file"
    assert contract["adapters"]["format"] == "format_pdx_file"
    assert contract["adapters"]["new"] == "Project.create"
    assert contract["adapters"]["project"] == "Project.to_view"
    assert contract["adapters"]["build"] == "Project.build"
    assert contract["adapters"]["projects"] == "registered_projects"
    assert contract["adapters"]["desktop-state"] == "desktop_state"
    assert contract["adapters"]["project-browser"] == "Project.browser"
    assert contract["adapters"]["project-find"] == "Project.find"
    assert contract["adapters"]["project-rename"] == "Project.rename"
    assert contract["adapters"]["project-language"] == "Project.set_preferred_language"
    assert contract["adapters"]["module-rename"] == "Project.rename_module"
    assert contract["adapters"]["module-collection-set"] == "Project.set_module_collection"
    assert contract["adapters"]["module-metadata-clean"] == "Project.clean_module_metadata"
    assert contract["adapters"]["module-remove"] == "Project.remove_module"
    assert contract["adapters"]["module-file"] == "Project.read_module_file"
    assert contract["adapters"]["module-edit"] == "Project.write_module_file"
    assert contract["adapters"]["module-batch-edit"] == "Project.write_module_files"
    assert contract["adapters"]["module-batch-request"] == "Project.module_batch_edit_request"
    assert contract["adapters"]["collection-file"] == "Project.read_collection_file"
    assert contract["adapters"]["collection-edit"] == "Project.write_collection_file"
    assert contract["adapters"]["collection-scaffold"] == ("Project.scaffold_collection")
    assert contract["adapters"]["collection-create"] == "Project.create_collection"
    assert contract["adapters"]["collection-rename"] == "Project.rename_collection"
    assert contract["adapters"]["collection-remove"] == "Project.remove_collection"


def test_cli_api_table_lists_command_contract() -> None:
    from typing_extensions import is_typeddict

    from paradev.surfaces.cli import (
        CLI_API_TABLE_SCHEMA,
        CliApiRow,
        CliApiTable,
        get_cli_api_table,
        get_cli_contract,
        render_cli_api_reference_markdown,
    )

    contract = get_cli_contract()
    table = get_cli_api_table()
    rows = table["rows"]
    row_by_key = {row["command_key"]: row for row in rows}
    reference = render_cli_api_reference_markdown()

    assert is_typeddict(CliApiRow)
    assert is_typeddict(CliApiTable)
    assert table["schema"] == CLI_API_TABLE_SCHEMA
    assert table["row_count"] == 208 == len(rows)
    assert len(contract["commands"]) == 105
    assert len(contract["adapters"]) == 197
    assert set(CliApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "feature",
        "command_key",
        "adapter",
        "filters",
        "projections",
        "returns",
        "raises",
        "registry_seam",
        "surface",
        "frontend_operation_ids",
        "doc_page",
        "test_anchor",
    }
    assert set(CliApiTable.__annotations__) == {
        "schema",
        "row_count",
        "feature_index",
        "kind_index",
        "adapter_index",
        "frontend_operation_index",
        "rows",
    }
    assert len(table["kind_index"]["command"]) == 101
    assert len(table["kind_index"]["command projection"]) == 96
    assert len(table["kind_index"]["binding variant"]) == 7
    assert table["feature_index"]["api-catalog"] == [
        "paradev api-catalog",
        "paradev api-catalog --reference",
        "paradev api-catalog --index --key",
        "paradev api-catalog --markdown",
    ]
    assert table["feature_index"]["package"] == [
        "paradev package-api",
        "paradev package-api --markdown",
        "paradev package-api --symbol",
        "paradev package-api --index --key",
    ]
    assert table["feature_index"]["surfaces"] == [
        "paradev surfaces-api",
        "paradev surfaces-api --markdown",
        "paradev surfaces-api --symbol",
        "paradev surfaces-api --index --key",
    ]
    assert table["feature_index"]["cli"] == [
        "paradev cli-api",
        "paradev cli-api --markdown",
        "paradev cli-api --symbol",
        "paradev cli-api --index --key",
    ]
    assert table["feature_index"]["sdk"] == [
        "paradev sdk-api",
        "paradev sdk-api --markdown",
        "paradev sdk-api --symbol",
        "paradev sdk-api --index --key",
    ]
    assert table["feature_index"]["localization"] == [
        "paradev localization-api",
        "paradev localization-api --markdown",
        "paradev localization-api --symbol",
        "paradev localization-api --index --key",
    ]
    assert table["feature_index"]["gui"] == [
        "paradev gui-api",
        "paradev gui-api --markdown",
        "paradev gui-api --symbol",
        "paradev gui-api --index --key",
    ]
    assert table["feature_index"]["desktop"] == [
        "paradev desktop-api",
        "paradev desktop-api --markdown",
        "paradev desktop-api --typescript",
        "paradev desktop-api --symbol",
        "paradev desktop-api --index --key",
    ]
    assert table["feature_index"]["games"] == [
        "paradev games-api",
        "paradev games-api --markdown",
        "paradev games-api --symbol",
        "paradev games-api --index --key",
    ]
    assert table["feature_index"]["authoring"] == [
        "paradev templates-api",
        "paradev module-batch-create",
        "paradev templates",
        "paradev authoring-path",
        "paradev authoring-plan",
        "paradev scaffold",
        "paradev templates-api --markdown",
        "paradev templates-api --symbol",
        "paradev templates-api --index --key",
    ]
    assert table["feature_index"]["copy-roots"] == [
        "paradev copy-roots-api",
        "paradev copy-roots-api --markdown",
        "paradev copy-roots-api --symbol",
        "paradev copy-roots-api --index --key",
    ]
    assert table["feature_index"]["config"] == [
        "paradev config-api",
        "paradev config",
        "paradev config get",
        "paradev config list",
        "paradev config set",
        "paradev config unset",
        "paradev config scopes",
        "paradev config history",
        "paradev setup",
        "paradev init",
        "paradev pj",
        "paradev config-api --markdown",
        "paradev config-api --symbol",
        "paradev config-api --index --key",
    ]
    assert table["feature_index"]["lsp"][:3] == [
        "paradev lsp-api",
        "paradev lsp-server-api",
        "paradev lsp",
    ]
    assert table["feature_index"]["mcp"] == [
        "paradev mcp-api",
        "paradev mcp",
        "paradev mcp serve",
        "paradev mcp-api --markdown",
        "paradev mcp-api --symbol",
        "paradev mcp-api --index --key",
    ]
    assert table["feature_index"]["rest"] == [
        "paradev rest-api",
        "paradev rest-facade-api",
        "paradev rest-api --markdown",
        "paradev rest-facade-api --markdown",
        "paradev rest-api --symbol",
        "paradev rest-api --index --key",
        "paradev rest-facade-api --symbol",
        "paradev rest-facade-api --index --key",
    ]
    assert "paradev project-api" in table["feature_index"]["projects"]
    assert "paradev project-api --markdown" in table["feature_index"]["projects"]
    assert "paradev project-api --symbol" in table["feature_index"]["projects"]
    assert "paradev project-facade-api" in table["feature_index"]["projects"]
    assert "paradev project-facade-api --markdown" in table["feature_index"]["projects"]
    assert "paradev project-facade-api --symbol" in table["feature_index"]["projects"]
    assert "paradev build-api" in table["feature_index"]["build"]
    assert "paradev build-api --markdown" in table["feature_index"]["build"]
    assert "paradev build-api --symbol" in table["feature_index"]["build"]
    assert table["feature_index"]["catalog"][:3] == [
        "paradev catalog-api",
        "paradev hb-api",
        "paradev hb",
    ]
    assert table["adapter_index"]["get_api_catalog_selection"] == [
        "paradev api-catalog",
        "paradev api-catalog --reference",
        "paradev api-catalog --index --key",
    ]
    assert table["adapter_index"]["render_api_catalog_reference_markdown"] == ["paradev api-catalog --markdown"]
    assert table["adapter_index"]["get_surface_contract_selection"] == [
        "paradev architecture --surface-contract",
        "paradev architecture --surface-contracts",
    ]
    assert table["adapter_index"]["get_frontend_api_selection"] == [
        "paradev frontend-api",
        "paradev frontend-api --operation",
        "paradev frontend-api --group",
        "paradev frontend-api --operation --form",
        "paradev frontend-api --index --key",
    ]
    assert table["adapter_index"]["get_project_inspection_selection"] == [
        "paradev inspections",
        "paradev inspections --kind",
        "paradev inspections --index --key",
    ]
    standard_api_selectors = [
        (
            "package-api",
            "get_package_api_selection",
            "render_package_api_reference_markdown",
        ),
        (
            "config-api",
            "get_config_api_selection",
            "render_config_api_reference_markdown",
        ),
        ("gui-api", "get_gui_api_selection", "render_gui_api_reference_markdown"),
        (
            "desktop-api",
            "get_desktop_api_selection",
            "render_desktop_api_reference_markdown",
        ),
        ("games-api", "get_games_api_selection", "render_games_api_reference_markdown"),
        (
            "surfaces-api",
            "get_surfaces_api_selection",
            "render_surfaces_api_reference_markdown",
        ),
        ("cli-api", "get_cli_api_selection", "render_cli_api_reference_markdown"),
        ("sdk-api", "get_sdk_api_selection", "render_sdk_api_reference_markdown"),
        (
            "project-api",
            "get_project_api_selection",
            "render_project_api_reference_markdown",
        ),
        (
            "templates-api",
            "get_templates_api_selection",
            "render_templates_api_reference_markdown",
        ),
        (
            "copy-roots-api",
            "get_copy_roots_api_selection",
            "render_copy_roots_api_reference_markdown",
        ),
        (
            "project-facade-api",
            "get_project_facade_api_selection",
            "render_project_facade_api_reference_markdown",
        ),
        (
            "localization-api",
            "get_localization_api_selection",
            "render_localization_api_reference_markdown",
        ),
        ("build-api", "get_build_api_selection", "render_build_api_reference_markdown"),
        ("pdx-api", "get_pdx_api_selection", "render_pdx_api_reference_markdown"),
        (
            "pdx-core-api",
            "get_pdx_core_api_selection",
            "render_pdx_core_api_reference_markdown",
        ),
        ("lsp-api", "get_lsp_api_selection", "render_lsp_api_reference_markdown"),
        (
            "lsp-server-api",
            "get_lsp_server_api_selection",
            "render_lsp_server_api_reference_markdown",
        ),
        (
            "catalog-api",
            "get_catalog_api_selection",
            "render_catalog_api_reference_markdown",
        ),
        ("hb-api", "get_hb_api_selection", "render_hb_api_reference_markdown"),
        ("rest-api", "get_rest_api_selection", "render_rest_api_reference_markdown"),
        (
            "rest-facade-api",
            "get_rest_facade_api_selection",
            "render_rest_facade_api_reference_markdown",
        ),
        ("mcp-api", "get_mcp_api_selection", "render_mcp_api_reference_markdown"),
    ]
    for command_key, selector_helper, markdown_helper in standard_api_selectors:
        assert table["adapter_index"][selector_helper] == [
            f"paradev {command_key}",
            f"paradev {command_key} --symbol",
            f"paradev {command_key} --index --key",
        ]
        assert table["adapter_index"][markdown_helper] == [f"paradev {command_key} --markdown"]
    assert table["adapter_index"]["render_desktop_typescript"] == ["paradev desktop-api --typescript"]
    assert table["adapter_index"]["Project.inspect('summary')"] == ["paradev summary"]
    assert table["frontend_operation_index"]["surface.frontend_api.action"] == ["paradev frontend-api --operation --action"]
    assert table["frontend_operation_index"]["collection.sources"] == ["paradev sources --owner-kind collection"]
    assert row_by_key["frontend-api --operation --action"]["adapter"] == "get_frontend_api_action"
    assert row_by_key["frontend-api --operation --action"]["filters"] == [
        "operation_id",
        "group_id",
        "index_name",
        "key",
    ]
    assert row_by_key["frontend-api --operation --action"]["projections"] == [
        "operation",
        "action",
    ]
    assert row_by_key["frontend-api"]["adapter"] == "get_frontend_api_selection"
    assert row_by_key["frontend-api --operation"]["adapter"] == "get_frontend_api_selection"
    assert row_by_key["frontend-api --group"]["adapter"] == "get_frontend_api_selection"
    assert row_by_key["frontend-api --operation --form"]["adapter"] == "get_frontend_api_selection"
    assert row_by_key["frontend-api --index --key"]["adapter"] == "get_frontend_api_selection"
    assert row_by_key["frontend-api --index --key"]["filters"] == [
        "operation_id",
        "group_id",
        "index_name",
        "key",
    ]
    assert row_by_key["frontend-api --index --key"]["projections"] == ["index", "key"]
    assert row_by_key["summary"]["adapter"] == "Project.inspect('summary')"
    assert row_by_key["inspections"]["filters"] == ["kind", "index_name", "key"]
    assert row_by_key["inspections"]["projections"] == [
        "kind",
        "index",
        "key",
        "markdown",
    ]
    assert row_by_key["inspections --kind"]["adapter"] == "get_project_inspection_selection"
    assert row_by_key["inspections --kind"]["filters"] == ["kind", "index_name", "key"]
    assert row_by_key["inspections --kind"]["projections"] == ["kind"]
    assert row_by_key["inspections --index --key"]["adapter"] == "get_project_inspection_selection"
    assert row_by_key["inspections --index --key"]["filters"] == [
        "kind",
        "index_name",
        "key",
    ]
    assert row_by_key["inspections --index --key"]["projections"] == ["index", "key"]
    assert row_by_key["api-catalog"]["adapter"] == "get_api_catalog_selection"
    assert row_by_key["api-catalog"]["filters"] == ["reference_id", "index_name", "key"]
    assert row_by_key["api-catalog --reference"]["adapter"] == "get_api_catalog_selection"
    assert row_by_key["api-catalog --reference"]["filters"] == [
        "reference_id",
        "index_name",
        "key",
    ]
    assert row_by_key["api-catalog --reference"]["projections"] == ["reference"]
    assert row_by_key["api-catalog --index --key"]["adapter"] == "get_api_catalog_selection"
    assert row_by_key["api-catalog --index --key"]["filters"] == [
        "reference_id",
        "index_name",
        "key",
    ]
    assert row_by_key["api-catalog --index --key"]["projections"] == ["index", "key"]
    assert row_by_key["api-catalog --markdown"]["adapter"] == "render_api_catalog_reference_markdown"
    assert row_by_key["api-catalog"]["projections"] == [
        "reference",
        "index",
        "key",
        "markdown",
    ]
    assert row_by_key["architecture --surface-contract"]["adapter"] == "get_surface_contract_selection"
    assert row_by_key["architecture --surface-contract"]["projections"] == ["surface-contract"]
    assert row_by_key["architecture --surface-contracts"]["adapter"] == "get_surface_contract_selection"
    assert row_by_key["architecture --surface-contracts"]["projections"] == ["surface-contracts"]
    standard_api_features = {
        "package-api": "package",
        "config-api": "config",
        "gui-api": "gui",
        "desktop-api": "desktop",
        "games-api": "games",
        "surfaces-api": "surfaces",
        "cli-api": "cli",
        "sdk-api": "sdk",
        "project-api": "projects",
        "templates-api": "authoring",
        "copy-roots-api": "copy-roots",
        "project-facade-api": "projects",
        "localization-api": "localization",
        "build-api": "build",
        "pdx-api": "pdx",
        "pdx-core-api": "pdx",
        "lsp-api": "lsp",
        "lsp-server-api": "lsp",
        "catalog-api": "catalog",
        "hb-api": "catalog",
        "rest-api": "rest",
        "rest-facade-api": "rest",
        "mcp-api": "mcp",
    }
    for command_key, selector_helper, markdown_helper in standard_api_selectors:
        assert row_by_key[command_key]["adapter"] == selector_helper
        assert row_by_key[command_key]["feature"] == standard_api_features[command_key]
        assert row_by_key[command_key]["filters"] == ["symbol", "index_name", "key"]
        assert row_by_key[command_key]["projections"] == [
            "symbol",
            "index",
            "key",
            "markdown",
        ]
        assert row_by_key[f"{command_key} --symbol"]["adapter"] == selector_helper
        assert row_by_key[f"{command_key} --symbol"]["projections"] == ["symbol"]
        assert row_by_key[f"{command_key} --index --key"]["adapter"] == selector_helper
        assert row_by_key[f"{command_key} --index --key"]["projections"] == [
            "index",
            "key",
        ]
        assert row_by_key[f"{command_key} --markdown"]["adapter"] == markdown_helper
    assert row_by_key["config get"]["adapter"] == "config_get"
    assert row_by_key["mcp"]["kind"] == "command group"
    assert row_by_key["mcp serve"]["adapter"] == "serve_authoring_mcp_stdio"
    assert row_by_key["mcp serve"]["feature"] == "mcp"
    assert row_by_key["module-batch-create"]["adapter"] == "Project.create_modules"
    assert row_by_key["module-batch-create"]["feature"] == "authoring"
    assert row_by_key["module-batch-edit"]["adapter"] == "Project.write_module_files"
    assert row_by_key["module-batch-edit"]["feature"] == "modules"
    assert row_by_key["module-batch-request"]["adapter"] == "Project.module_batch_edit_request"
    assert row_by_key["module-batch-request"]["feature"] == "modules"
    assert row_by_key["module-collection-set"]["adapter"] == "Project.set_module_collection"
    assert row_by_key["module-collection-set"]["feature"] == "modules"
    assert row_by_key["module-collection-set"]["filters"] == [
        "module_id",
        "collection_id",
        "source_root",
        "write",
        "plan_hash",
    ]
    assert row_by_key["module-collection-set"]["frontend_operation_ids"] == ["module.collection.set"]
    assert row_by_key["module-metadata-clean"]["adapter"] == "Project.clean_module_metadata"
    assert row_by_key["module-metadata-clean"]["feature"] == "modules"
    assert row_by_key["module-metadata-clean"]["filters"] == [
        "family",
        "module_id",
        "source_root",
        "write",
        "plan_hash",
    ]
    assert row_by_key["module-metadata-clean"]["frontend_operation_ids"] == ["module.metadata.clean"]
    assert row_by_key["module-diagram"]["adapter"] == "Project.module_diagram"
    assert row_by_key["module-diagram"]["filters"] == ["family", "profile"]
    assert row_by_key["module-diagram"]["frontend_operation_ids"] == ["module.diagram"]
    assert row_by_key["module-diagram-edit"]["adapter"] == ("Project.edit_module_diagram")
    assert row_by_key["module-diagram-edit"]["frontend_operation_ids"] == ["module.diagram.edit"]
    assert row_by_key["hb catalog-write"]["frontend_operation_ids"] == ["catalog.write"]
    assert row_by_key["inspections and inspection commands"]["symbol"] == "CLI binding: inspections and inspection commands"
    assert row_by_key["inspections and inspection commands"]["kind"] == "binding variant"
    assert reference.startswith("# CLI API Reference\n")
    assert "Generated from `paradev.surfaces.cli.get_cli_api_table()`." in reference
    assert "| `command group` | 4 | `paradev config`, `paradev hb`, `paradev mcp`, `paradev lsp` |" in reference
    assert (
        "| `api-catalog` | 4 | `paradev api-catalog`, `paradev api-catalog --reference`, "
        "`paradev api-catalog --index --key`, `paradev api-catalog --markdown` |"
    ) in reference
    assert (
        "| `package` | 4 | `paradev package-api`, `paradev package-api --markdown`, `paradev package-api --symbol`, `paradev package-api --index --key` |"
        in reference
    )
    assert "| `gui` | 4 | `paradev gui-api`, `paradev gui-api --markdown`, `paradev gui-api --symbol`, `paradev gui-api --index --key` |" in reference
    assert (
        "| `desktop` | 5 | `paradev desktop-api`, `paradev desktop-api --markdown`, `paradev desktop-api --typescript`, `paradev desktop-api --symbol`, `paradev desktop-api --index --key` |"
        in reference
    )
    assert "| `games` | 4 | `paradev games-api`, `paradev games-api --markdown`, `paradev games-api --symbol`, `paradev games-api --index --key` |" in reference
    assert (
        "| `authoring` | 9 | `paradev templates-api`, `paradev module-batch-create`, `paradev templates`, `paradev authoring-path`, "
        "`paradev authoring-plan`, `paradev scaffold`, `paradev templates-api --markdown`, "
        "`paradev templates-api --symbol`, `paradev templates-api --index --key` |"
    ) in reference
    assert (
        "| `copy-roots` | 4 | `paradev copy-roots-api`, `paradev copy-roots-api --markdown`, `paradev copy-roots-api --symbol`, `paradev copy-roots-api --index --key` |"
        in reference
    )
    assert "| `config` | 14 | `paradev config-api`, `paradev config`, `paradev config get`," in reference
    assert (
        "| `surfaces` | 4 | `paradev surfaces-api`, `paradev surfaces-api --markdown`, `paradev surfaces-api --symbol`, `paradev surfaces-api --index --key` |"
        in reference
    )
    assert "| `cli` | 4 | `paradev cli-api`, `paradev cli-api --markdown`, `paradev cli-api --symbol`, `paradev cli-api --index --key` |" in reference
    assert "| `sdk` | 4 | `paradev sdk-api`, `paradev sdk-api --markdown`, `paradev sdk-api --symbol`, `paradev sdk-api --index --key` |" in reference
    assert (
        "| `localization` | 4 | `paradev localization-api`, `paradev localization-api --markdown`, `paradev localization-api --symbol`, `paradev localization-api --index --key` |"
        in reference
    )
    assert ("| `lsp` | 17 | `paradev lsp-api`, `paradev lsp-server-api`, `paradev lsp`, `paradev lsp serve`, " "`paradev lsp diagnostics`,") in reference
    assert (
        "| `rest` | 8 | `paradev rest-api`, `paradev rest-facade-api`, `paradev rest-api --markdown`, "
        "`paradev rest-facade-api --markdown`, `paradev rest-api --symbol`, `paradev rest-api --index --key`, "
        "`paradev rest-facade-api --symbol`, `paradev rest-facade-api --index --key` |"
    ) in reference
    assert (
        "| `pdx` | 12 | `paradev pdx-api`, `paradev pdx-core-api`, `paradev parse`, `paradev format`, "
        "`paradev pdx-api --markdown`, `paradev pdx-core-api --markdown`, `paradev pdx-api --symbol`, "
        "`paradev pdx-api --index --key`, `paradev pdx-core-api --symbol`, `paradev pdx-core-api --index --key`, "
        "`paradev parse --tokens`, `paradev parse --dump` |"
    ) in reference
    assert "| `projects` | 17 |" in reference
    assert (
        "| `inspections` | 5 | `paradev inspections`, `paradev inspections --kind`, "
        "`paradev inspections --index --key`, `paradev inspections --markdown`, `CLI binding: inspections and inspection commands` |"
    ) in reference
    assert "| `build` | 25 |" in reference
    assert (
        "| `get_api_catalog_selection` | 3 | `paradev api-catalog`, `paradev api-catalog --reference`, " "`paradev api-catalog --index --key` |"
    ) in reference
    assert ("| `get_surface_contract_selection` | 2 | `paradev architecture --surface-contract`, " "`paradev architecture --surface-contracts` |") in reference
    assert (
        "| `get_frontend_api_selection` | 5 | `paradev frontend-api`, `paradev frontend-api --operation`, "
        "`paradev frontend-api --group`, `paradev frontend-api --operation --form`, `paradev frontend-api --index --key` |"
    ) in reference
    assert "| `get_project_inspection_selection` | 3 | `paradev inspections`, `paradev inspections --kind`, `paradev inspections --index --key` |" in reference
    for command_key, selector_helper, _ in standard_api_selectors:
        assert (
            f"| `{selector_helper}` | 3 | `paradev {command_key}`, `paradev {command_key} --symbol`, " f"`paradev {command_key} --index --key` |"
        ) in reference
    assert "| `surface.frontend_api.action` | 1 | `paradev frontend-api --operation --action` |" in reference
    assert (
        "| `paradev frontend-api --operation --action` | `command projection` | `cli` | `frontend-api` | "
        "`frontend-api --operation --action` | `get_frontend_api_action` | `operation_id`, `group_id`, `index_name`, `key` | "
        "`operation`, `action` | `CLI output from get_frontend_api_action` | `Typer validation errors` | "
        "`surface.frontend_api.action` |"
    ) in reference
    assert (
        "| `paradev api-catalog` | `command` | `cli` | `api-catalog` | `api-catalog` | `get_api_catalog_selection` | "
        "`reference_id`, `index_name`, `key` | "
        "`reference`, `index`, `key`, `markdown` | `CLI output from get_api_catalog_selection` | `Typer validation errors` |"
    ) in reference
    assert (
        "| `paradev api-catalog --reference` | `command projection` | `cli` | `api-catalog` | `api-catalog --reference` | "
        "`get_api_catalog_selection` | `reference_id`, `index_name`, `key` | `reference` | "
        "`CLI output from get_api_catalog_selection` | `Typer validation errors` |"
    ) in reference
    assert (
        "| `paradev api-catalog --index --key` | `command projection` | `cli` | `api-catalog` | `api-catalog --index --key` | "
        "`get_api_catalog_selection` | `reference_id`, `index_name`, `key` | `index`, `key` | "
        "`CLI output from get_api_catalog_selection` | `Typer validation errors` |"
    ) in reference
    assert (
        "| `paradev inspections --kind` | `command projection` | `cli` | `inspections` | "
        "`inspections --kind` | `get_project_inspection_selection` | `kind`, `index_name`, `key` | "
        "`kind` | `CLI output from get_project_inspection_selection` | `Typer validation errors` |"
    ) in reference
    assert (
        "| `paradev architecture --surface-contract` | `command projection` | `cli` | `architecture` | "
        "`architecture --surface-contract` | `get_surface_contract_selection` |  | `surface-contract` | "
        "`CLI output from get_surface_contract_selection` | `Typer validation errors` |"
    ) in reference
    assert (
        "| `paradev architecture --surface-contracts` | `command projection` | `cli` | `architecture` | "
        "`architecture --surface-contracts` | `get_surface_contract_selection` |  | `surface-contracts` | "
        "`CLI output from get_surface_contract_selection` | `Typer validation errors` |"
    ) in reference
    for command_key, selector_helper, _ in standard_api_selectors:
        assert (
            f"| `paradev {command_key}` | `command` | `cli` | `{standard_api_features[command_key]}` | "
            f"`{command_key}` | `{selector_helper}` | `symbol`, `index_name`, `key` | "
            "`symbol`, `index`, `key`, `markdown` | "
            f"`CLI output from {selector_helper}` | `Typer validation errors` |"
        ) in reference
    assert (
        "| `paradev package-api --symbol` | `command projection` | `cli` | `package` | "
        "`package-api --symbol` | `get_package_api_selection` | `symbol`, `index_name`, `key` | "
        "`symbol` | `CLI output from get_package_api_selection` | `Typer validation errors` |"
    ) in reference
    assert (
        "| `paradev cli-api --index --key` | `command projection` | `cli` | `cli` | "
        "`cli-api --index --key` | `get_cli_api_selection` | `symbol`, `index_name`, `key` | "
        "`index`, `key` | `CLI output from get_cli_api_selection` | `Typer validation errors` |"
    ) in reference
    manual = Path("docs/user-manual/cli-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_cli_api_table()["rows"][0]["symbol"] == "paradev architecture"
    table["frontend_operation_index"]["catalog.write"].append("paradev cli-api")
    assert get_cli_api_table()["frontend_operation_index"]["catalog.write"] == ["paradev hb catalog-write"]


def test_mcp_surface_contract_lists_sdk_owned_tools() -> None:
    from paradev.sdk import get_frontend_api_binding_index
    from paradev.surfaces.mcp import get_mcp_contract

    contract = get_mcp_contract()

    tools = {tool["name"]: tool for tool in contract["tool_contracts"]}
    assert contract["identifier"] == "mcp"
    assert contract["sdk_owned"] is True
    assert "project_inspections" in contract["tools"]
    assert "project_inspect" in contract["tools"]
    assert "project_templates" in contract["tools"]
    assert "project_authoring_path" in contract["tools"]
    assert "project_authoring_plan" in contract["tools"]
    assert "project_scaffold" in contract["tools"]
    assert "project_create_modules" in contract["tools"]
    assert "project_create" in contract["tools"]
    assert "project_open" in contract["tools"]
    assert "project_view" in contract["tools"]
    assert "project_find" in contract["tools"]
    assert "project_rename" in contract["tools"]
    assert "module_rename" in contract["tools"]
    assert "module_duplicate" in contract["tools"]
    assert "module_collection_set" in contract["tools"]
    assert "module_metadata_clean" in contract["tools"]
    assert "module_diagram" in contract["tools"]
    assert "module_diagram_edit" in contract["tools"]
    assert "module_remove" in contract["tools"]
    assert "module_file" in contract["tools"]
    assert "module_asset" in contract["tools"]
    assert "module_source_form" in contract["tools"]
    assert "module_source_form_update" in contract["tools"]
    assert "module_source_form_update_batch" in contract["tools"]
    assert "localization_workspace" in contract["tools"]
    assert "localization_plan" in contract["tools"]
    assert "module_edit" in contract["tools"]
    assert "collection_file" in contract["tools"]
    assert "collection_edit" in contract["tools"]
    assert "collection_create" in contract["tools"]
    assert "collection_scaffold" in contract["tools"]
    assert "collection_rename" in contract["tools"]
    assert "collection_remove" in contract["tools"]
    assert "pdx_parse" in contract["tools"]
    assert "pdx_format" in contract["tools"]
    assert "lsp_api" in contract["tools"]
    assert "catalog_api" in contract["tools"]
    assert "mcp_api" in contract["tools"]
    assert "api_catalog" in contract["tools"]
    assert "surface_contracts" in contract["tools"]
    assert "frontend_api" in contract["tools"]
    assert tools["project_inspections"] == {
        "name": "project_inspections",
        "sdk_method": "Project.inspect('inspections')",
        "read_only": True,
    }
    assert tools["project_inspect"]["sdk_method"] == "Project.inspect"
    assert "modules" in tools["project_inspect"]["inspection_contract"]["index"]["filter"]["module_id"]
    assert tools["project_templates"] == {
        "name": "project_templates",
        "sdk_method": "Project.templates",
        "read_only": True,
        "filters": [
            "template_id",
            "family",
            "kind",
            "source",
            "authoring_ready",
            "diagnostic_code",
        ],
    }
    assert tools["project_authoring_path"] == {
        "name": "project_authoring_path",
        "sdk_method": "Project.authoring_path",
        "read_only": True,
    }
    assert tools["project_authoring_plan"] == {
        "name": "project_authoring_plan",
        "sdk_method": "Project.authoring_plan",
        "read_only": True,
    }
    assert tools["project_scaffold"] == {
        "name": "project_scaffold",
        "sdk_method": "Project.scaffold_module",
        "read_only": False,
    }
    assert tools["project_create_modules"] == {
        "name": "project_create_modules",
        "sdk_method": "Project.create_modules",
        "read_only": False,
    }
    assert tools["project_preferred_language"] == {
        "name": "project_preferred_language",
        "sdk_method": "Project.set_preferred_language",
        "read_only": False,
    }
    assert tools["project_draft_apply"] == {
        "name": "project_draft_apply",
        "sdk_method": "Project.apply_source_draft",
        "read_only": False,
    }
    assert tools["collection_scaffold"] == {
        "name": "collection_scaffold",
        "sdk_method": "Project.scaffold_collection",
        "read_only": False,
    }
    assert tools["module_duplicate"] == {
        "name": "module_duplicate",
        "sdk_method": "Project.duplicate_module",
        "read_only": False,
    }
    assert tools["module_collection_set"] == {
        "name": "module_collection_set",
        "sdk_method": "Project.set_module_collection",
        "read_only": False,
    }
    assert tools["module_activity_set"] == {
        "name": "module_activity_set",
        "sdk_method": "Project.set_module_active",
        "read_only": False,
    }
    assert tools["module_metadata_clean"] == {
        "name": "module_metadata_clean",
        "sdk_method": "Project.clean_module_metadata",
        "read_only": False,
    }
    assert tools["module_diagram"] == {
        "name": "module_diagram",
        "sdk_method": "Project.module_diagram",
        "read_only": True,
    }
    assert tools["module_diagram_edit"] == {
        "name": "module_diagram_edit",
        "sdk_method": "Project.edit_module_diagram",
        "read_only": False,
    }
    assert contract["runtime_tools"] == [
        "project_templates",
        "project_authoring_path",
        "project_authoring_plan",
        "project_browser",
        "module_file",
        "collection_file",
        "module_asset",
        "module_source_form",
        "module_source_form_update",
        "module_source_form_update_batch",
        "localization_workspace",
        "localization_plan",
        "project_create_modules",
        "project_preferred_language",
        "project_draft_apply",
        "collection_scaffold",
        "collection_remove",
        "module_duplicate",
        "module_collection_set",
        "module_activity_set",
        "module_metadata_clean",
        "module_diagram",
        "module_diagram_edit",
    ]
    assert contract["toolkit_factory"] == "create_authoring_mcp_toolkit"
    assert contract["transport"] == "stdio"
    assert contract["server_command"] == "paradev mcp serve"
    assert contract["runtime_status"] == "implemented"
    assert contract["runtime_scope"] == "authoring"
    assert contract["stdio_server"] == "serve_authoring_mcp_stdio"
    assert tools["project_create"] == {
        "name": "project_create",
        "sdk_method": "Project.create",
        "read_only": False,
    }
    assert tools["project_open"] == {
        "name": "project_open",
        "sdk_method": "Project.load",
        "read_only": True,
    }
    assert tools["project_view"] == {
        "name": "project_view",
        "sdk_method": "Project.to_view",
        "read_only": True,
    }
    assert tools["project_browser"] == {
        "name": "project_browser",
        "sdk_method": "Project.browser",
        "read_only": True,
    }
    assert tools["project_find"] == {
        "name": "project_find",
        "sdk_method": "Project.find",
        "read_only": True,
    }
    assert tools["project_rename"] == {
        "name": "project_rename",
        "sdk_method": "Project.rename",
        "read_only": False,
    }
    assert tools["module_rename"] == {
        "name": "module_rename",
        "sdk_method": "Project.rename_module",
        "read_only": False,
    }
    assert tools["module_remove"] == {
        "name": "module_remove",
        "sdk_method": "Project.remove_module",
        "read_only": False,
    }
    assert tools["module_file"] == {
        "name": "module_file",
        "sdk_method": "Project.read_module_file",
        "read_only": True,
    }
    assert tools["module_asset"] == {
        "name": "module_asset",
        "sdk_method": "Project.read_module_asset",
        "read_only": True,
    }
    assert tools["module_source_form"] == {
        "name": "module_source_form",
        "sdk_method": "Project.read_module_file + Project.source_form",
        "read_only": True,
    }
    assert tools["module_source_form_update"] == {
        "name": "module_source_form_update",
        "sdk_method": "Project.read_module_file + Project.plan_source_form_update",
        "read_only": True,
    }
    assert tools["module_source_form_update_batch"] == {
        "name": "module_source_form_update_batch",
        "sdk_method": "Project.read_module_file + Project.plan_source_form_updates",
        "read_only": True,
    }
    assert tools["module_edit"] == {
        "name": "module_edit",
        "sdk_method": "Project.write_module_file",
        "read_only": False,
    }
    assert tools["collection_file"] == {
        "name": "collection_file",
        "sdk_method": "Project.read_collection_file",
        "read_only": True,
    }
    assert tools["collection_edit"] == {
        "name": "collection_edit",
        "sdk_method": "Project.write_collection_file",
        "read_only": False,
    }
    assert tools["collection_create"] == {
        "name": "collection_create",
        "sdk_method": "Project.create_collection",
        "read_only": False,
    }
    assert tools["collection_rename"] == {
        "name": "collection_rename",
        "sdk_method": "Project.rename_collection",
        "read_only": False,
    }
    assert tools["collection_remove"] == {
        "name": "collection_remove",
        "sdk_method": "Project.remove_collection",
        "read_only": False,
    }
    assert tools["pdx_parse"]["sdk_method"] == "parse_pdx_file"
    assert tools["pdx_format"] == {
        "name": "pdx_format",
        "sdk_method": "format_pdx_file",
        "read_only": False,
    }
    assert tools["frontend_api"] == {
        "name": "frontend_api",
        "sdk_method": "get_frontend_api_selection",
        "read_only": True,
        "selectors": ["operation_id", "group_id", "index_name", "key"],
    }
    assert tools["api_catalog"] == {
        "name": "api_catalog",
        "sdk_method": "get_api_catalog_selection",
        "read_only": True,
        "selectors": ["reference_id", "index_name", "key"],
    }
    assert tools["catalog_api"] == {
        "name": "catalog_api",
        "sdk_method": "get_catalog_api_selection",
        "read_only": True,
        "selectors": ["symbol", "index_name", "key"],
    }
    assert tools["mcp_api"] == {
        "name": "mcp_api",
        "sdk_method": "get_mcp_api_selection",
        "read_only": True,
        "selectors": ["symbol", "index_name", "key"],
    }
    assert tools["surface_contracts"] == {
        "name": "surface_contracts",
        "sdk_method": "get_surface_contract_selection",
        "read_only": True,
        "selectors": ["identifier", "status"],
    }
    assert tools["lsp_api"] == {
        "name": "lsp_api",
        "sdk_method": "get_lsp_api_selection",
        "read_only": True,
        "selectors": ["symbol", "index_name", "key"],
    }
    assert contract["frontend_operation_ids"] == get_frontend_api_binding_index("mcp")
    assert contract["frontend_operation_ids"]["project_inspect"][:5] == [
        "project.inspect",
        "module.list",
        "module.view",
        "module.source_slots",
        "module.sources",
    ]
    assert "collection.sources" in contract["frontend_operation_ids"]["project_inspect"]
    assert "catalog.query" in contract["frontend_operation_ids"]["project_inspect"]
    assert contract["frontend_operation_ids"]["project_open"] == ["project.open"]
    assert contract["frontend_operation_ids"]["project_view"] == ["project.view"]
    assert contract["frontend_operation_ids"]["project_browser"] == ["project.browser"]
    assert contract["frontend_operation_ids"]["collection_rename"] == ["collection.rename"]
    assert contract["frontend_operation_ids"]["collection_remove"] == ["collection.remove"]
    assert contract["frontend_operation_ids"]["collection_scaffold"] == ["collection.scaffold"]
    assert contract["frontend_operation_ids"]["localization_workspace"] == ["localization.workspace"]
    assert contract["frontend_operation_ids"]["localization_plan"] == ["localization.plan"]
    assert contract["frontend_operation_ids"]["pdx_format"] == ["pdx.format"]


def test_mcp_api_table_lists_tool_contracts() -> None:
    from typing_extensions import is_typeddict

    from paradev.surfaces.mcp import (
        MCP_API_TABLE_SCHEMA,
        McpApiRow,
        McpApiTable,
        get_mcp_api_table,
        get_mcp_contract,
        render_mcp_api_reference_markdown,
    )

    contract = get_mcp_contract()
    table = get_mcp_api_table()
    rows = table["rows"]
    row_by_symbol = {row["symbol"]: row for row in rows}
    reference = render_mcp_api_reference_markdown()

    assert is_typeddict(McpApiRow)
    assert is_typeddict(McpApiTable)
    assert table["schema"] == MCP_API_TABLE_SCHEMA
    assert table["row_count"] == len(contract["tool_contracts"]) == 51 == len(rows)
    assert set(McpApiRow.__annotations__) == {
        "symbol",
        "kind",
        "layer",
        "feature",
        "mode",
        "sdk_method",
        "inputs",
        "returns",
        "raises",
        "registry_seam",
        "surface",
        "frontend_operation_ids",
        "doc_page",
        "test_anchor",
    }
    assert set(McpApiTable.__annotations__) == {
        "schema",
        "row_count",
        "mode_index",
        "feature_index",
        "frontend_operation_index",
        "rows",
    }
    assert len(table["mode_index"]["read"]) == 31
    assert len(table["mode_index"]["write"]) == 20
    assert table["feature_index"]["authoring"] == [
        "project_templates",
        "project_authoring_path",
        "project_authoring_plan",
        "project_scaffold",
        "project_create_modules",
        "project_draft_apply",
        "collection_scaffold",
        "localization_workspace",
        "localization_plan",
    ]
    assert table["feature_index"]["pdx"] == ["pdx_parse", "pdx_format", "pdx_api"]
    assert table["feature_index"]["lsp"] == ["lsp_api"]
    assert table["feature_index"]["catalog"] == ["catalog_api"]
    assert table["feature_index"]["mcp"] == ["mcp_api"]
    assert table["feature_index"]["cli"] == ["cli_api"]
    assert table["feature_index"]["api-catalog"] == ["api_catalog"]
    assert table["feature_index"]["surface-contracts"] == ["surface_contracts"]
    assert table["frontend_operation_index"]["catalog.query"] == ["project_inspect"]
    assert table["frontend_operation_index"]["module.create"] == ["project_scaffold"]
    assert table["frontend_operation_index"]["collection.scaffold"] == ["collection_scaffold"]
    assert row_by_symbol["collection_scaffold"]["sdk_method"] == ("Project.scaffold_collection")
    assert row_by_symbol["collection_scaffold"]["mode"] == "write"
    assert row_by_symbol["project_inspect"]["inputs"] == "path, kind, filters"
    assert row_by_symbol["project_inspect"]["returns"] == "Project inspection payload"
    assert row_by_symbol["frontend_api"]["inputs"] == "operation_id, group_id, index_name, key"
    assert row_by_symbol["api_catalog"]["mode"] == "read"
    assert row_by_symbol["api_catalog"]["inputs"] == "reference_id, index_name, key"
    assert row_by_symbol["api_catalog"]["returns"] == "API catalog table, row, or index lookup payload"
    assert row_by_symbol["api_catalog"]["raises"] == "ValueError or KeyError on invalid API catalog selector"
    assert row_by_symbol["catalog_api"]["mode"] == "read"
    assert row_by_symbol["catalog_api"]["inputs"] == "symbol, index_name, key"
    assert row_by_symbol["catalog_api"]["returns"] == "Catalog API table, row, or index lookup payload"
    assert row_by_symbol["catalog_api"]["raises"] == "ValueError or KeyError on invalid catalog API selector"
    assert row_by_symbol["mcp_api"]["mode"] == "read"
    assert row_by_symbol["mcp_api"]["inputs"] == "symbol, index_name, key"
    assert row_by_symbol["mcp_api"]["returns"] == "MCP API table, row, or index lookup payload"
    assert row_by_symbol["mcp_api"]["raises"] == "ValueError or KeyError on invalid MCP API selector"
    assert row_by_symbol["cli_api"]["mode"] == "read"
    assert row_by_symbol["cli_api"]["inputs"] == "symbol, index_name, key"
    assert row_by_symbol["cli_api"]["returns"] == "CLI API table, row, or index lookup payload"
    assert row_by_symbol["cli_api"]["raises"] == "ValueError or KeyError on invalid CLI API selector"
    assert row_by_symbol["surface_contracts"]["mode"] == "read"
    assert row_by_symbol["surface_contracts"]["inputs"] == "identifier, status"
    assert row_by_symbol["surface_contracts"]["returns"] == "Surface contract summary, contract payload, or status id list"
    assert row_by_symbol["surface_contracts"]["raises"] == "ValueError or KeyError on invalid surface contract selector"
    assert row_by_symbol["lsp_api"]["mode"] == "read"
    assert row_by_symbol["lsp_api"]["inputs"] == "symbol, index_name, key"
    assert row_by_symbol["lsp_api"]["returns"] == "LSP API table, row, or index lookup payload"
    assert row_by_symbol["lsp_api"]["raises"] == "ValueError or KeyError on invalid LSP API selector"
    assert row_by_symbol["project_scaffold"]["mode"] == "write"
    assert row_by_symbol["project_scaffold"]["inputs"] == "path, template_id, object_id, source_root, values, write, force"
    assert row_by_symbol["project_create_modules"] == {
        "symbol": "project_create_modules",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "authoring",
        "mode": "write",
        "sdk_method": "Project.create_modules",
        "inputs": "path, modules, source_root, write, plan_hash",
        "returns": "SDK atomic module batch plan or apply payload",
        "raises": "ProjectManifestError, OSError, or ValueError on invalid module batch",
        "registry_seam": "MCP tool registry: project_create_modules",
        "surface": "mcp",
        "frontend_operation_ids": ["module.create_batch"],
        "doc_page": "docs/user-manual/mcp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts",
    }
    assert row_by_symbol["project_draft_apply"] == {
        "symbol": "project_draft_apply",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "authoring",
        "mode": "write",
        "sdk_method": "Project.apply_source_draft",
        "inputs": ("path, source_edits, source_removals, source_replacements, " "module_rename"),
        "returns": "SDK source-draft apply payload",
        "raises": ("ProjectManifestError, OSError, or ValueError on invalid source draft"),
        "registry_seam": "MCP tool registry: project_draft_apply",
        "surface": "mcp",
        "frontend_operation_ids": ["project.draft_apply"],
        "doc_page": "docs/user-manual/mcp-api-reference.md",
        "test_anchor": ("tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts"),
    }
    assert row_by_symbol["collection_scaffold"] == {
        "symbol": "collection_scaffold",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "authoring",
        "mode": "write",
        "sdk_method": "Project.scaffold_collection",
        "inputs": ("path, template_id, collection_id, values, source_root, write, " "force, plan_hash"),
        "returns": "SDK guarded collection scaffold plan or apply payload",
        "raises": ("ProjectManifestError, OSError, or ValueError on invalid " "collection scaffold"),
        "registry_seam": "MCP tool registry: collection_scaffold",
        "surface": "mcp",
        "frontend_operation_ids": ["collection.scaffold"],
        "doc_page": "docs/user-manual/mcp-api-reference.md",
        "test_anchor": ("tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts"),
    }
    assert row_by_symbol["module_duplicate"] == {
        "symbol": "module_duplicate",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "modules",
        "mode": "write",
        "sdk_method": "Project.duplicate_module",
        "inputs": "path, module_id, object_id, source_root, destination_source_root, write, plan_hash",
        "returns": "SDK guarded module duplicate plan or apply payload",
        "raises": "ProjectManifestError, OSError, or ValueError on invalid module duplicate",
        "registry_seam": "MCP tool registry: module_duplicate",
        "surface": "mcp",
        "frontend_operation_ids": ["module.duplicate"],
        "doc_page": "docs/user-manual/mcp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts",
    }
    assert row_by_symbol["module_collection_set"] == {
        "symbol": "module_collection_set",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "modules",
        "mode": "write",
        "sdk_method": "Project.set_module_collection",
        "inputs": "path, module_id, collection_id, source_root, write, plan_hash",
        "returns": "SDK guarded module collection plan or apply payload",
        "raises": "ProjectManifestError, OSError, or ValueError on invalid module collection",
        "registry_seam": "MCP tool registry: module_collection_set",
        "surface": "mcp",
        "frontend_operation_ids": ["module.collection.set"],
        "doc_page": "docs/user-manual/mcp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts",
    }
    assert row_by_symbol["module_metadata_clean"] == {
        "symbol": "module_metadata_clean",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "modules",
        "mode": "write",
        "sdk_method": "Project.clean_module_metadata",
        "inputs": "path, family, module_id, source_root, write, plan_hash",
        "returns": "SDK guarded module metadata cleanup plan or apply payload",
        "raises": "ProjectManifestError, OSError, or ValueError on invalid metadata cleanup",
        "registry_seam": "MCP tool registry: module_metadata_clean",
        "surface": "mcp",
        "frontend_operation_ids": ["module.metadata.clean"],
        "doc_page": "docs/user-manual/mcp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts",
    }
    assert row_by_symbol["module_diagram"]["mode"] == "read"
    assert row_by_symbol["module_diagram"]["sdk_method"] == ("Project.module_diagram")
    assert row_by_symbol["module_diagram"]["frontend_operation_ids"] == ["module.diagram"]
    assert row_by_symbol["module_diagram_edit"]["mode"] == "write"
    assert row_by_symbol["module_diagram_edit"]["sdk_method"] == ("Project.edit_module_diagram")
    assert row_by_symbol["module_diagram_edit"]["frontend_operation_ids"] == ["module.diagram.edit"]
    assert row_by_symbol["module_asset"] == {
        "symbol": "module_asset",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "modules",
        "mode": "read",
        "sdk_method": "Project.read_module_asset",
        "inputs": "path, module_id, relative_path, source_root, include_content",
        "returns": "Registry-owned module asset payload",
        "raises": ("ProjectManifestError, OSError, or ValueError on invalid module asset"),
        "registry_seam": "MCP tool registry: module_asset",
        "surface": "mcp",
        "frontend_operation_ids": [],
        "doc_page": "docs/user-manual/mcp-api-reference.md",
        "test_anchor": ("tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts"),
    }
    assert row_by_symbol["module_source_form"] == {
        "symbol": "module_source_form",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "modules",
        "mode": "read",
        "sdk_method": "Project.read_module_file + Project.source_form",
        "inputs": "path, module_id, relative_path, source_root, encoding",
        "returns": ("Stable module file snapshot plus optional Registry-owned source form"),
        "raises": ("ProjectManifestError, OSError, or ValueError on invalid module " "source form"),
        "registry_seam": "MCP tool registry: module_source_form",
        "surface": "mcp",
        "frontend_operation_ids": [],
        "doc_page": "docs/user-manual/mcp-api-reference.md",
        "test_anchor": ("tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts"),
    }
    assert row_by_symbol["module_source_form_update"] == {
        "symbol": "module_source_form_update",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "modules",
        "mode": "read",
        "sdk_method": "Project.read_module_file + Project.plan_source_form_update",
        "inputs": "path, module_id, relative_path, values, source_root, encoding",
        "returns": "Revision-guarded full-text source edit plan from guided control values",
        "raises": "ProjectManifestError, OSError, or ValueError on invalid guided source update",
        "registry_seam": "MCP tool registry: module_source_form_update",
        "surface": "mcp",
        "frontend_operation_ids": [],
        "doc_page": "docs/user-manual/mcp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts",
    }
    assert row_by_symbol["module_source_form_update_batch"] == {
        "symbol": "module_source_form_update_batch",
        "kind": "MCP tool",
        "layer": "mcp",
        "feature": "modules",
        "mode": "read",
        "sdk_method": "Project.read_module_file + Project.plan_source_form_updates",
        "inputs": "path, updates, source_root, encoding",
        "returns": "Atomic draft plan for several guided module source updates",
        "raises": ("ProjectManifestError, OSError, or ValueError on invalid guided " "source update batch"),
        "registry_seam": "MCP tool registry: module_source_form_update_batch",
        "surface": "mcp",
        "frontend_operation_ids": [],
        "doc_page": "docs/user-manual/mcp-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_mcp_api_table_lists_tool_contracts",
    }
    assert row_by_symbol["pdx_format"]["raises"] == "ValueError on invalid PDX format request"
    assert reference.startswith("# MCP API Reference\n")
    assert "Generated from `paradev.surfaces.mcp.get_mcp_api_table()`." in reference
    assert (f"- Runtime server / Runtime server: `{contract['server_command']}` " f"(`{contract['transport']}`)") in reference
    assert (f"- Runtime status / Runtime status: `{contract['runtime_status']}` " f"(`{contract['runtime_scope']}` scope)") in reference
    assert ("| `read` | 31 | `project_inspections`, `project_inspect`, " "`project_templates`,") in reference
    assert (
        "| `write` | 20 | `project_scaffold`, `project_create_modules`, `project_draft_apply`, `collection_scaffold`, `project_create`, `project_rename`, `project_preferred_language`,"
        in reference
    )
    assert (
        "| `authoring` | 9 | `project_templates`, `project_authoring_path`, "
        "`project_authoring_plan`, `project_scaffold`, `project_create_modules`, "
        "`project_draft_apply`, `collection_scaffold`, `localization_workspace`, "
        "`localization_plan` |"
    ) in reference
    assert "| `api-catalog` | 1 | `api_catalog` |" in reference
    assert "| `surface-contracts` | 1 | `surface_contracts` |" in reference
    assert "| `lsp` | 1 | `lsp_api` |" in reference
    assert "| `catalog` | 1 | `catalog_api` |" in reference
    assert "| `mcp` | 1 | `mcp_api` |" in reference
    assert "| `cli` | 1 | `cli_api` |" in reference
    assert "| `catalog.query` | 1 | `project_inspect` |" in reference
    assert (
        "| `frontend_api` | `MCP tool` | `mcp` | `frontend-api` | `read` | "
        "`get_frontend_api_selection` | `operation_id, group_id, index_name, key` | "
        "`Frontend API contract or selected projection` | `ValueError on invalid frontend API selector` |"
    ) in reference
    assert (
        "| `api_catalog` | `MCP tool` | `mcp` | `api-catalog` | `read` | `get_api_catalog_selection` | "
        "`reference_id, index_name, key` | `API catalog table, row, or index lookup payload` | "
        "`ValueError or KeyError on invalid API catalog selector` |"
    ) in reference
    assert (
        "| `catalog_api` | `MCP tool` | `mcp` | `catalog` | `read` | `get_catalog_api_selection` | "
        "`symbol, index_name, key` | `Catalog API table, row, or index lookup payload` | "
        "`ValueError or KeyError on invalid catalog API selector` |"
    ) in reference
    assert (
        "| `mcp_api` | `MCP tool` | `mcp` | `mcp` | `read` | `get_mcp_api_selection` | "
        "`symbol, index_name, key` | `MCP API table, row, or index lookup payload` | "
        "`ValueError or KeyError on invalid MCP API selector` |"
    ) in reference
    assert (
        "| `cli_api` | `MCP tool` | `mcp` | `cli` | `read` | `get_cli_api_selection` | "
        "`symbol, index_name, key` | `CLI API table, row, or index lookup payload` | "
        "`ValueError or KeyError on invalid CLI API selector` |"
    ) in reference
    assert (
        "| `surface_contracts` | `MCP tool` | `mcp` | `surface-contracts` | `read` | "
        "`get_surface_contract_selection` | `identifier, status` | "
        "`Surface contract summary, contract payload, or status id list` | "
        "`ValueError or KeyError on invalid surface contract selector` |"
    ) in reference
    assert (
        "| `project_scaffold` | `MCP tool` | `mcp` | `authoring` | `write` | `Project.scaffold_module` | "
        "`path, template_id, object_id, source_root, values, write, force` | `SDK scaffold draft plan` |  | "
        "`module.create` | `MCP tool registry: project_scaffold` |"
    ) in reference
    manual = Path("docs/user-manual/mcp-api-reference.md").read_text(encoding="utf-8")
    assert manual == reference

    rows[0]["symbol"] = "changed"
    assert get_mcp_api_table()["rows"][0]["symbol"] == "project_inspections"
    table["frontend_operation_index"]["catalog.query"].append("project_inspections")
    assert get_mcp_api_table()["frontend_operation_index"]["catalog.query"] == ["project_inspect"]


def test_lsp_surface_contract_lists_sdk_owned_methods() -> None:
    from paradev.sdk import get_frontend_api_binding_index
    from paradev.surfaces.lsp import get_lsp_contract

    contract = get_lsp_contract()
    methods = {method["method"]: method for method in contract["method_contracts"]}

    assert contract["identifier"] == "lsp"
    assert contract["sdk_owned"] is True
    assert contract["status"] == "implemented"
    assert contract["server_command"] == "paradev lsp serve --project <project-root> --game-root <hoi4-root> --change-diagnostics-max-bytes 50000"
    assert contract["server_framework_target"] == "pygls-compatible"
    assert "codemirror-adapter" in contract["frontend_clients"]
    assert "monaco-languageclient-target" in contract["frontend_clients"]
    assert "HOI4 keyword dataset" in contract["backend_components"]
    assert contract["side_channel"] == "FastAPI REST for non-LSP product actions"
    assert "formatting" in contract["capabilities"]
    assert contract["frontend_operation_ids"] == get_frontend_api_binding_index("lsp")
    assert contract["frontend_operation_ids"]["textDocument/hover"] == ["lsp.hover"]
    assert contract["frontend_operation_ids"]["textDocument/completion"] == ["lsp.completion"]
    assert contract["frontend_operation_ids"]["textDocument/semanticTokens/full"] == ["lsp.semantic_tokens"]
    assert methods["textDocument/publishDiagnostics"] == {
        "method": "textDocument/publishDiagnostics",
        "capability": "diagnostics",
        "sdk_method": "diagnose_pdx_lsp_text",
        "payload": "paradev.lsp.diagnostics.v1",
        "status": "implemented",
    }
    assert methods["textDocument/documentSymbol"] == {
        "method": "textDocument/documentSymbol",
        "capability": "document_symbols",
        "sdk_method": "document_symbols_pdx_lsp_text",
        "payload": "paradev.lsp.symbols.v1",
        "status": "implemented",
    }
    assert methods["textDocument/formatting"] == {
        "method": "textDocument/formatting",
        "capability": "formatting",
        "sdk_method": "format_pdx_lsp_text",
        "payload": "paradev.lsp.formatting.v1",
        "status": "implemented",
    }
    assert methods["textDocument/hover"] == {
        "method": "textDocument/hover",
        "capability": "hover",
        "sdk_method": "hover_pdx_lsp_text",
        "payload": "paradev.lsp.hover.v1",
        "status": "implemented",
    }
    assert methods["textDocument/completion"] == {
        "method": "textDocument/completion",
        "capability": "completion",
        "sdk_method": "complete_pdx_lsp_text",
        "payload": "paradev.lsp.completion.v1",
        "status": "implemented",
    }
    assert methods["textDocument/semanticTokens/full"] == {
        "method": "textDocument/semanticTokens/full",
        "capability": "semantic_tokens",
        "sdk_method": "semantic_tokens_pdx_lsp_text",
        "payload": "paradev.lsp.semantic-tokens.v1",
        "status": "implemented",
    }


def test_vscode_surface_contract_launches_pdx_lsp() -> None:
    from paradev.surfaces.vscode import get_vscode_contract

    contract = get_vscode_contract()
    manifest = json.loads(Path("packages/vscode-paradev/package.json").read_text(encoding="utf-8"))

    assert contract["identifier"] == "vscode"
    assert contract["status"] == "scaffold"
    assert contract["extension_entrypoint"] == "packages/vscode-paradev/src/extension.ts"
    assert contract["lsp_server_command"] == "paradev lsp serve --project <workspace-folder> --game-root <hoi4-root>"
    assert contract["lsp_transport"] == "stdio"
    assert contract["client_role"] == "thin LSP client over SDK-owned PDX semantics"
    assert contract["uses"] == ["lsp", "cli", "rest", "openapi"]
    assert contract["sdk_owned"] is True
    assert manifest["activationEvents"] == [
        "onLanguage:paradox-pdx",
        "workspaceContains:paradev.yaml",
    ]
    assert manifest["contributes"]["languages"][0]["id"] == "paradox-pdx"
    assert manifest["contributes"]["configuration"]["properties"]["paradev.lsp.command"]["default"] == "paradev"
    assert manifest["contributes"]["configuration"]["properties"]["paradev.lsp.args"]["default"] == ["lsp", "serve"]
    assert manifest["contributes"]["configuration"]["properties"]["paradev.lsp.gameRoot"]["default"] == ""
