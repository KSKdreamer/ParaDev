# Desktop Frontend API Endpoints Progress

Date: 2026-06-08 12:30 CST

Linear: TAL-295

## Done

- Added typed desktop helper payloads for frontend API action detail, forms, option payloads, normalized inputs, and REST request plans.
- Added `frontendApiEndpointPaths` plus URL builders for frontend API discovery, selected-action detail, option resolution, input normalization, and REST-request planning endpoints.
- Updated the GUI spec, architecture contract, and English/Chinese user/developer manuals so TypeScript clients use the helper rather than hand-building `operation_id` or `field_name` query strings.

## Verification

- Red check first: `tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_rest_endpoint_helpers` failed before implementation.
- Focused helper checks: `3 passed`.
- Desktop TypeScript build: `rtk npm --prefix apps/desktop run build`.
- Targeted Python checks: `tests/test_architecture.py tests/test_cli.py -q` passed with 69 tests, and `tests/test_sdk_examples.py -q` passed with 20 tests.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py`.
- Formatting/diff checks: `rtk bash scripts/flake.bash --ci` and `rtk git diff --check`.
- Full suite: `rtk bash scripts/test.bash` passed with 490 tests.
- Package build: `rtk uv build`.

## Risks Or Blockers

- Codex app Linear search/fetch remains expired for issue lookup; the alternate Linear connector accepted the TAL-295 progress comment.

## Next

- Continue tightening the GUI-facing TypeScript helper only around SDK-owned metadata and endpoint affordances.
- Avoid adding frontend-only request planning logic; keep normalization, option resolution, and REST request splitting in the Python SDK.
