# Desktop Form Controls Progress

Date: 2026-06-08 13:41 CST

Linear: TAL-295

## Done

- Added `FrontendApiFormControlKind`, `FrontendApiFormControl`, `getFrontendApiFormControlKind(...)`, and `getFrontendApiFormControls(...)` to the desktop TypeScript frontend API helper.
- Derived selected-action control kind, submitted/default value preview, defaulted state, choices, option-source metadata, `maps_to`, `minimum`, and disabled reasons for missing option-source requirements from generated operation `inputs`.
- Rendered the selected workspace section's default action controls in the desktop workspace as read-only form state so frontend panels can see defaults and missing requirements without owning a parallel form schema.
- Updated the architecture guide, GUI spec, and English/Chinese user/developer manuals to document `getFrontendApiFormControls(...)` as the maintained TypeScript helper for selected-action form render state.

## Verification

- Red check first: `tests/test_architecture.py::test_desktop_workspace_uses_generated_form_controls_for_selected_action` failed before the helper and workspace rendering existed.
- Focused checks: `tests/test_architecture.py::test_desktop_workspace_uses_generated_form_controls_for_selected_action tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_selected_action_detail tests/test_architecture.py::test_desktop_workspace_renders_selected_section_actions_from_frontend_api_helper tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_input_metadata -q` passed with 4 tests.
- Browser smoke: opened `http://127.0.0.1:5173` through the in-app browser; the app rendered and console output had no warnings or errors.
- Targeted Python checks: `tests/test_architecture.py tests/test_cli.py -q` passed with 74 tests, and `tests/test_sdk_examples.py -q` passed with 20 tests.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py`.
- Formatting/diff checks: `rtk bash scripts/flake.bash --ci` and `rtk git diff --check`.
- Full suite: `rtk bash scripts/test.bash` passed with 495 tests.
- Package build: `rtk uv build`.
- Desktop TypeScript build: `rtk npm --prefix apps/desktop run build`.

## Risks Or Blockers

- The form controls are intentionally read-only. They do not yet mutate local form state, resolve dynamic options, normalize submitted values, or execute actions.
- Dynamic option lists still need to be requested through SDK-owned options endpoints; this slice only exposes disabled reasons when required context is not available.

## Next

- Add selected-action form state and dynamic option request planning through `buildFrontendApiOptionsRequest(...)`.
- Keep action execution routed through normalize/rest-plan helpers before adding any write path to the desktop shell.
