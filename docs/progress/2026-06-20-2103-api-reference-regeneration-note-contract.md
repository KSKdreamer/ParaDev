# API Reference Regeneration Note Contract

## Summary

- Tightened generated API reference markdown checks so each regeneration note must match the renderer's `regenerate_when` metadata.
- Reused the renderer keyword extractor for title metadata and allowed module-level string constants where renderers already use them.
- Added a stale REST regeneration-note regression that changes only the intro note line.
- Runtime behavior is unchanged; this slice only strengthens the generated API documentation contract.

## Verification

- RED: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_regeneration_note -q` failed before the helper change.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_contract_flags_stale_regeneration_note -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py::test_api_reference_markdown_matches_renderers -q`.
- GREEN: `rtk uv run pytest tests/test_api_table_contracts.py tests/test_api_table.py -q` with 244 passed.
- GREEN: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk bash scripts/flake.bash --ci --paths tests/api_table_contract_helpers.py tests/test_api_table_contracts.py`.
- GREEN: `rtk git diff --check`.

## Waiver

- Skipped the full suite in this loop to reduce CPU contention while other workers continue the PIHC migration.
