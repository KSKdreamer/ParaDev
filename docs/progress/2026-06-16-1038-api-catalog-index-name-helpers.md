# API Catalog Index Name Helpers Progress

Date: 2026-06-16 10:38 CST

Linear: N/A

## Done

- Split API catalog index-name derivation into helpers for top-level index fields, flat nested indexes, and nested index names.
- Kept the aggregate API catalog index-name lists, row order, row counts, indexes, and generated Markdown unchanged.
- Preserved the API catalog as the top-level SDK/CLI/REST/MCP/docs reference inventory.

## Verification

- `rtk uv run black src/paradev/surfaces/api_catalog.py`
- `rtk uv run python -m py_compile src/paradev/surfaces/api_catalog.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_table_json -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown -q`
- Generated-reference parity over all 29 `API_CATALOG_SOURCE_ROWS`: no content mismatches, no missing pages; 27 existing non-frontend pages remain trailing-newline-only differences.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/api_catalog.py`
- `rtk git diff --check -- src/paradev/surfaces/api_catalog.py docs/progress/2026-06-16-1038-api-catalog-index-name-helpers.md`
- Full suite intentionally deferred to keep CPU free for parallel PIHC3 migration workers.

## Risks Or Blockers

- None known for this slice; it is intended as a private API catalog refactor only.

## Next

- Continue making generated API catalog behavior explicit and easy to audit while preserving public SDK, CLI, REST, MCP, and documentation surfaces.
