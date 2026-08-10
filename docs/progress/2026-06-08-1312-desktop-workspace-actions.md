# Desktop Workspace Actions Progress

Date: 2026-06-08 13:12 CST

Linear: TAL-295

## Done

- Typed desktop feature-module and workspace-tab state with `ParaDevFrontendApiWorkspaceSectionId` so selected workspace state follows the generated frontend API contract.
- Added a shared workspace-section selection handler in the desktop shell so sidebar/module clicks and workspace tabs stay synchronized.
- Rendered the selected section's canonical action rows through `getFrontendApiSectionActions(...)`.
- Highlighted the default action through `getFrontendApiDefaultSectionAction(...)` and surfaced the action execution surface plus required-input count through `getFrontendApiRequiredInputNames(...)`.
- Updated the GUI spec, architecture guide, and English/Chinese manuals so frontend shells use the SDK-owned workspace section/action helpers instead of local action tables.

## Verification

- Red check first: `tests/test_architecture.py::test_desktop_workspace_renders_selected_section_actions_from_frontend_api_helper` failed before the desktop workspace used the generated workspace-section id type and action helper.
- Second red check: the same test failed until `handleWorkspaceSectionSelect(...)` synchronized sidebar/module and tab state.
- Focused checks: `tests/test_architecture.py::test_desktop_workspace_renders_selected_section_actions_from_frontend_api_helper tests/test_architecture.py::test_desktop_shell_derives_workspace_navigation_from_frontend_api_sections -q` passed with 2 tests.
- Browser smoke: opened `http://127.0.0.1:5173` through the in-app browser; the app rendered and console output had no warnings or errors.
- Targeted Python checks: `tests/test_architecture.py tests/test_cli.py -q` passed with 72 tests, and `tests/test_sdk_examples.py -q` passed with 20 tests.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py`.
- Formatting/diff checks: `rtk bash scripts/flake.bash --ci` and `rtk git diff --check`.
- Full suite: `rtk bash scripts/test.bash` passed with 493 tests.
- Package build: `rtk uv build`.
- Desktop TypeScript build: `rtk npm --prefix apps/desktop run build`.

## Risks Or Blockers

- Selected action rows still show metadata only. Executing actions from the desktop remains deferred to the typed action-detail/form execution work.
- Runtime option resolution and REST request planning are still owned by the SDK and frontend API endpoints; desktop panels should continue calling those helpers rather than duplicating request construction.

## Next

- Continue connecting selected action detail and generated form metadata into the desktop panel.
- Keep CLI, Python SDK, REST, MCP, and LSP operation rows synchronized through the maintained frontend API contract.
