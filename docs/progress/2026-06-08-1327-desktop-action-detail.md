# Desktop Action Detail Progress

Date: 2026-06-08 13:27 CST

Linear: TAL-295

## Done

- Added `getFrontendApiActionDetail(...)` to the desktop TypeScript frontend API helper so components can read one selected action's operation row, workspace action, section membership, generated form metadata, option-source fields, bindings, and execution hints without scanning generated JSON.
- Rendered the selected workspace section's default action detail in the desktop workspace, including operation summary, default execution surface, available-surface count, generated field count, option-source count, defaults count, and a compact generated field grid.
- Kept action execution and option resolution out of the desktop component; the panel still points future execution toward the SDK-owned normalize/options/rest-plan helpers.
- Updated the architecture guide, GUI spec, and English/Chinese user/developer manuals to document `getFrontendApiActionDetail(...)` as the TypeScript selected-action summary helper.

## Verification

- Red check first: `tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_selected_action_detail` failed before `getFrontendApiActionDetail(...)` existed.
- Focused checks: `tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_selected_action_detail tests/test_architecture.py::test_desktop_workspace_renders_selected_section_actions_from_frontend_api_helper tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_input_metadata tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_workspace_actions tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_rest_endpoint_helpers -q` passed with 5 tests.
- Browser smoke: opened `http://127.0.0.1:5173` through the in-app browser; the app rendered and console output had no warnings or errors.
- Targeted Python checks: `tests/test_architecture.py tests/test_cli.py -q` passed with 73 tests, and `tests/test_sdk_examples.py -q` passed with 20 tests.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py`.
- Formatting/diff checks: `rtk bash scripts/flake.bash --ci` and `rtk git diff --check`.
- Full suite: `rtk bash scripts/test.bash` passed with 494 tests.
- Package build: `rtk uv build`.
- Desktop TypeScript build: `rtk npm --prefix apps/desktop run build`.

## Risks Or Blockers

- The desktop panel is still a read-only selected-action summary. It does not yet execute actions, resolve dynamic options, or submit normalized values.
- The TypeScript detail helper mirrors the generated contract for local rendering; REST/CLI/Python remain the source for runtime selected-action, option, normalize, and REST-plan payloads.

## Next

- Wire generated form controls to selected actions, starting with read-only/default-value state and disabled controls for missing option-source requirements.
- Keep execution planning routed through `buildFrontendApiOptionsRequest(...)`, `buildFrontendApiNormalizeRequest(...)`, and `buildFrontendApiRestPlanRequest(...)` rather than adding desktop-only request logic.
