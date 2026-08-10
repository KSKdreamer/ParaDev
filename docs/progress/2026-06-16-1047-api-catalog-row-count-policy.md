# API Catalog Row Count Policy Progress

Date: 2026-06-16 10:47 CST

Linear: N/A

## Done

- Consolidated API catalog source-specific row-count fallback fields into one private map.
- Added a shared fallback counter that preserves integer payload counts and list-length payload counts.
- Kept public API catalog rows, schemas, indexes, CLI output, and generated Markdown behavior unchanged.

## Verification

- `rtk uv run black src/paradev/surfaces/api_catalog.py`
- `rtk uv run python -m py_compile src/paradev/surfaces/api_catalog.py`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_table_json -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_reference_markdown -q`
- Generated-reference parity over all 29 `API_CATALOG_SOURCE_ROWS`: no content mismatches, no missing pages; 27 existing non-frontend pages remain trailing-newline-only differences.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/api_catalog.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/api_catalog.py`
- `rtk git diff --check -- src/paradev/surfaces/api_catalog.py docs/progress/2026-06-16-1047-api-catalog-row-count-policy.md`
- Full suite intentionally deferred to keep CPU free for parallel PIHC3 migration workers.

## Risks Or Blockers

- None known for this slice; the change is private API catalog plumbing only.

## Next

- Continue reducing manual policy duplication in API reference/catalog helpers while preserving the stable SDK, CLI, REST, MCP, LSP, frontend, and docs surfaces.
