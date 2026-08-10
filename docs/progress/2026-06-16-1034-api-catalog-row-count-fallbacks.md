# API Catalog Row Count Fallbacks Progress

Date: 2026-06-16 10:34 CST

Linear: N/A

## Done

- Replaced source-specific API catalog row-count branches with named fallback-field maps.
- Split row-count derivation into helpers for direct integer fields, frontend summary operation counts, and source-specific fallback fields.
- Kept the aggregate API catalog payload, row counts, row order, indexes, and generated Markdown unchanged.

## Verification

- `rtk uv run black src/paradev/surfaces/api_catalog.py`
- `rtk uv run python -m py_compile src/paradev/surfaces/api_catalog.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_table_json -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown -q`
- Generated-reference parity over all 29 `API_CATALOG_SOURCE_ROWS`: no content mismatches, no missing pages; 27 existing non-frontend pages remain trailing-newline-only differences.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/api_catalog.py`
- `rtk git diff --check -- src/paradev/surfaces/api_catalog.py docs/progress/2026-06-16-1034-api-catalog-row-count-fallbacks.md`
- Full suite intentionally deferred to keep CPU free for parallel PIHC3 migration workers.

## Risks Or Blockers

- None known for this slice; it is intended as a private API catalog refactor only.

## Next

- Continue making generated API catalog behavior data-driven and explicit while preserving public SDK, CLI, REST, MCP, and documentation surfaces.
