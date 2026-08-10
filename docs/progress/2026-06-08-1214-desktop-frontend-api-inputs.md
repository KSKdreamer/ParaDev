# Desktop Frontend API Inputs Progress

Date: 2026-06-08 12:14 CST

Linear: TAL-295

## Done

- Added a desktop TypeScript helper layer for raw frontend API input metadata: typed option sources, `frontendApiInputOperations`, input lookup, required-name lookup, default-value lookup, and option-source field lookup.
- Added an architecture guard so the desktop helper continues exposing those input/default/option-source helpers.
- Updated the GUI spec, architecture interface contract, and English/Chinese user/developer manuals to route frontend code through the helper instead of scanning generated JSON or keeping local form defaults.

## Verification

- Red check first: `rtk bash scripts/test.bash tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_input_metadata -q` failed before the helper existed.
- Focused architecture check: `5 passed`.
- Desktop TypeScript build: `rtk npm --prefix apps/desktop run build`.
- Targeted Python checks: `tests/test_architecture.py tests/test_cli.py -q` passed with 68 tests, and `tests/test_sdk_examples.py -q` passed with 20 tests.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py`.
- Formatting/diff checks: `rtk bash scripts/flake.bash --ci` and `rtk git diff --check`.
- Full suite: `rtk bash scripts/test.bash` passed with 489 tests.
- Package build: `rtk uv build`.

## Risks Or Blockers

- None for this slice. Linear TAL-295 accepted the progress comment.

## Next

- Continue keeping the frontend-facing operation list, desktop helper, and manuals in one reviewable slice whenever GUI-facing API rows change.
- Extend the helper only when a frontend panel needs derived metadata that should remain SDK-owned rather than app-local.
