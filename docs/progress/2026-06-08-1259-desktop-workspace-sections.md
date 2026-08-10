# Desktop Workspace Sections Progress

Date: 2026-06-08 12:59 CST

Linear: TAL-295

## Done

- Replaced the desktop shell's static feature-module and workspace-tab data with derived views over `frontendApiWorkspaceSections`.
- Used `getFrontendApiDefaultSectionAction(...)` so shell copy follows the SDK-owned default action for each workspace section.
- Removed the hardcoded PIHC3 migration label from the desktop project panel and changed the panel list label from modules to workspace.
- Added horizontal tab overflow handling so the full canonical workspace section list can render without compressing tab content.
- Updated the GUI spec, architecture guide, and English/Chinese manuals to document `frontendApiWorkspaceSections` as the shell navigation source.

## Verification

- Red check first: `tests/test_architecture.py::test_desktop_shell_derives_workspace_navigation_from_frontend_api_sections` failed before implementation.
- Focused checks: `tests/test_architecture.py::test_desktop_frontend_api_helper_consumes_generated_contract tests/test_architecture.py::test_desktop_shell_derives_workspace_navigation_from_frontend_api_sections -q` passed with 2 tests.
- Desktop TypeScript build: `rtk npm --prefix apps/desktop run build`.
- Browser smoke: opened `http://127.0.0.1:5173` through the in-app browser at desktop size; the app rendered, with only the pre-existing missing `favicon.ico` 404 in console output.
- Targeted Python checks: `tests/test_architecture.py tests/test_cli.py -q` passed with 71 tests, and `tests/test_sdk_examples.py -q` passed with 20 tests.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py`.
- Formatting/diff checks: `rtk bash scripts/flake.bash --ci` and `rtk git diff --check`.
- Full suite: `rtk bash scripts/test.bash` passed with 492 tests.
- Package build: `rtk uv build`.

## Risks Or Blockers

- The browser console still reports `GET /favicon.ico` as 404. It is outside this slice and does not affect the shell contract rendering.
- This remains a local generated-contract integration; runtime REST calls are still intentionally deferred to the typed helper/action execution slices.

## Next

- Continue connecting desktop panels to selected action detail and generated form metadata from the same frontend API helper.
- Keep actual option resolution, normalization, and REST request planning in the Python SDK and REST frontend API endpoints.
