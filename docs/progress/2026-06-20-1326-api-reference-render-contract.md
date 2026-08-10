# API Reference Render Contract

## Summary

- Added a shared contract that every `render_*_api_reference_markdown()` output matches its checked-in `docs/user-manual/*-api-reference.md` page.
- Synced `docs/user-manual/sdk-api-reference.md` with the rendered SDK API table tuple counts.
- Updated the SDK API facade test to the current 128-row surface, including API selection helpers in grouped counts.

## Verification

- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q` failed before the doc sync on `docs/user-manual/sdk-api-reference.md`.
- `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`
- `rtk uv run pytest tests/test_api_table.py tests/test_api_table_contracts.py tests/test_architecture.py::test_sdk_api_table_lists_facade_exports -q`
- `rtk bash scripts/flake.bash --all --paths tests/test_api_table_contracts.py tests/api_table_contract_helpers.py tests/test_architecture.py`
- `rtk git diff --check -- tests/test_api_table_contracts.py tests/api_table_contract_helpers.py tests/test_architecture.py docs/user-manual/sdk-api-reference.md`

## Waiver

- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/test_api_table_contracts.py tests/api_table_contract_helpers.py tests/test_architecture.py` reports pre-existing `json`/`pathlib` imports in `tests/test_architecture.py`. This slice leaves that broad test-file cleanup out of scope and keeps the change focused on API reference synchronization.
