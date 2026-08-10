import inspect

import pytest

from paradev._api_table import (
    API_STANDARD_INDEXES,
    API_SYMBOL_FIELDS,
    ApiIndexSpec,
    append_api_index_entry,
    append_api_nested_index_entry,
    api_annotation_text,
    api_indexed_table,
    api_table_index_names,
    api_table_index_values,
    api_table_row,
    api_table_selection,
    append_index_entry,
    append_nested_index_entry,
    api_standard_table,
    api_symbol_indexes,
    api_value_indexes,
    copy_api_row,
    copy_api_symbol_row,
)
from paradev._api_table_markdown import (
    ApiIndexSectionSpec,
    api_field_label,
    api_field_table_header,
    api_field_table_rows,
    api_field_table_section,
    api_index_section,
    api_index_sections,
    api_indexed_reference_sections,
    api_index_table_header,
    api_reference_intro_lines,
    api_reference_markdown,
    api_regeneration_command_block,
    api_section_lines,
    api_standard_index_sections,
    api_standard_overview_sections,
    api_standard_reference_markdown,
    api_standard_table_section,
    api_summary_lines,
    api_summary_section,
    api_summary_reference_sections,
    api_surface_reference_markdown,
    api_table_lines,
    api_table_section,
    api_symbol_markdown_value_table_row,
    api_symbol_markdown_value_table_rows,
    api_symbol_table_header,
    api_symbol_table_row,
    api_symbol_table_rows,
    code_list_cell,
    index_row,
    index_rows,
    table_header,
    table_row,
    table_rows,
)


def test_append_index_entry_preserves_key_and_value_types() -> None:
    key = ("GET", "/projects")
    index: dict[tuple[str, str], list[int]] = {}

    append_index_entry(index, key, 1)
    append_index_entry(index, key, 2)

    assert index == {key: [1, 2]}


def test_append_nested_index_entry_preserves_key_and_value_types() -> None:
    outer_key = ("module", "focus")
    index: dict[tuple[str, str], dict[str, list[int]]] = {}

    append_nested_index_entry(index, outer_key, "def", 1)
    append_nested_index_entry(index, outer_key, "def", 2)
    append_nested_index_entry(index, outer_key, "loc", 3)

    assert index == {outer_key: {"def": [1, 2], "loc": [3]}}


def test_append_api_index_entry_coerces_keys_and_values() -> None:
    index: dict[str, list[str]] = {}

    append_api_index_entry(index, "project", "alpha")
    append_api_index_entry(index, 7, 42)
    append_api_index_entry(index, "project", "beta")

    assert index == {"project": ["alpha", "beta"], "7": ["42"]}


def test_append_api_nested_index_entry_coerces_outer_keys_and_values() -> None:
    index: dict[str, dict[str, list[str]]] = {}

    append_api_nested_index_entry(index, "rest", "GET /projects", "project.open")
    append_api_nested_index_entry(index, "rest", "GET /projects", "project.view")
    append_api_nested_index_entry(index, 7, 42, "numeric")

    assert index == {
        "rest": {"GET /projects": ["project.open", "project.view"]},
        "7": {"42": ["numeric"]},
    }


def test_api_symbol_indexes_expands_list_fields_and_skips_empty_keys() -> None:
    rows = (
        {"symbol": "alpha", "feature": "projects", "adapter": "", "operations": ["open", "view"]},
        {"symbol": "beta", "feature": "projects", "adapter": "render_beta", "operations": ["open"]},
    )

    feature_index, adapter_index, operation_index = api_symbol_indexes(
        rows,
        "feature",
        "adapter",
        "operations",
        list_fields=("operations",),
        skip_empty_fields=("adapter",),
    )

    assert feature_index == {"projects": ["alpha", "beta"]}
    assert adapter_index == {"render_beta": ["beta"]}
    assert operation_index == {"open": ["alpha", "beta"], "view": ["alpha"]}


def test_api_value_indexes_supports_custom_value_fields() -> None:
    rows = (
        {"id": "sdk-api", "layer": "sdk", "surfaces": ["sdk", "docs"]},
        {"id": "cli-api", "layer": "surface", "surfaces": ["cli", "docs"]},
    )

    layer_index, surface_index = api_value_indexes(
        rows,
        "layer",
        "surfaces",
        value_field="id",
        list_fields=("surfaces",),
    )

    assert layer_index == {"sdk": ["sdk-api"], "surface": ["cli-api"]}
    assert surface_index == {"sdk": ["sdk-api"], "docs": ["sdk-api", "cli-api"], "cli": ["cli-api"]}


def test_api_value_indexes_rejects_scalar_list_field_values() -> None:
    rows = ({"id": "sdk-api", "surfaces": "sdk"},)

    with pytest.raises(TypeError, match="API table field 'surfaces' must be a list-like value, not str"):
        api_value_indexes(rows, "surfaces", value_field="id", list_fields=("surfaces",))


def test_api_value_indexes_rejects_mapping_list_field_values() -> None:
    rows = ({"id": "sdk-api", "surfaces": {"sdk": True}},)

    with pytest.raises(TypeError, match="API table field 'surfaces' must be a list-like value, not dict"):
        api_value_indexes(rows, "surfaces", value_field="id", list_fields=("surfaces",))


def test_api_value_indexes_rejects_non_string_list_field_values() -> None:
    rows = ({"id": "sdk-api", "surfaces": ["sdk", 42]},)

    with pytest.raises(TypeError, match="API table field 'surfaces' must contain string values, not int"):
        api_value_indexes(rows, "surfaces", value_field="id", list_fields=("surfaces",))


def test_api_value_indexes_rejects_mapping_rows() -> None:
    rows = {"id": "sdk-api", "surface": "sdk"}

    with pytest.raises(TypeError, match="API table rows must be a list-like value, not dict"):
        api_value_indexes(rows, "surface", value_field="id")


def test_api_value_indexes_rejects_scalar_list_fields() -> None:
    rows = ({"id": "sdk-api", "surfaces": ["sdk"]},)

    with pytest.raises(TypeError, match="API table list fields must be a list-like value, not str"):
        api_value_indexes(rows, "surfaces", value_field="id", list_fields="surfaces")


def test_api_value_indexes_rejects_mapping_list_fields() -> None:
    rows = ({"id": "sdk-api", "surfaces": ["sdk"]},)

    with pytest.raises(TypeError, match="API table list fields must be a list-like value, not dict"):
        api_value_indexes(rows, "surfaces", value_field="id", list_fields={"surfaces": True})


def test_api_value_indexes_rejects_non_string_fields() -> None:
    rows = ({"id": "sdk-api", "surface": "sdk"},)

    with pytest.raises(TypeError, match="API table index fields must contain string values, not int"):
        api_value_indexes(rows, 42, value_field="id")


def test_api_table_index_names_lists_index_payload_keys() -> None:
    table = api_indexed_table(
        "test.api-table.v1",
        (
            {"symbol": "alpha", "feature": "projects", "surface": "sdk"},
            {"symbol": "beta", "feature": "projects", "surface": "cli"},
        ),
        (("feature_index", "feature"), ("surface_index", "surface")),
    )
    table["ignored_index"] = ["not", "a", "mapping"]

    assert api_table_index_names(table) == ["feature_index", "surface_index"]


def test_api_table_row_returns_detached_row_by_selected_key() -> None:
    table = api_indexed_table(
        "test.api-table.v1",
        (
            {"symbol": "alpha", "command_key": "alpha", "features": ["sdk"]},
            {"symbol": "beta", "command_key": "beta", "features": ["cli"]},
        ),
        (("symbol_index", "symbol"),),
        row_list_fields=("features",),
    )

    row = api_table_row(table, "command_key", "alpha", row_list_fields=("features",))

    assert row == {"symbol": "alpha", "command_key": "alpha", "features": ["sdk"]}
    row["features"].append("changed")
    assert api_table_row(table, "command_key", "alpha", row_list_fields=("features",))["features"] == ["sdk"]


def test_api_table_row_rejects_unknown_key_with_choices() -> None:
    table = api_indexed_table(
        "test.api-table.v1",
        ({"symbol": "alpha", "command_key": "alpha"},),
        (("symbol_index", "symbol"),),
    )

    with pytest.raises(KeyError, match="unknown API table command_key 'missing'; expected one of: alpha"):
        api_table_row(table, "command_key", "missing")


def test_api_table_index_values_returns_copied_index_values() -> None:
    table = api_indexed_table(
        "test.api-table.v1",
        (
            {"symbol": "alpha", "feature": "projects", "surface": "sdk"},
            {"symbol": "beta", "feature": "projects", "surface": "cli"},
        ),
        (("feature_index", "feature"), ("surface_index", "surface")),
    )

    values = api_table_index_values(table, "feature_index", "projects")

    assert values == ["alpha", "beta"]
    values.append("changed")
    assert api_table_index_values(table, "feature_index", "projects") == ["alpha", "beta"]


def test_api_table_index_values_rejects_unknown_index_and_key() -> None:
    table = api_indexed_table(
        "test.api-table.v1",
        ({"symbol": "alpha", "feature": "projects"},),
        (("feature_index", "feature"),),
    )

    with pytest.raises(ValueError, match="unsupported API table index 'surface_index'; expected one of: feature_index"):
        api_table_index_values(table, "surface_index", "sdk")
    with pytest.raises(ValueError, match="unknown API table feature_index key 'missing'; expected one of: projects"):
        api_table_index_values(table, "feature_index", "missing")


def test_api_table_selection_returns_detached_full_table_without_selectors() -> None:
    table = api_indexed_table(
        "test.api-table.v1",
        (
            {"symbol": "alpha", "feature": "projects", "surfaces": ["sdk"]},
            {"symbol": "beta", "feature": "projects", "surfaces": ["cli"]},
        ),
        (("feature_index", "feature"), ("surface_index", "surfaces")),
        index_list_fields=("surfaces",),
        row_list_fields=("surfaces",),
    )

    selected = api_table_selection(table, row_list_fields=("surfaces",))

    assert selected == table
    selected["rows"][0]["surfaces"].append("changed")
    selected["feature_index"]["projects"].append("changed")
    assert api_table_selection(table, row_list_fields=("surfaces",))["rows"][0]["surfaces"] == ["sdk"]
    assert api_table_selection(table)["feature_index"]["projects"] == ["alpha", "beta"]


def test_api_table_selection_returns_row_or_index_projection() -> None:
    table = api_indexed_table(
        "test.api-table.v1",
        (
            {"symbol": "alpha", "command_key": "alpha", "feature": "projects", "surfaces": ["sdk"]},
            {"symbol": "beta", "command_key": "beta", "feature": "projects", "surfaces": ["cli"]},
        ),
        (("feature_index", "feature"), ("surface_index", "surfaces")),
        index_list_fields=("surfaces",),
        row_list_fields=("surfaces",),
    )

    assert api_table_selection(table, row_key_field="command_key", row_key="alpha", row_list_fields=("surfaces",)) == {
        "symbol": "alpha",
        "command_key": "alpha",
        "feature": "projects",
        "surfaces": ["sdk"],
    }
    assert api_table_selection(table, index_name="surface_index", key="cli") == ["beta"]


def test_api_table_selection_rejects_ambiguous_or_incomplete_selectors() -> None:
    table = api_indexed_table(
        "test.api-table.v1",
        ({"symbol": "alpha", "command_key": "alpha", "feature": "projects"},),
        (("feature_index", "feature"),),
    )

    with pytest.raises(ValueError, match="Pass only one API table selector: command_key or index_name/key."):
        api_table_selection(table, row_key_field="command_key", row_key="alpha", index_name="feature_index", key="projects")
    with pytest.raises(ValueError, match="index_name requires key, and key requires index_name."):
        api_table_selection(table, index_name="feature_index")
    with pytest.raises(ValueError, match="index_name requires key, and key requires index_name."):
        api_table_selection(table, key="projects")


def test_api_value_indexes_rejects_non_string_value_field() -> None:
    rows = ({"id": "sdk-api", "surface": "sdk"},)

    with pytest.raises(TypeError, match="API table value field must be a string value, not int"):
        api_value_indexes(rows, "surface", value_field=42)


def test_api_value_indexes_rejects_non_string_list_fields() -> None:
    rows = ({"id": "sdk-api", "surfaces": ["sdk"]},)

    with pytest.raises(TypeError, match="API table list fields must contain string values, not int"):
        api_value_indexes(rows, "surfaces", value_field="id", list_fields=[42])


def test_api_value_indexes_rejects_scalar_skip_empty_fields() -> None:
    rows = ({"id": "sdk-api", "adapter": ""},)

    with pytest.raises(TypeError, match="API table skip-empty fields must be a list-like value, not str"):
        api_value_indexes(rows, "adapter", value_field="id", skip_empty_fields="adapter")


def test_api_value_indexes_rejects_mapping_skip_empty_fields() -> None:
    rows = ({"id": "sdk-api", "adapter": ""},)

    with pytest.raises(TypeError, match="API table skip-empty fields must be a list-like value, not dict"):
        api_value_indexes(rows, "adapter", value_field="id", skip_empty_fields={"adapter": True})


def test_api_value_indexes_rejects_non_string_skip_empty_fields() -> None:
    rows = ({"id": "sdk-api", "adapter": ""},)

    with pytest.raises(TypeError, match="API table skip-empty fields must contain string values, not int"):
        api_value_indexes(rows, "adapter", value_field="id", skip_empty_fields=[42])


def test_api_value_indexes_rejects_missing_value_field() -> None:
    rows = ({"surface": "sdk"},)

    with pytest.raises(KeyError, match="API table row missing field 'id'"):
        api_value_indexes(rows, "surface", value_field="id")


def test_api_value_indexes_rejects_missing_index_field() -> None:
    rows = ({"id": "sdk-api"},)

    with pytest.raises(KeyError, match="API table row missing field 'surface'"):
        api_value_indexes(rows, "surface", value_field="id")


def test_api_value_indexes_rejects_missing_list_field() -> None:
    rows = ({"id": "sdk-api"},)

    with pytest.raises(KeyError, match="API table row missing field 'surfaces'"):
        api_value_indexes(rows, "surfaces", value_field="id", list_fields=("surfaces",))


def test_copy_api_row_preserves_field_order_and_copies_list_fields() -> None:
    row = {
        "symbol": "cli.project.open",
        "filters": ["template_id"],
        "returns": "Project view",
        "extra": "ignored",
    }

    copied = copy_api_row(row, ("symbol", "filters", "returns"), list_fields=("filters",))
    row["filters"].append("family")

    assert list(copied) == ["symbol", "filters", "returns"]
    assert copied == {
        "symbol": "cli.project.open",
        "filters": ["template_id"],
        "returns": "Project view",
    }


def test_copy_api_row_rejects_scalar_list_field_values() -> None:
    row = {"symbol": "cli.project.open", "filters": "template_id"}

    with pytest.raises(TypeError, match="API table field 'filters' must be a list-like value, not str"):
        copy_api_row(row, ("symbol", "filters"), list_fields=("filters",))


def test_copy_api_row_rejects_mapping_list_field_values() -> None:
    row = {"symbol": "cli.project.open", "filters": {"template_id": True}}

    with pytest.raises(TypeError, match="API table field 'filters' must be a list-like value, not dict"):
        copy_api_row(row, ("symbol", "filters"), list_fields=("filters",))


def test_copy_api_row_rejects_non_string_list_field_values() -> None:
    row = {"symbol": "cli.project.open", "filters": ["template_id", 42]}

    with pytest.raises(TypeError, match="API table field 'filters' must contain string values, not int"):
        copy_api_row(row, ("symbol", "filters"), list_fields=("filters",))


def test_copy_api_row_rejects_scalar_fields() -> None:
    row = {"symbol": "cli.project.open", "filters": ["template_id"]}

    with pytest.raises(TypeError, match="API table row fields must be a list-like value, not str"):
        copy_api_row(row, "symbol")


def test_copy_api_row_rejects_mapping_fields() -> None:
    row = {"symbol": "cli.project.open", "filters": ["template_id"]}

    with pytest.raises(TypeError, match="API table row fields must be a list-like value, not dict"):
        copy_api_row(row, {"symbol": True})


def test_copy_api_row_rejects_non_string_fields() -> None:
    row = {"symbol": "cli.project.open", "filters": ["template_id"]}

    with pytest.raises(TypeError, match="API table row fields must contain string values, not int"):
        copy_api_row(row, [42])


def test_copy_api_row_rejects_scalar_list_fields() -> None:
    row = {"symbol": "cli.project.open", "filters": ["template_id"]}

    with pytest.raises(TypeError, match="API table list fields must be a list-like value, not str"):
        copy_api_row(row, ("symbol", "filters"), list_fields="filters")


def test_copy_api_row_rejects_mapping_list_fields() -> None:
    row = {"symbol": "cli.project.open", "filters": ["template_id"]}

    with pytest.raises(TypeError, match="API table list fields must be a list-like value, not dict"):
        copy_api_row(row, ("symbol", "filters"), list_fields={"filters": True})


def test_copy_api_row_rejects_non_string_list_fields() -> None:
    row = {"symbol": "cli.project.open", "filters": ["template_id"]}

    with pytest.raises(TypeError, match="API table list fields must contain string values, not int"):
        copy_api_row(row, ("symbol", "filters"), list_fields=[42])


def test_copy_api_row_rejects_missing_field() -> None:
    row = {"symbol": "cli.project.open"}

    with pytest.raises(KeyError, match="API table row missing field 'returns'"):
        copy_api_row(row, ("symbol", "returns"))


def test_copy_api_row_rejects_missing_list_field() -> None:
    row = {"symbol": "cli.project.open"}

    with pytest.raises(KeyError, match="API table row missing field 'filters'"):
        copy_api_row(row, ("symbol", "filters"), list_fields=("filters",))


def test_copy_api_row_rejects_scalar_row() -> None:
    with pytest.raises(TypeError, match="API table row must be a mapping value, not str"):
        copy_api_row("symbol")


def test_copy_api_row_rejects_non_string_row_keys() -> None:
    with pytest.raises(TypeError, match="API table row keys must be string values, not int"):
        copy_api_row({42: "open_project"})


def test_copy_api_symbol_row_returns_canonical_detached_fields() -> None:
    row = _api_symbol_row(extra="ignored")

    copied = copy_api_symbol_row(row)
    row["symbol"] = "mutated"

    assert tuple(copied) == API_SYMBOL_FIELDS
    assert copied["symbol"] == "open_project"
    assert "extra" not in copied


def test_api_standard_table_returns_schema_indexes_and_copied_rows() -> None:
    rows = [
        _api_symbol_row(),
        _api_symbol_row(
            symbol="Project",
            kind="dataclass",
            import_path="paradev.sdk.Project",
            returns="Project class",
        ),
    ]

    table = api_standard_table("paradev.sdk.api-table.v1", rows)
    rows[0]["symbol"] = "mutated"

    assert table == {
        "schema": "paradev.sdk.api-table.v1",
        "row_count": 2,
        "module_index": {"sdk.project": ["open_project", "Project"]},
        "feature_index": {"projects": ["open_project", "Project"]},
        "kind_index": {"function": ["open_project"], "dataclass": ["Project"]},
        "rows": [
            _api_symbol_row(),
            _api_symbol_row(
                symbol="Project",
                kind="dataclass",
                import_path="paradev.sdk.Project",
                returns="Project class",
            ),
        ],
    }


def test_api_standard_indexes_define_module_feature_kind_grouping() -> None:
    table = api_standard_table("paradev.sdk.api-table.v1", (_api_symbol_row(),))

    assert API_STANDARD_INDEXES == (
        ("module_index", "module"),
        ("feature_index", "feature"),
        ("kind_index", "kind"),
    )
    assert [spec.index_name for spec in API_STANDARD_INDEXES] == [
        "module_index",
        "feature_index",
        "kind_index",
    ]
    assert [spec.field for spec in API_STANDARD_INDEXES] == ["module", "feature", "kind"]
    assert api_table_index_names(table) == [spec.index_name for spec in API_STANDARD_INDEXES]


def test_api_standard_table_rejects_scalar_rows() -> None:
    with pytest.raises(TypeError, match="API table rows must be a list-like value, not str"):
        api_standard_table("paradev.sdk.api-table.v1", "open_project")


def test_api_standard_table_rejects_mapping_rows() -> None:
    with pytest.raises(TypeError, match="API table rows must be a list-like value, not dict"):
        api_standard_table("paradev.sdk.api-table.v1", {"symbol": "open_project"})


def test_api_standard_table_rejects_non_mapping_row() -> None:
    with pytest.raises(TypeError, match="API table row must be a mapping value, not str"):
        api_standard_table("paradev.sdk.api-table.v1", ("open_project",))


def test_api_standard_table_rejects_non_string_row_keys() -> None:
    rows = (_api_symbol_row(),)
    rows[0][42] = "extra"

    with pytest.raises(TypeError, match="API table row keys must be string values, not int"):
        api_standard_table("paradev.sdk.api-table.v1", rows)


def test_api_standard_table_requires_doc_page_and_test_anchor_fields() -> None:
    row = _api_symbol_row()

    for field in ("doc_page", "test_anchor"):
        missing_row = dict(row)
        missing_row.pop(field)
        with pytest.raises(KeyError, match=f"API table row missing field {field!r}"):
            api_standard_table("paradev.sdk.api-table.v1", (missing_row,))


def test_api_standard_table_rejects_non_string_schema() -> None:
    rows = (_api_symbol_row(),)

    with pytest.raises(TypeError, match="API table schema must be a string value, not int"):
        api_standard_table(42, rows)


def test_api_indexed_table_returns_named_indexes_and_copied_rows() -> None:
    rows = [
        {
            "id": "project-api",
            "feature": "projects",
            "adapter": "",
            "surfaces": ["sdk", "docs"],
            "tags": ["Project.load"],
        },
        {
            "id": "cli-api",
            "feature": "cli",
            "adapter": "render_cli",
            "surfaces": ["cli", "docs"],
            "tags": ["paradev projects"],
        },
    ]

    table = api_indexed_table(
        "paradev.test.api-table.v1",
        rows,
        (
            ("feature_index", "feature"),
            ("adapter_index", "adapter"),
            ("surface_index", "surfaces"),
        ),
        value_field="id",
        index_list_fields=("surfaces",),
        index_skip_empty_fields=("adapter",),
        row_list_fields=("surfaces", "tags"),
    )
    rows[0]["surfaces"].append("mutated")
    rows[0]["tags"].append("mutated")

    assert list(table) == ["schema", "row_count", "feature_index", "adapter_index", "surface_index", "rows"]
    assert table == {
        "schema": "paradev.test.api-table.v1",
        "row_count": 2,
        "feature_index": {"projects": ["project-api"], "cli": ["cli-api"]},
        "adapter_index": {"render_cli": ["cli-api"]},
        "surface_index": {"sdk": ["project-api"], "docs": ["project-api", "cli-api"], "cli": ["cli-api"]},
        "rows": [
            {
                "id": "project-api",
                "feature": "projects",
                "adapter": "",
                "surfaces": ["sdk", "docs"],
                "tags": ["Project.load"],
            },
            {
                "id": "cli-api",
                "feature": "cli",
                "adapter": "render_cli",
                "surfaces": ["cli", "docs"],
                "tags": ["paradev projects"],
            },
        ],
    }


def test_api_indexed_table_accepts_named_index_specs() -> None:
    rows = [{"id": "project-api", "feature": "projects", "surface": "sdk"}]
    spec = ApiIndexSpec("feature_index", "feature")

    table = api_indexed_table(
        "paradev.test.api-table.v1",
        rows,
        (spec, ApiIndexSpec("surface_index", "surface")),
        value_field="id",
    )

    assert spec.index_name == "feature_index"
    assert spec.field == "feature"
    assert list(table) == ["schema", "row_count", "feature_index", "surface_index", "rows"]
    assert table["feature_index"] == {"projects": ["project-api"]}
    assert table["surface_index"] == {"sdk": ["project-api"]}


def test_api_indexed_table_rejects_duplicate_index_names() -> None:
    rows = [{"id": "project-api", "feature": "projects", "kind": "table"}]

    with pytest.raises(ValueError, match="duplicate API table index 'feature_index'"):
        api_indexed_table(
            "paradev.test.api-table.v1",
            rows,
            (
                ("feature_index", "feature"),
                ("feature_index", "kind"),
            ),
            value_field="id",
        )


def test_api_indexed_table_rejects_reserved_index_names() -> None:
    rows = [{"id": "project-api", "feature": "projects"}]

    for index_name in ("schema", "row_count", "rows"):
        with pytest.raises(ValueError, match=f"API table index {index_name!r} is reserved"):
            api_indexed_table(
                "paradev.test.api-table.v1",
                rows,
                ((index_name, "feature"),),
                value_field="id",
            )


def test_api_indexed_table_rejects_non_mapping_row() -> None:
    with pytest.raises(TypeError, match="API table row must be a mapping value, not str"):
        api_indexed_table(
            "paradev.test.api-table.v1",
            ("project-api",),
            (("feature_index", "feature"),),
            value_field="id",
        )


def test_api_indexed_table_rejects_mapping_rows() -> None:
    with pytest.raises(TypeError, match="API table rows must be a list-like value, not dict"):
        api_indexed_table(
            "paradev.test.api-table.v1",
            {"id": "project-api", "feature": "projects"},
            (("feature_index", "feature"),),
            value_field="id",
        )


def test_api_indexed_table_rejects_non_string_schema() -> None:
    rows = [{"id": "project-api", "feature": "projects"}]

    with pytest.raises(TypeError, match="API table schema must be a string value, not int"):
        api_indexed_table(42, rows, (("feature_index", "feature"),), value_field="id")


def test_api_indexed_table_rejects_scalar_indexes() -> None:
    rows = [{"id": "project-api", "feature": "projects"}]

    with pytest.raises(TypeError, match="API table indexes must be a list-like value, not str"):
        api_indexed_table("paradev.test.api-table.v1", rows, "feature_index", value_field="id")


def test_api_indexed_table_rejects_mapping_indexes() -> None:
    rows = [{"id": "project-api", "feature": "projects"}]

    with pytest.raises(TypeError, match="API table indexes must be a list-like value, not dict"):
        api_indexed_table(
            "paradev.test.api-table.v1",
            rows,
            {"feature_index": "feature"},
            value_field="id",
        )


def test_api_indexed_table_rejects_scalar_index_spec() -> None:
    rows = [{"id": "project-api", "feature": "projects"}]

    with pytest.raises(TypeError, match="API table index spec must be a list-like value, not str"):
        api_indexed_table("paradev.test.api-table.v1", rows, ("feature_index",), value_field="id")


def test_api_indexed_table_rejects_mapping_index_spec() -> None:
    rows = [{"id": "project-api", "feature": "projects"}]

    with pytest.raises(TypeError, match="API table index spec must be a list-like value, not dict"):
        api_indexed_table(
            "paradev.test.api-table.v1",
            rows,
            ({"feature_index": "feature"},),
            value_field="id",
        )


def test_api_indexed_table_rejects_non_string_index_spec_entries() -> None:
    rows = [{"id": "project-api", "feature": "projects"}]

    with pytest.raises(TypeError, match="API table index spec must contain string values, not int"):
        api_indexed_table("paradev.test.api-table.v1", rows, ((42, "feature"),), value_field="id")


def test_api_indexed_table_rejects_wrong_length_index_spec() -> None:
    rows = [{"id": "project-api", "feature": "projects"}]

    with pytest.raises(ValueError, match="API table index spec must contain 2 values, not 3"):
        api_indexed_table(
            "paradev.test.api-table.v1",
            rows,
            (("feature_index", "feature", "extra"),),
            value_field="id",
        )


def test_api_annotation_text_returns_stable_labels_for_annotations() -> None:
    class CustomType:
        pass

    class CollectionsText:
        def __str__(self) -> str:
            return "collections.abc.Mapping[str, object]"

    assert api_annotation_text(inspect.Signature.empty) == ""
    assert api_annotation_text("'Project'") == "'Project'"
    assert api_annotation_text("'Project'", strip_string_quotes=True) == "Project"
    assert api_annotation_text(None) == "None"
    assert api_annotation_text(CustomType) == "CustomType"
    assert api_annotation_text(str, prefer_builtins_qualname=True, use_name=False) == "str"
    assert api_annotation_text(CustomType, use_name=False).endswith(".CustomType'>")
    assert api_annotation_text(CollectionsText(), drop_collections_abc=True) == "Mapping[str, object]"


def _api_symbol_row(**overrides: str) -> dict[str, str]:
    row = {
        "symbol": "open_project",
        "kind": "function",
        "layer": "sdk",
        "module": "sdk.project",
        "feature": "projects",
        "import_path": "paradev.sdk.open_project",
        "returns": "Project",
        "value": "",
        "registry_seam": "Project.load",
        "surface": "sdk",
        "doc_page": "docs/user-manual/project-api-reference.md",
        "test_anchor": "tests/test_architecture.py::test_sdk_api_table_lists_facade_exports",
    }
    row.update(overrides)
    return row


def test_api_symbol_table_header_returns_standard_columns() -> None:
    assert api_symbol_table_header() == [
        "| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]


def test_table_header_returns_safe_header_and_separator_rows() -> None:
    assert table_header(["Feature | unsafe", "Count", "Values"]) == [
        "| Feature \\| unsafe | Count | Values |",
        "| --- | --- | --- |",
    ]


def test_table_row_rejects_scalar_cells() -> None:
    with pytest.raises(TypeError, match="API Markdown table cells must be a list-like value, not str"):
        table_row("Symbol")


def test_table_row_rejects_non_string_cell() -> None:
    with pytest.raises(TypeError, match="API Markdown table cell must be a string value, not int"):
        table_row(["Symbol", 42])


def test_table_rows_returns_rendered_rows() -> None:
    assert table_rows((("`project.open`", "`Project.load`"), ("`project.view`", "`Project.view`"))) == [
        "| `project.open` | `Project.load` |",
        "| `project.view` | `Project.view` |",
    ]


def test_table_rows_rejects_scalar_cell_rows() -> None:
    with pytest.raises(TypeError, match="API Markdown table cell rows must be a list-like value, not str"):
        table_rows("`project.open`")


def test_table_rows_rejects_scalar_cell_row() -> None:
    with pytest.raises(TypeError, match="API Markdown table cells must be a list-like value, not str"):
        table_rows(("`project.open`",))


def test_table_header_rejects_scalar_labels() -> None:
    with pytest.raises(TypeError, match="API Markdown table labels must be a list-like value, not str"):
        table_header("Symbol")


def test_api_table_lines_returns_header_and_rows() -> None:
    assert api_table_lines(
        ("Feature | unsafe", "Count"),
        [
            "| `modules` | 13 |",
            "| `projects` | 9 |",
        ],
    ) == [
        "| Feature \\| unsafe | Count |",
        "| --- | --- |",
        "| `modules` | 13 |",
        "| `projects` | 9 |",
    ]


def test_api_table_lines_rejects_scalar_rows() -> None:
    with pytest.raises(TypeError, match="API Markdown table rows must be a list-like value, not str"):
        api_table_lines(("Feature",), "| `projects` |")


def test_api_table_lines_rejects_non_string_row() -> None:
    with pytest.raises(TypeError, match="API Markdown table row must be a string value, not int"):
        api_table_lines(("Feature",), [42])


def test_api_table_section_returns_custom_table_section() -> None:
    assert api_table_section(
        "Index Catalog / Index 目录",
        ("Index", "Contract Path", "Use"),
        [
            '| `kind` | `contract["index"]["kind"]` | Lookup inspection row. |',
        ],
    ) == [
        "## Index Catalog / Index 目录",
        "",
        "| Index | Contract Path | Use |",
        "| --- | --- | --- |",
        '| `kind` | `contract["index"]["kind"]` | Lookup inspection row. |',
    ]

    assert api_table_section(
        "Group Index / Group 索引",
        ("Group", "Operations"),
        ["| `project` | 4 |"],
        level=3,
        body=("Rows group canonical operation ids by SDK-owned operation group.",),
    ) == [
        "### Group Index / Group 索引",
        "",
        "Rows group canonical operation ids by SDK-owned operation group.",
        "",
        "| Group | Operations |",
        "| --- | --- |",
        "| `project` | 4 |",
    ]


def test_api_table_section_rejects_non_string_title() -> None:
    with pytest.raises(TypeError, match="API Markdown section title must be a string value, not int"):
        api_table_section(
            42,
            ("Group", "Operations"),
            ["| `project` | 4 |"],
        )


def test_api_table_section_rejects_non_integer_level() -> None:
    with pytest.raises(TypeError, match="API Markdown section level must be an integer value, not str"):
        api_table_section(
            "Group Index / Group 索引",
            ("Group", "Operations"),
            ["| `project` | 4 |"],
            level="3",
        )


def test_api_table_section_rejects_zero_level() -> None:
    with pytest.raises(ValueError, match="API Markdown section level must be at least 1, not 0"):
        api_table_section(
            "Group Index / Group 索引",
            ("Group", "Operations"),
            ["| `project` | 4 |"],
            level=0,
        )


def test_api_table_section_rejects_scalar_body_lines() -> None:
    with pytest.raises(TypeError, match="API Markdown section body lines must be a list-like value, not str"):
        api_table_section(
            "Group Index / Group 索引",
            ("Group", "Operations"),
            ["| `project` | 4 |"],
            body="Rows group canonical operation ids by SDK-owned operation group.",
        )


def test_api_table_section_rejects_non_string_body_lines() -> None:
    with pytest.raises(TypeError, match="API Markdown section body line must be a string value, not int"):
        api_table_section(
            "Group Index / Group 索引",
            ("Group", "Operations"),
            ["| `project` | 4 |"],
            body=(42,),
        )


def test_api_section_lines_returns_blank_line_between_sections() -> None:
    assert api_section_lines(
        (
            ["## Summary", "", "- Rows: 2"],
            ["## API Table", "", "| Symbol |", "| --- |", "| `open_project` |"],
        )
    ) == [
        "## Summary",
        "",
        "- Rows: 2",
        "",
        "## API Table",
        "",
        "| Symbol |",
        "| --- |",
        "| `open_project` |",
    ]


def test_api_section_lines_rejects_scalar_sections() -> None:
    with pytest.raises(TypeError, match="API Markdown sections must be a list-like value, not str"):
        api_section_lines("Summary")


def test_api_section_lines_rejects_scalar_section_lines() -> None:
    with pytest.raises(TypeError, match="API Markdown section lines must be a list-like value, not str"):
        api_section_lines(("Summary",))


def test_api_section_lines_rejects_non_string_section_line() -> None:
    with pytest.raises(TypeError, match="API Markdown section line must be a string value, not int"):
        api_section_lines((["## Summary", 42],))


def test_api_field_label_returns_known_and_fallback_labels() -> None:
    assert api_field_label("frontend_operation_ids") == "Frontend Operation IDs"
    assert api_field_label("sdk_method") == "SDK Method"
    assert api_field_label("row_count") == "Rows"
    assert api_field_label("custom_field") == "Custom Field"


def test_api_field_label_rejects_non_string_field() -> None:
    with pytest.raises(TypeError, match="API Markdown field must be a string value, not int"):
        api_field_label(42)


def test_api_field_table_header_returns_labels_from_fields() -> None:
    assert api_field_table_header(["symbol", "frontend_operation_ids", "row_count"]) == [
        "| Symbol | Frontend Operation IDs | Rows |",
        "| --- | --- | --- |",
    ]


def test_api_field_table_header_rejects_scalar_fields() -> None:
    with pytest.raises(TypeError, match="API Markdown table fields must be a list-like value, not str"):
        api_field_table_header("symbol")


def test_api_field_table_header_rejects_non_string_field() -> None:
    with pytest.raises(TypeError, match="API Markdown table field must be a string value, not int"):
        api_field_table_header([42])


def test_api_field_table_rows_render_selected_field_kinds() -> None:
    rows = [
        {
            "symbol": "open_project",
            "operations": ["project.open", "project.view"],
            "title": "Project | Reference",
            "row_count": 7,
        }
    ]

    assert api_field_table_rows(
        rows,
        ["symbol", "operations", "title", "row_count"],
        list_fields=("operations",),
        markdown_fields=("title", "row_count"),
    ) == [
        "| `open_project` | `project.open`, `project.view` | Project \\| Reference | 7 |",
    ]


def test_api_field_table_rows_reject_scalar_rows() -> None:
    with pytest.raises(TypeError, match="API Markdown rows must be a list-like value, not str"):
        api_field_table_rows("open_project", ["symbol"])


def test_api_field_table_rows_reject_non_mapping_row() -> None:
    with pytest.raises(TypeError, match="API Markdown row must be a mapping value, not str"):
        api_field_table_rows(("open_project",), ["symbol"])


def test_api_field_table_rows_reject_non_string_row_keys() -> None:
    with pytest.raises(TypeError, match="API Markdown row keys must be string values, not int"):
        api_field_table_rows(({42: "open_project"},), ["symbol"])


def test_api_field_table_rows_reject_scalar_fields() -> None:
    rows = [{"symbol": "open_project"}]

    with pytest.raises(TypeError, match="API Markdown table fields must be a list-like value, not str"):
        api_field_table_rows(rows, "symbol")


def test_api_field_table_rows_reject_non_string_field() -> None:
    rows = [{"symbol": "open_project"}]

    with pytest.raises(TypeError, match="API Markdown table field must be a string value, not int"):
        api_field_table_rows(rows, [42])


def test_api_field_table_rows_reject_missing_field() -> None:
    rows = [{"symbol": "open_project"}]

    with pytest.raises(KeyError, match="API Markdown row missing field 'returns'"):
        api_field_table_rows(rows, ["symbol", "returns"])


def test_api_field_table_rows_reject_scalar_list_fields() -> None:
    rows = [{"symbol": "open_project", "operations": ["project.open"]}]

    with pytest.raises(TypeError, match="API Markdown list fields must be a list-like value, not str"):
        api_field_table_rows(rows, ["symbol", "operations"], list_fields="operations")


def test_api_field_table_rows_reject_non_string_list_field() -> None:
    rows = [{"symbol": "open_project", "operations": ["project.open"]}]

    with pytest.raises(TypeError, match="API Markdown list field must be a string value, not int"):
        api_field_table_rows(rows, ["symbol", "operations"], list_fields=[42])


def test_api_field_table_rows_reject_scalar_markdown_fields() -> None:
    rows = [{"symbol": "open_project", "title": "Project Reference"}]

    with pytest.raises(TypeError, match="API Markdown plain-value fields must be a list-like value, not str"):
        api_field_table_rows(rows, ["symbol", "title"], markdown_fields="title")


def test_api_field_table_rows_reject_non_string_markdown_field() -> None:
    rows = [{"symbol": "open_project", "title": "Project Reference"}]

    with pytest.raises(TypeError, match="API Markdown plain-value field must be a string value, not int"):
        api_field_table_rows(rows, ["symbol", "title"], markdown_fields=[42])


def test_api_field_table_rows_reject_scalar_list_field_values() -> None:
    rows = [{"symbol": "open_project", "operations": "project.open"}]

    with pytest.raises(TypeError, match="API Markdown field 'operations' must be a list-like value, not str"):
        api_field_table_rows(rows, ["symbol", "operations"], list_fields=("operations",))


def test_api_field_table_rows_reject_mapping_list_field_values() -> None:
    rows = [{"symbol": "open_project", "operations": {"project.open": True}}]

    with pytest.raises(TypeError, match="API Markdown field 'operations' must be a list-like value, not dict"):
        api_field_table_rows(rows, ["symbol", "operations"], list_fields=("operations",))


def test_api_field_table_rows_reject_non_string_list_field_values() -> None:
    rows = [{"symbol": "open_project", "operations": ["project.open", 42]}]

    with pytest.raises(TypeError, match="API Markdown field 'operations' value must be a string value, not int"):
        api_field_table_rows(rows, ["symbol", "operations"], list_fields=("operations",))


def test_code_list_cell_rejects_scalar_values() -> None:
    with pytest.raises(TypeError, match="API Markdown code-list values must be a list-like value, not str"):
        code_list_cell("project.open")


def test_code_list_cell_rejects_mapping_values() -> None:
    with pytest.raises(TypeError, match="API Markdown code-list values must be a list-like value, not dict"):
        code_list_cell({"project.open": True})


def test_code_list_cell_rejects_non_string_values() -> None:
    with pytest.raises(TypeError, match="API Markdown code-list value must be a string value, not int"):
        code_list_cell(["project.open", 42])


def test_api_field_table_section_returns_title_header_and_rows() -> None:
    rows = [
        {
            "symbol": "Project.load",
            "operations": ["project.open", "project.view"],
            "title": "Project | Reference",
            "row_count": 7,
        }
    ]

    assert api_field_table_section(
        "Project API Table / Project API 表",
        rows,
        ["symbol", "operations", "title", "row_count"],
        list_fields=("operations",),
        markdown_fields=("title", "row_count"),
    ) == [
        "## Project API Table / Project API 表",
        "",
        "| Symbol | Operations | Title | Rows |",
        "| --- | --- | --- | --- |",
        "| `Project.load` | `project.open`, `project.view` | Project \\| Reference | 7 |",
    ]


def test_api_symbol_table_rows_return_standard_rows() -> None:
    rows = [
        {
            "symbol": "open_project",
            "kind": "function",
            "layer": "sdk",
            "module": "paradev.sdk",
            "feature": "projects",
            "import_path": "paradev.sdk.open_project",
            "returns": "Project",
            "value": "callable",
            "registry_seam": "Project.load",
            "surface": "sdk",
            "doc_page": "docs/user-manual/sdk-api-reference.md",
            "test_anchor": "tests/test_architecture.py::test_sdk_api_table_lists_facade_exports",
        }
    ]

    assert api_symbol_table_rows(rows) == [
        "| `open_project` | `function` | `sdk` | `paradev.sdk` | `projects` | `paradev.sdk.open_project` | `Project` | `callable` | `Project.load` | `sdk` | `docs/user-manual/sdk-api-reference.md` | `tests/test_architecture.py::test_sdk_api_table_lists_facade_exports` |"
    ]
    assert api_symbol_table_row(rows[0]) == api_symbol_table_rows(rows)[0]
    assert api_symbol_markdown_value_table_rows(rows) == [
        "| `open_project` | `function` | `sdk` | `paradev.sdk` | `projects` | `paradev.sdk.open_project` | `Project` | callable | `Project.load` | `sdk` | `docs/user-manual/sdk-api-reference.md` | `tests/test_architecture.py::test_sdk_api_table_lists_facade_exports` |"
    ]
    assert api_symbol_markdown_value_table_row(rows[0]) == api_symbol_markdown_value_table_rows(rows)[0]
    assert api_standard_table_section(rows) == [
        "## API Standard Table / API 标准表",
        "",
        "| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        "| `open_project` | `function` | `sdk` | `paradev.sdk` | `projects` | `paradev.sdk.open_project` | `Project` | `callable` | `Project.load` | `sdk` | `docs/user-manual/sdk-api-reference.md` | `tests/test_architecture.py::test_sdk_api_table_lists_facade_exports` |",
    ]
    assert api_standard_table_section(rows, markdown_value=True) == [
        "## API Standard Table / API 标准表",
        "",
        "| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        "| `open_project` | `function` | `sdk` | `paradev.sdk` | `projects` | `paradev.sdk.open_project` | `Project` | callable | `Project.load` | `sdk` | `docs/user-manual/sdk-api-reference.md` | `tests/test_architecture.py::test_sdk_api_table_lists_facade_exports` |",
    ]


def test_api_index_table_header_returns_standard_columns() -> None:
    assert api_index_table_header("Module") == [
        "| Module | Symbols | Public Exports |",
        "| --- | --- | --- |",
    ]
    assert api_index_table_header("Feature | unsafe") == [
        "| Feature \\| unsafe | Symbols | Public Exports |",
        "| --- | --- | --- |",
    ]
    assert api_index_table_header("Kind", count_label="Commands | Routes", values_label="Symbols") == [
        "| Kind | Commands \\| Routes | Symbols |",
        "| --- | --- | --- |",
    ]


def test_api_index_table_header_rejects_non_string_label() -> None:
    with pytest.raises(TypeError, match="API Markdown index label must be a string value, not int"):
        api_index_table_header(42)


def test_api_index_table_header_rejects_non_string_count_label() -> None:
    with pytest.raises(TypeError, match="API Markdown index count label must be a string value, not int"):
        api_index_table_header("Kind", count_label=42)


def test_api_index_table_header_rejects_non_string_values_label() -> None:
    with pytest.raises(TypeError, match="API Markdown index values label must be a string value, not int"):
        api_index_table_header("Kind", values_label=42)


def test_api_index_section_returns_titled_header_and_rows() -> None:
    assert api_index_section(
        "Feature Index / Feature 索引",
        {"projects": ["Project.load", "Project.save"], "build": ["Project.build"]},
        "Feature",
        count_label="Project APIs",
        values_label="Symbols",
    ) == [
        "## Feature Index / Feature 索引",
        "",
        "| Feature | Project APIs | Symbols |",
        "| --- | --- | --- |",
        "| `projects` | 2 | `Project.load`, `Project.save` |",
        "| `build` | 1 | `Project.build` |",
    ]


def test_api_index_section_rejects_scalar_index() -> None:
    with pytest.raises(TypeError, match="API Markdown index 'Feature Index / Feature 索引' must be a mapping value, not str"):
        api_index_section("Feature Index / Feature 索引", "Project.load", "Feature")


def test_api_index_section_rejects_non_string_label() -> None:
    with pytest.raises(TypeError, match="API Markdown index label must be a string value, not int"):
        api_index_section("Feature Index / Feature 索引", {"projects": ["Project.load"]}, 42)


def test_api_index_section_rejects_non_string_count_label() -> None:
    with pytest.raises(TypeError, match="API Markdown index count label must be a string value, not int"):
        api_index_section(
            "Feature Index / Feature 索引",
            {"projects": ["Project.load"]},
            "Feature",
            count_label=42,
        )


def test_api_index_section_rejects_non_string_values_label() -> None:
    with pytest.raises(TypeError, match="API Markdown index values label must be a string value, not int"):
        api_index_section(
            "Feature Index / Feature 索引",
            {"projects": ["Project.load"]},
            "Feature",
            values_label=42,
        )


def test_index_row_rejects_scalar_index_values() -> None:
    with pytest.raises(TypeError, match="API Markdown index values for 'projects' must be a list-like value, not str"):
        index_row("projects", "Project.load")


def test_index_row_rejects_mapping_index_values() -> None:
    with pytest.raises(TypeError, match="API Markdown index values for 'projects' must be a list-like value, not dict"):
        index_row("projects", {"Project.load": True})


def test_index_row_rejects_non_string_index_key() -> None:
    with pytest.raises(TypeError, match="API Markdown index key must be a string value, not int"):
        index_row(42, ["Project.load"])


def test_index_row_rejects_non_string_index_values() -> None:
    with pytest.raises(TypeError, match="API Markdown index value for 'projects' must be a string value, not int"):
        index_row("projects", ["Project.load", 42])


def test_index_rows_returns_standard_index_rows() -> None:
    assert index_rows({"projects": ["Project.load"], "build": ["Project.build", "Project.emit"]}) == [
        "| `projects` | 1 | `Project.load` |",
        "| `build` | 2 | `Project.build`, `Project.emit` |",
    ]


def test_index_rows_rejects_scalar_index() -> None:
    with pytest.raises(TypeError, match="API Markdown index rows must be a mapping value, not str"):
        index_rows("Project.load")


def test_api_index_sections_returns_named_table_indexes() -> None:
    table = {
        "feature_index": {"projects": ["Project.load"]},
        "kind_index": {"method": ["Project.load"]},
    }

    assert api_index_sections(
        table,
        (
            ("Feature Index / Feature 索引", "feature_index", "Feature", "Symbols", "Project APIs"),
            ("Kind Index / 行类型索引", "kind_index", "Kind", "Symbols", "Project APIs"),
        ),
    ) == [
        [
            "## Feature Index / Feature 索引",
            "",
            "| Feature | Symbols | Project APIs |",
            "| --- | --- | --- |",
            "| `projects` | 1 | `Project.load` |",
        ],
        [
            "## Kind Index / 行类型索引",
            "",
            "| Kind | Symbols | Project APIs |",
            "| --- | --- | --- |",
            "| `method` | 1 | `Project.load` |",
        ],
    ]


def test_api_index_sections_accepts_named_section_specs() -> None:
    table = {"feature_index": {"projects": ["Project.load"]}}
    spec = ApiIndexSectionSpec(
        "Feature Index / Feature 索引",
        "feature_index",
        "Feature",
        "Symbols",
        "Project APIs",
    )

    assert spec.index_name == "feature_index"
    assert api_index_sections(table, (spec,)) == [
        [
            "## Feature Index / Feature 索引",
            "",
            "| Feature | Symbols | Project APIs |",
            "| --- | --- | --- |",
            "| `projects` | 1 | `Project.load` |",
        ],
    ]


def test_api_index_sections_rejects_scalar_table_index() -> None:
    table = {"feature_index": "Project.load"}

    with pytest.raises(TypeError, match="API Markdown index 'feature_index' must be a mapping value, not str"):
        api_index_sections(
            table,
            (("Feature Index / Feature 索引", "feature_index", "Feature", "Symbols", "Project APIs"),),
        )


def test_api_index_sections_rejects_missing_table_index() -> None:
    table: dict[str, object] = {}

    with pytest.raises(KeyError, match="API Markdown table missing field 'feature_index'"):
        api_index_sections(
            table,
            (("Feature Index / Feature 索引", "feature_index", "Feature", "Symbols", "Project APIs"),),
        )


def test_api_index_sections_rejects_scalar_table() -> None:
    with pytest.raises(TypeError, match="API Markdown table must be a mapping value, not str"):
        api_index_sections(
            "feature_index",
            (("Feature Index / Feature 索引", "feature_index", "Feature", "Symbols", "Project APIs"),),
        )


def test_api_index_sections_rejects_non_string_table_keys() -> None:
    table: dict[object, object] = {42: {"projects": ["Project.load"]}}

    with pytest.raises(TypeError, match="API Markdown table keys must be string values, not int"):
        api_index_sections(
            table,
            (("Feature Index / Feature 索引", "feature_index", "Feature", "Symbols", "Project APIs"),),
        )


def test_api_index_sections_rejects_scalar_specs() -> None:
    table = {"feature_index": {"projects": ["Project.load"]}}

    with pytest.raises(TypeError, match="API Markdown index section specs must be a list-like value, not str"):
        api_index_sections(table, "feature_index")


def test_api_index_sections_rejects_scalar_spec() -> None:
    table = {"feature_index": {"projects": ["Project.load"]}}

    with pytest.raises(TypeError, match="API Markdown index section spec must be a list-like value, not str"):
        api_index_sections(table, ("Feature Index / Feature 索引",))


def test_api_index_sections_rejects_wrong_length_spec() -> None:
    table = {"feature_index": {"projects": ["Project.load"]}}

    with pytest.raises(ValueError, match="API Markdown index section spec must contain 5 values, not 4"):
        api_index_sections(
            table,
            (("Feature Index / Feature 索引", "feature_index", "Feature", "Symbols"),),
        )


def test_api_index_sections_rejects_non_string_spec_entries() -> None:
    table = {"feature_index": {"projects": ["Project.load"]}}

    with pytest.raises(TypeError, match="API Markdown index section spec must contain string values, not int"):
        api_index_sections(
            table,
            (("Feature Index / Feature 索引", "feature_index", "Feature", "Symbols", 42),),
        )


def test_api_indexed_reference_sections_returns_summary_indexes_and_table() -> None:
    table = {
        "feature_index": {"projects": ["Project.load"]},
        "rows": [
            {
                "symbol": "Project.load",
                "feature": "projects",
                "frontend_operation_ids": ["project.open"],
            }
        ],
    }

    assert api_indexed_reference_sections(
        summary_lines=("- API rows / API 行数: 1", "- Features / Feature 数: 1"),
        table=table,
        index_specs=(("Feature Index / Feature 索引", "feature_index", "Feature", "Symbols", "Project APIs"),),
        fields=("symbol", "feature", "frontend_operation_ids"),
        list_fields=("frontend_operation_ids",),
    ) == [
        [
            "## Summary / 汇总",
            "",
            "- API rows / API 行数: 1",
            "- Features / Feature 数: 1",
        ],
        [
            "## Feature Index / Feature 索引",
            "",
            "| Feature | Symbols | Project APIs |",
            "| --- | --- | --- |",
            "| `projects` | 1 | `Project.load` |",
        ],
        [
            "## API Standard Table / API 标准表",
            "",
            "| Symbol | Feature | Frontend Operation IDs |",
            "| --- | --- | --- |",
            "| `Project.load` | `projects` | `project.open` |",
        ],
    ]


def test_api_indexed_reference_sections_rejects_missing_rows() -> None:
    table = {"feature_index": {"projects": ["Project.load"]}}

    with pytest.raises(KeyError, match="API Markdown table missing field 'rows'"):
        api_indexed_reference_sections(
            summary_lines=("- API rows / API 行数: 1",),
            table=table,
            index_specs=(("Feature Index / Feature 索引", "feature_index", "Feature", "Symbols", "Project APIs"),),
            fields=("symbol", "feature"),
        )


def test_api_summary_lines_returns_standard_counts() -> None:
    table = {
        "row_count": 7,
        "module_index": {"paradev": ["A", "B"], "paradev.sdk": ["C"]},
        "feature_index": {"project": ["A"], "build": ["B"], "docs": ["C"]},
        "kind_index": {"function": ["A", "B", "C"]},
    }

    assert api_summary_lines(table, module_label="SDK") == [
        "- API rows / API 行数: 7",
        "- SDK modules / SDK 模块数: 2",
        "- Features / Feature 数: 3",
        "- Row kinds / 行类型数: 1",
    ]


def test_api_summary_lines_follow_standard_index_contract() -> None:
    table: dict[str, object] = {"row_count": 3}
    for count, spec in enumerate(API_STANDARD_INDEXES, start=1):
        table[spec.index_name] = {f"{spec.field}-{offset}": [spec.field] for offset in range(count)}

    assert api_summary_lines(table, module_label="SDK") == [
        "- API rows / API 行数: 3",
        "- SDK modules / SDK 模块数: 1",
        "- Features / Feature 数: 2",
        "- Row kinds / 行类型数: 3",
    ]


def test_api_summary_lines_rejects_missing_table_field() -> None:
    table = {
        "module_index": {"paradev": ["A"]},
        "feature_index": {"project": ["A"]},
        "kind_index": {"function": ["A"]},
    }

    with pytest.raises(KeyError, match="API Markdown table missing field 'row_count'"):
        api_summary_lines(table, module_label="SDK")


def test_api_summary_lines_rejects_scalar_table() -> None:
    with pytest.raises(TypeError, match="API Markdown table must be a mapping value, not str"):
        api_summary_lines("sdk", module_label="SDK")


def test_api_summary_lines_rejects_non_string_table_keys() -> None:
    table: dict[object, object] = {
        42: "extra",
        "row_count": 7,
        "module_index": {"paradev": ["A"]},
        "feature_index": {"project": ["A"]},
        "kind_index": {"function": ["A"]},
    }

    with pytest.raises(TypeError, match="API Markdown table keys must be string values, not int"):
        api_summary_lines(table, module_label="SDK")


def test_api_summary_lines_rejects_non_string_module_label() -> None:
    table = {
        "row_count": 7,
        "module_index": {"paradev": ["A"]},
        "feature_index": {"project": ["A"]},
        "kind_index": {"function": ["A"]},
    }

    with pytest.raises(TypeError, match="API Markdown module label must be a string value, not int"):
        api_summary_lines(table, module_label=42)


def test_api_summary_lines_rejects_scalar_index_field() -> None:
    table = {
        "row_count": 7,
        "module_index": "paradev",
        "feature_index": {"project": ["A"]},
        "kind_index": {"function": ["A"]},
    }

    with pytest.raises(TypeError, match="API Markdown index 'module_index' must be a mapping value, not str"):
        api_summary_lines(table, module_label="SDK")


def test_api_summary_section_returns_standard_summary_heading() -> None:
    assert api_summary_section(
        [
            "- API rows / API 行数: 7",
            "- Features / Feature 数: 3",
        ]
    ) == [
        "## Summary / 汇总",
        "",
        "- API rows / API 行数: 7",
        "- Features / Feature 数: 3",
    ]


def test_api_summary_section_rejects_scalar_lines() -> None:
    with pytest.raises(TypeError, match="API Markdown summary lines must be a list-like value, not str"):
        api_summary_section("- API rows / API 行数: 2")


def test_api_summary_section_rejects_non_string_line() -> None:
    with pytest.raises(TypeError, match="API Markdown summary line must be a string value, not int"):
        api_summary_section(("- API rows / API 行数: 2", 42))


def test_api_summary_reference_sections_returns_summary_and_custom_sections() -> None:
    assert api_summary_reference_sections(
        ("- Surfaces / Surface 数: 2",),
        (
            ["## Index Catalog / Index 目录", "", "| Index | Use |", "| --- | --- |"],
            ["## Surface Contracts / Surface Contract 表", "", "| Surface | Status |", "| --- | --- |"],
        ),
    ) == [
        [
            "## Summary / 汇总",
            "",
            "- Surfaces / Surface 数: 2",
        ],
        [
            "## Index Catalog / Index 目录",
            "",
            "| Index | Use |",
            "| --- | --- |",
        ],
        [
            "## Surface Contracts / Surface Contract 表",
            "",
            "| Surface | Status |",
            "| --- | --- |",
        ],
    ]


def test_api_summary_reference_sections_rejects_scalar_sections() -> None:
    with pytest.raises(TypeError, match="API Markdown reference sections must be a list-like value, not str"):
        api_summary_reference_sections(("- API rows / API 行数: 2",), "## Custom")


def test_api_summary_reference_sections_rejects_scalar_section_lines() -> None:
    with pytest.raises(
        TypeError,
        match="API Markdown reference section lines must be a list-like value, not str",
    ):
        api_summary_reference_sections(("- API rows / API 行数: 2",), ("## Custom",))


def test_api_summary_reference_sections_rejects_non_string_section_line() -> None:
    with pytest.raises(
        TypeError,
        match="API Markdown reference section line must be a string value, not int",
    ):
        api_summary_reference_sections(("- API rows / API 行数: 2",), (["## Custom", 42],))


def test_api_regeneration_command_block_returns_fenced_bash_command() -> None:
    assert api_regeneration_command_block("rtk uv run paradev sdk-api --markdown > docs/user-manual/sdk-api-reference.md") == [
        "```bash",
        "rtk uv run paradev sdk-api --markdown > docs/user-manual/sdk-api-reference.md",
        "```",
    ]


def test_api_regeneration_command_block_rejects_non_string_command() -> None:
    with pytest.raises(TypeError, match="API Markdown regeneration command must be a string value, not int"):
        api_regeneration_command_block(42)


def test_api_reference_intro_lines_returns_source_and_regeneration_block() -> None:
    assert api_reference_intro_lines(
        source="paradev.sdk.get_sdk_api_table()",
        regenerate_when="Regenerate this file whenever the public Python SDK facade changes:",
        command="rtk uv run paradev sdk-api --markdown > docs/user-manual/sdk-api-reference.md",
    ) == [
        "Generated from `paradev.sdk.get_sdk_api_table()`.",
        "",
        "Regenerate this file whenever the public Python SDK facade changes:",
        "",
        "```bash",
        "rtk uv run paradev sdk-api --markdown > docs/user-manual/sdk-api-reference.md",
        "```",
    ]


def test_api_reference_intro_lines_rejects_non_string_source() -> None:
    with pytest.raises(TypeError, match="API Markdown reference source must be a string value, not int"):
        api_reference_intro_lines(
            source=42,
            regenerate_when="Regenerate this file whenever the public Python SDK facade changes:",
            command="rtk uv run paradev sdk-api --markdown > docs/user-manual/sdk-api-reference.md",
        )


def test_api_reference_intro_lines_rejects_non_string_regeneration_note() -> None:
    with pytest.raises(TypeError, match="API Markdown regeneration note must be a string value, not int"):
        api_reference_intro_lines(
            source="paradev.sdk.get_sdk_api_table()",
            regenerate_when=42,
            command="rtk uv run paradev sdk-api --markdown > docs/user-manual/sdk-api-reference.md",
        )


def test_api_reference_markdown_returns_title_intro_and_sections() -> None:
    expected = (
        "\n".join(
            [
                "# CLI API Reference",
                "",
                "Generated from `paradev.surfaces.cli.get_cli_api_table()`.",
                "",
                "Regenerate this file whenever the CLI command contract changes:",
                "",
                "```bash",
                "rtk uv run paradev cli-api --markdown > docs/user-manual/cli-api-reference.md",
                "```",
                "",
                "## Summary / 汇总",
                "",
                "- API rows / API 行数: 2",
                "",
                "## Command Table / 命令表",
                "",
                "| Command |",
                "| --- |",
                "| `project open` |",
            ]
        )
        + "\n"
    )

    assert (
        api_reference_markdown(
            title="CLI API Reference",
            source="paradev.surfaces.cli.get_cli_api_table()",
            regenerate_when="Regenerate this file whenever the CLI command contract changes:",
            command="rtk uv run paradev cli-api --markdown > docs/user-manual/cli-api-reference.md",
            sections=(
                ["## Summary / 汇总", "", "- API rows / API 行数: 2"],
                ["## Command Table / 命令表", "", "| Command |", "| --- |", "| `project open` |"],
            ),
        )
        == expected
    )


def test_api_reference_markdown_rejects_non_string_title() -> None:
    with pytest.raises(TypeError, match="API Markdown reference title must be a string value, not int"):
        api_reference_markdown(
            title=42,
            source="paradev.surfaces.cli.get_cli_api_table()",
            regenerate_when="Regenerate this file whenever the CLI command contract changes:",
            command="rtk uv run paradev cli-api --markdown > docs/user-manual/cli-api-reference.md",
            sections=(["## Summary / 汇总", "", "- API rows / API 行数: 2"],),
        )


def test_api_reference_markdown_rejects_scalar_sections() -> None:
    with pytest.raises(TypeError, match="API Markdown reference sections must be a list-like value, not str"):
        api_reference_markdown(
            title="CLI API Reference",
            source="paradev.surfaces.cli.get_cli_api_table()",
            regenerate_when="Regenerate this file whenever the CLI command contract changes:",
            command="rtk uv run paradev cli-api --markdown > docs/user-manual/cli-api-reference.md",
            sections="## Summary / 汇总",
        )


def test_api_reference_markdown_rejects_scalar_section_lines() -> None:
    with pytest.raises(
        TypeError,
        match="API Markdown reference section lines must be a list-like value, not str",
    ):
        api_reference_markdown(
            title="CLI API Reference",
            source="paradev.surfaces.cli.get_cli_api_table()",
            regenerate_when="Regenerate this file whenever the CLI command contract changes:",
            command="rtk uv run paradev cli-api --markdown > docs/user-manual/cli-api-reference.md",
            sections=("## Summary / 汇总",),
        )


def test_api_standard_index_sections_returns_module_feature_kind_sections() -> None:
    table = {
        "module_index": {"paradev": ["open_project", "save_project"]},
        "feature_index": {"project": ["open_project"], "build": ["save_project"]},
        "kind_index": {"function": ["open_project", "save_project"]},
    }

    assert api_standard_index_sections(table) == [
        "## Module Index / 模块索引",
        "",
        "| Module | Symbols | Public Exports |",
        "| --- | --- | --- |",
        "| `paradev` | 2 | `open_project`, `save_project` |",
        "",
        "## Feature Index / Feature 索引",
        "",
        "| Feature | Symbols | Public Exports |",
        "| --- | --- | --- |",
        "| `project` | 1 | `open_project` |",
        "| `build` | 1 | `save_project` |",
        "",
        "## Kind Index / 行类型索引",
        "",
        "| Kind | Symbols | Public Exports |",
        "| --- | --- | --- |",
        "| `function` | 2 | `open_project`, `save_project` |",
    ]


def test_api_standard_index_sections_follow_standard_index_contract() -> None:
    table = {spec.index_name: {f"{spec.field}-key": [spec.field]} for spec in API_STANDARD_INDEXES}

    rows = [line for line in api_standard_index_sections(table) if line.startswith("| `")]

    assert rows == [f"| `{spec.field}-key` | 1 | `{spec.field}` |" for spec in API_STANDARD_INDEXES]


def test_api_standard_overview_sections_returns_summary_and_indexes() -> None:
    table = {
        "row_count": 2,
        "module_index": {"paradev": ["open_project", "save_project"]},
        "feature_index": {"project": ["open_project"], "build": ["save_project"]},
        "kind_index": {"function": ["open_project", "save_project"]},
    }

    assert api_standard_overview_sections(table, module_label="SDK") == [
        "## Summary / 汇总",
        "",
        "- API rows / API 行数: 2",
        "- SDK modules / SDK 模块数: 1",
        "- Features / Feature 数: 2",
        "- Row kinds / 行类型数: 1",
        "",
        "## Module Index / 模块索引",
        "",
        "| Module | Symbols | Public Exports |",
        "| --- | --- | --- |",
        "| `paradev` | 2 | `open_project`, `save_project` |",
        "",
        "## Feature Index / Feature 索引",
        "",
        "| Feature | Symbols | Public Exports |",
        "| --- | --- | --- |",
        "| `project` | 1 | `open_project` |",
        "| `build` | 1 | `save_project` |",
        "",
        "## Kind Index / 行类型索引",
        "",
        "| Kind | Symbols | Public Exports |",
        "| --- | --- | --- |",
        "| `function` | 2 | `open_project`, `save_project` |",
    ]


def test_api_standard_reference_markdown_returns_complete_document() -> None:
    table = {
        "row_count": 1,
        "module_index": {"paradev.sdk": ["open_project"]},
        "feature_index": {"project": ["open_project"]},
        "kind_index": {"function": ["open_project"]},
        "rows": [
            {
                "symbol": "open_project",
                "kind": "function",
                "layer": "sdk",
                "module": "paradev.sdk",
                "feature": "project",
                "import_path": "paradev.sdk.open_project",
                "returns": "Project",
                "value": "callable",
                "registry_seam": "Project.load",
                "surface": "sdk",
                "doc_page": "docs/user-manual/sdk-api-reference.md",
                "test_anchor": "tests/test_architecture.py::test_sdk_api_table_lists_facade_exports",
            }
        ],
    }

    expected = (
        "\n".join(
            [
                "# SDK API Reference",
                "",
                "Generated from `paradev.sdk.get_sdk_api_table()`.",
                "",
                "Regenerate this file whenever the public Python SDK facade changes:",
                "",
                "```bash",
                "rtk uv run paradev sdk-api --markdown > docs/user-manual/sdk-api-reference.md",
                "```",
                "",
                "## Summary / 汇总",
                "",
                "- API rows / API 行数: 1",
                "- SDK modules / SDK 模块数: 1",
                "- Features / Feature 数: 1",
                "- Row kinds / 行类型数: 1",
                "",
                "## Module Index / 模块索引",
                "",
                "| Module | Symbols | Public Exports |",
                "| --- | --- | --- |",
                "| `paradev.sdk` | 1 | `open_project` |",
                "",
                "## Feature Index / Feature 索引",
                "",
                "| Feature | Symbols | Public Exports |",
                "| --- | --- | --- |",
                "| `project` | 1 | `open_project` |",
                "",
                "## Kind Index / 行类型索引",
                "",
                "| Kind | Symbols | Public Exports |",
                "| --- | --- | --- |",
                "| `function` | 1 | `open_project` |",
                "",
                "## API Standard Table / API 标准表",
                "",
                "| Symbol | Kind | Layer | Module | Feature | Import Path | Returns | Value | Registry Seam | Surface | Doc Page | Test Anchor |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
                "| `open_project` | `function` | `sdk` | `paradev.sdk` | `project` | `paradev.sdk.open_project` | `Project` | callable | `Project.load` | `sdk` | `docs/user-manual/sdk-api-reference.md` | `tests/test_architecture.py::test_sdk_api_table_lists_facade_exports` |",
            ]
        )
        + "\n"
    )

    assert (
        api_standard_reference_markdown(
            title="SDK API Reference",
            source="paradev.sdk.get_sdk_api_table()",
            regenerate_when="Regenerate this file whenever the public Python SDK facade changes:",
            command="rtk uv run paradev sdk-api --markdown > docs/user-manual/sdk-api-reference.md",
            table=table,
            module_label="SDK",
            markdown_value=True,
        )
        == expected
    )


def test_api_surface_reference_markdown_returns_feature_and_surface_document() -> None:
    table = {
        "row_count": 1,
        "surface_index": {"sdk": ["parse_pdx_file"]},
        "feature_index": {"parse": ["parse_pdx_file"]},
        "rows": [
            {
                "symbol": "parse_pdx_file",
                "kind": "function",
                "surface": "sdk",
                "feature": "parse",
            }
        ],
    }

    expected = (
        "\n".join(
            [
                "# PDX API Reference",
                "",
                "Generated from `paradev.sdk.get_pdx_api_table()`.",
                "",
                "Regenerate this file whenever the PDX API table changes:",
                "",
                "```bash",
                "rtk uv run paradev pdx-api --markdown > docs/user-manual/pdx-api-reference.md",
                "```",
                "",
                "## Summary / 汇总",
                "",
                "- API rows / API 行数: 1",
                "- Surfaces / Surface 数: 1",
                "- Features / Feature 数: 1",
                "",
                "## Feature Index / Feature 索引",
                "",
                "| Feature | APIs | Symbols |",
                "| --- | --- | --- |",
                "| `parse` | 1 | `parse_pdx_file` |",
                "",
                "## Surface Index / Surface 索引",
                "",
                "| Surface | APIs | Symbols |",
                "| --- | --- | --- |",
                "| `sdk` | 1 | `parse_pdx_file` |",
                "",
                "## API Standard Table / API 标准表",
                "",
                "| Symbol | Kind | Surface | Feature |",
                "| --- | --- | --- | --- |",
                "| `parse_pdx_file` | `function` | `sdk` | `parse` |",
            ]
        )
        + "\n"
    )

    assert (
        api_surface_reference_markdown(
            title="PDX API Reference",
            source="paradev.sdk.get_pdx_api_table()",
            regenerate_when="Regenerate this file whenever the PDX API table changes:",
            command="rtk uv run paradev pdx-api --markdown > docs/user-manual/pdx-api-reference.md",
            table=table,
            fields=("symbol", "kind", "surface", "feature"),
        )
        == expected
    )


def test_api_surface_reference_markdown_can_skip_feature_index() -> None:
    table = {
        "row_count": 1,
        "surface_index": {"sdk": ["get_architecture_spec"]},
        "rows": [
            {
                "symbol": "get_architecture_spec",
                "kind": "function",
                "surface": "sdk",
            }
        ],
    }

    reference = api_surface_reference_markdown(
        title="Architecture API Reference",
        source="paradev.sdk.get_architecture_api_table()",
        regenerate_when="Regenerate this file whenever the architecture graph API table changes:",
        command="rtk uv run paradev architecture --api-table-markdown > docs/user-manual/architecture-api-reference.md",
        table=table,
        fields=("symbol", "kind", "surface"),
        include_feature_index=False,
    )

    assert "- Features / Feature 数:" not in reference
    assert "## Feature Index / Feature 索引" not in reference
    assert "## Surface Index / Surface 索引" in reference
