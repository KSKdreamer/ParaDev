# Desktop Frontend API Requests Progress

Date: 2026-06-08 12:45 CST

Linear: TAL-295

## Done

- Added typed desktop helper request payloads: `FrontendApiSubmittedValues` and `FrontendApiJsonRequestInit`.
- Added `buildFrontendApiJsonRequestInit(...)` plus operation-aware JSON POST builders for frontend API option resolution, input normalization, and REST-request planning meta endpoints.
- Updated the GUI spec, architecture contract, and English/Chinese user/developer manuals so TypeScript clients use the helper rather than hand-building request methods, headers, query strings, or submitted-value bodies.

## Verification

- Red check first: `tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_json_request_helpers` failed before implementation.
- Focused helper checks: `tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_json_request_helpers` passed, and the endpoint/request helper pair passed with 2 tests.
- Desktop TypeScript build: `rtk npm --prefix apps/desktop run build`.
- Targeted Python checks: `tests/test_architecture.py tests/test_cli.py -q` passed with 70 tests, and `tests/test_sdk_examples.py -q` passed with 20 tests.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py`.
- Formatting/diff checks: `rtk bash scripts/flake.bash --ci` and `rtk git diff --check`.
- Full suite: `rtk bash scripts/test.bash` passed with 491 tests.
- Package build: `rtk uv build`.

## Risks Or Blockers

- The direct Linear connector accepted the TAL-295 progress comment. The Codex app Linear connector was not used for this slice because the direct connector was available after tool discovery.
- The helpers intentionally build only frontend API meta requests; SDK-owned option resolution, normalization, and REST request planning remain in Python.

## Next

- Continue tightening frontend-facing APIs around SDK-owned action metadata and request affordances without moving domain behavior into TypeScript.
- Start the next slice from the remaining desktop shell integration gaps rather than broadening the helper into a generated REST client.
