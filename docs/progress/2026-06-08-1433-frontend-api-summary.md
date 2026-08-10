# Frontend API Summary Progress

Date: 2026-06-08 14:33 CST

Linear: TAL-299, TAL-295

## Done

- Added SDK-owned `FRONTEND_API_SUMMARY_SCHEMA` and `get_frontend_api_contract()["summary"]` so the canonical frontend API list now publishes operation, group, status, read/write, and workspace-section counts.
- Added per-group `operation_count` rows to the generated frontend API group metadata.
- Rendered the summary table into `docs/user-manual/frontend-api-reference.md` from `render_frontend_api_reference_markdown()`.
- Regenerated `apps/desktop/src/generated/frontendApi.ts` and made its contract type include `summary`.
- Changed `apps/desktop/src/data/frontendApi.ts` so `frontendApiSummary` points at `PARADEV_FRONTEND_API_CONTRACT.summary` instead of rederiving local counts.
- Updated English/Chinese frontend API, SDK, developer, and architecture manual text to describe the summary as the maintained API audit surface.

## Verification

- Red check first: `tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations` failed before `FRONTEND_API_SUMMARY_SCHEMA` was exported.
- Focused frontend API architecture checks: `rtk bash scripts/test.bash tests/test_architecture.py -q -k "frontend_api"` passed with 28 tests.
- Desktop TypeScript build: `rtk npm --prefix apps/desktop run build`.
- SDK examples: `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 20 tests.
- Architecture and CLI checks: `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q` passed with 76 tests.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py`.
- Formatting/diff checks: `rtk bash scripts/flake.bash --ci` and `rtk git diff --check`.
- CLI probe: `rtk uv run paradev frontend-api --json` returned `paradev.sdk.frontend-api.summary.v1`, 71 operations, and 11 project operations.
- Full suite: `rtk bash scripts/test.bash` passed with 497 tests.
- Package build: `rtk uv build`.

## Risks Or Blockers

- The summary is intentionally count-oriented. It does not replace the full operation table or row-level bindings.
- No new user-facing operation behavior was added in this slice; this is a maintenance and integration surface for the canonical API list.

## Next

- Use the summary as the API audit header for future frontend-visible rows.
- Continue from the generated contract into richer desktop consumption: bind successful option payloads into field controls, then add submitted-value normalization and REST request planning in the shell.
