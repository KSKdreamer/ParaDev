# Desktop Option Control Binding Progress

Date: 2026-06-08 14:55 CST

Linear: TAL-299, TAL-295

## Done

- Added `FrontendApiFormControlOptionSource`, `FrontendApiFormControlOption`, and `FrontendApiFormOptionResults` to the desktop frontend API helper so rendered controls can carry static choices and SDK-returned option payload rows through one typed model.
- Extended `getFrontendApiFormControls(operationId, values, optionResults)` to convert static `choices` and successful `paradev.sdk.frontend-api.options.v1` payloads into select-ready option rows with stable value tokens.
- Updated the desktop workspace form renderer to pass option results back into the generated control helper, render select controls when options exist, and preserve the original option value when the user chooses a row.
- Styled generated select controls through the existing form-control rules and added an inline favicon so browser smoke checks do not report a missing `/favicon.ico`.
- Updated the English and Chinese frontend API, SDK, developer, architecture, and GUI spec manual text so future frontend code uses the helper instead of maintaining an option-to-control mapper.

## Verification

- Red check first: `rtk bash scripts/test.bash tests/test_architecture.py::test_desktop_workspace_binds_option_results_to_generated_form_controls -q` failed before the option-control types and helper plumbing existed.
- Focused option-control checks: `rtk bash scripts/test.bash tests/test_architecture.py::test_desktop_workspace_binds_option_results_to_generated_form_controls tests/test_architecture.py::test_desktop_workspace_executes_option_requests_through_sdk_endpoint_helper tests/test_architecture.py::test_desktop_workspace_uses_generated_form_controls_for_selected_action tests/test_architecture.py::test_desktop_workspace_plans_option_requests_from_local_form_state -q` passed with 4 tests.
- Architecture and CLI checks: `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q` passed with 77 tests.
- SDK examples: `rtk bash scripts/test.bash tests/test_sdk_examples.py -q` passed with 20 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 498 tests.
- Desktop TypeScript build: `rtk npm --prefix apps/desktop run build`.
- Browser smoke: in-app browser opened `http://127.0.0.1:5174?smoke=option-controls` with 0 console errors.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py` returned OK.
- Formatting/diff checks: `rtk bash scripts/flake.bash --ci` and `rtk git diff --check`.
- Package build: `rtk uv build`.

## Review

- Local diff review checked the value-token path in `apps/desktop/src/data/frontendApi.ts` and `apps/desktop/src/components/Workspace.tsx`.
- No blocking issues found. The current behavior intentionally keeps option provider execution in the SDK/meta endpoint path and keeps React responsible only for local submitted values plus rendering.

## Risks Or Blockers

- Object-valued option rows render safely, but selected-state matching is strongest for primitive option values. Current SDK providers return frontend-facing scalar values for the first desktop use cases.
- The shell still needs submitted-value normalization and REST request planning before action execution can be fully frontend-driven.

## Next

- Add desktop consumption for `normalize_frontend_api_inputs(...)` and `plan_frontend_api_rest_request(...)`.
- Keep TAL-299 as the canonical API maintenance ticket and TAL-295 as the manual freshness ticket for every frontend-visible SDK/CLI change.
