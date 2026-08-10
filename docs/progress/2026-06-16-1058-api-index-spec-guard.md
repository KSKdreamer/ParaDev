# API Index Spec Guard Progress

Date: 2026-06-16 10:58 CST

Linear: N/A

## Done

- Added a shared internal guard for duplicate generated API table index names.
- Covered the guard in the focused API table helper test suite.
- Preserved valid SDK, CLI, REST, MCP, LSP, frontend, and docs API table behavior while turning invalid duplicate index specs into loud failures.

## Verification

- `rtk uv run black src/paradev/_api_table.py tests/test_api_table.py`
- `rtk uv run python -m py_compile src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/test.bash tests/test_api_table.py -q`
- `rtk bash scripts/test.bash tests/test_architecture.py::test_api_catalog_lists_generated_references -q`
- `rtk bash scripts/test.bash tests/test_cli.py::test_api_catalog_cli_outputs_table_json -q`
- Generated-reference parity over all 29 `API_CATALOG_SOURCE_ROWS`: no content mismatches, no missing pages; 27 existing non-frontend pages remain trailing-newline-only differences.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py tests/test_api_table.py docs/progress/2026-06-16-1058-api-index-spec-guard.md`
- Full suite intentionally deferred to keep CPU free for parallel PIHC3 migration workers.

## Risks Or Blockers

- None known for valid table specs; only invalid duplicate index names change from silent overwrite to `ValueError`.

## Next

- Continue hardening generated API table infrastructure so future public surface additions stay explicit and auditable.
