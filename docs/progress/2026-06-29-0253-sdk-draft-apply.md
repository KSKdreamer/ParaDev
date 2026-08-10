# SDK Draft Apply Progress

Date: 2026-06-29 02:53 CST

Linear: none

## Done

- Moved project source text reads and draft apply validation/writes onto `Project.read_source_text(...)` and `Project.apply_source_draft(...)`.
- Kept REST, CLI, and frontend operation rows as wrappers around the SDK-owned methods.
- Regenerated Project API, CLI API, Frontend API, SDK/CLI, API catalog, and desktop TypeScript contract references.
- Updated architecture/frontend manual prose to name the SDK helpers behind source editing.

## Verification

- `rtk bash scripts/test.bash tests/test_project.py tests/test_architecture.py tests/test_cli.py tests/test_rest_facade_api_selection.py -q`: 432 passed.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/surfaces/rest.py src/paradev/cli.py src/paradev/surfaces/cli.py src/paradev/sdk/frontend_api.py tests/test_project.py tests/test_architecture.py tests/test_cli.py`: OK.
- `rtk npm --prefix apps/desktop run build`: passed; Vite reported existing large-chunk warnings.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk git diff --check`: passed.

## Risks Or Blockers

- Payload schema names still use the existing `paradev.rest.*` ids for compatibility; renaming them would be a separate cross-surface migration.

## Next

- Continue reducing GUI/Tauri duplication by moving the remaining source-editor and project browser effects behind explicit SDK APIs.
