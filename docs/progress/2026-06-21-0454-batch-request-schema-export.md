# Batch Request Schema Export Progress

Date: 2026-06-21 04:54 +0800

Linear: TAL-000

## Done

- Exported `MODULE_BATCH_EDIT_REQUEST_SCHEMA` through the public `paradev.sdk` facade so SDK callers can discover the batch-request schema alongside the request generator.
- Regenerated the SDK and aggregate API catalog references so the public facade table includes `paradev.module.batch_edit_request.v1`.
- Tightened SDK/API catalog tests and CLI JSON checks for the new facade row and schema-constant count.

## Verification

- `rtk uv run pytest tests/test_architecture.py::test_sdk_api_table_lists_facade_exports tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk uv run pytest tests/test_cli.py::test_sdk_api_cli_outputs_table_json tests/test_cli.py::test_sdk_api_cli_outputs_reference_markdown tests/test_cli.py::test_api_catalog_cli_outputs_table_json -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/__init__.py tests/test_architecture.py tests/test_cli.py`
- `rtk git diff --check -- src/paradev/sdk/__init__.py tests/test_architecture.py tests/test_cli.py docs/user-manual/sdk-api-reference.md docs/user-manual/api-catalog-reference.md`

## Risks Or Blockers

- This is an additive SDK facade export; runtime batch-edit behavior is unchanged.

## Next

- Continue using PIHC3 focus modules as the real migration fixture for GUI and batch-update follow-up slices.
