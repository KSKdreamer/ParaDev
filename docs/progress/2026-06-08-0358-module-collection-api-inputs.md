# Module And Collection Frontend API Inputs

Date: 2026-06-08 03:58 CST

Issues: TAL-299, TAL-295

Linear comments:

- TAL-299: `2893e84e-ea31-445c-a960-a28b7e05602d`
- TAL-295: `47f59710-b1e5-4bf6-a753-f9aae64bda0d`

## Summary

- Added canonical `inputs` metadata to module and collection frontend API rows so GUI, importer, and PIHC3-facing code can build list filters, view actions, file editors, authoring forms, scaffold flows, rename/remove actions, and collection-create flows from the SDK contract.
- Covered module rows for list/view/create/authoring-path/authoring-plan/source-slots/sources/file/edit/rename/remove and collection rows for list/view/authoring-path/authoring-plan/source-slots/file/create/edit.
- Kept safe mutation defaults explicit: `write`, `create`, and `force` default to `false`; required identifiers and body-like fields such as `text`, `values`, and `metadata` are declared directly on the operation row.
- Updated the English and Chinese frontend API manual, SDK manual, developer manual, and architecture interface contract.

## Verification

- Red test: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations -q` failed on missing `module.list["inputs"]`.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations -q` passed.
- Lookup coverage: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_lookup_helpers_return_canonical_rows -q` passed.
- SDK probe: `rtk uv run python - <<'PY' ... get_frontend_api_operation(...) ... PY` confirmed module and collection inputs through the public SDK.
- Docs/source check: `rtk rg -n 'Module and collection rows|module 和 collection 行|module_edit_inputs|collection_create_inputs|Module and collection frontend rows|module\.create.*inputs|collection\.create.*inputs|input_names\("module' src/paradev/sdk/frontend_api.py tests/test_architecture.py docs/user-manual docs/architecture/interfaces.md`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py`
- Formatting: `rtk bash scripts/flake.bash --ci`
- Full tests: `rtk bash scripts/test.bash` (`443 passed`)
- Package build: `rtk uv build`

## Review

- This is contract metadata only; it does not change SDK behavior, CLI command semantics, REST routing, or file mutation paths.
- The operation row remains the maintained frontend source of truth, while inspection filters continue to come from SDK-owned project inspection methods.
- PDX, LSP, build, catalog, and surface rows still need per-operation `inputs` where they represent forms or editor actions; this slice completes the module/collection management area first.
