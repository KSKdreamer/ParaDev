# Frontend Form Reference Sections

Date: 2026-06-15 15:35

## Scope

- Continued the generated frontend API reference renderer cleanup in `src/paradev/sdk/frontend_api.py`.
- Routed the workspace-section form, control, option-source, input-target, and validation summary sections through the shared API table-section helper.
- Preserved generated markdown output exactly; no frontend contract rows or docs pages were regenerated.

## Verification

- `rtk uv run black src/paradev/sdk/frontend_api.py`
- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- Catalog-wide generated reference parity:

```bash
rtk uv run python - <<'PY'
from importlib import import_module
from pathlib import Path
from paradev.surfaces.api_catalog import API_CATALOG_SOURCE_ROWS

checked = []
for source in API_CATALOG_SOURCE_ROWS:
    module = import_module(source["owner_module"])
    render = getattr(module, source["markdown_helper"])
    path = Path(source["doc_page"])
    expected = path.read_text(encoding="utf-8").strip()
    actual = render().strip()
    if actual != expected:
        raise SystemExit(f"{source['id']} reference differs: {path}")
    checked.append(source["id"])
print(f"checked {len(checked)} references")
print(", ".join(checked))
PY
```

Result: checked all 29 maintained generated API references against their manual pages.
- `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_reference_manual_matches_sdk_renderer tests/test_architecture.py::test_frontend_api_workspace_projection_groups_gui_actions tests/test_architecture.py::test_frontend_api_form_contract_is_derived_from_operation_inputs tests/test_architecture.py::test_frontend_api_form_fields_expose_sdk_owned_option_sources tests/test_architecture.py::test_frontend_api_form_fields_have_sdk_owned_user_text tests/test_architecture.py::test_api_catalog_lists_generated_references tests/test_cli.py::test_frontend_api_cli_outputs_reference_markdown -q`
  - `7 passed in 1.11s`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/sdk/frontend_api.py`

Full-suite tests were deferred to keep the active loop light while other migration work is running.
