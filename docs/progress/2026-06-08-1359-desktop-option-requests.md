# Desktop Option Requests Progress

Date: 2026-06-08 13:59 CST

Linear: TAL-295

## Done

- Added `FrontendApiFormOptionRequest`, `getFrontendApiFormValuesWithDefaults(...)`, and `getFrontendApiFormOptionRequests(...)` to the desktop TypeScript frontend API helper.
- Changed selected-action form controls from read-only previews to local per-action submitted values while keeping SDK/default merging in the helper layer.
- Planned dynamic option-source requests from the same generated operation metadata, including `available`, `missing_requirements`, the original `option_source`, and the ready `buildFrontendApiOptionsRequest(...)` fetch input.
- Rendered selected-action option request state in the desktop workspace so users can see which dynamic fields are ready and which still need upstream context.
- Updated the architecture guide, GUI spec, and English/Chinese user/developer manuals to document local form values, helper-owned defaults, and helper-owned option request planning.

## Verification

- Red check first: `tests/test_architecture.py::test_desktop_workspace_plans_option_requests_from_local_form_state` failed before `FrontendApiFormOptionRequest` and the option-request helper existed.
- TypeScript guard: `rtk npm --prefix apps/desktop run build` initially failed until the per-action form state was typed as `Partial<Record<ParaDevFrontendApiOperationId, FrontendApiSubmittedValues>>`.
- Focused checks: `tests/test_architecture.py::test_desktop_workspace_plans_option_requests_from_local_form_state tests/test_architecture.py::test_desktop_workspace_uses_generated_form_controls_for_selected_action tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_selected_action_detail tests/test_architecture.py::test_desktop_workspace_renders_selected_section_actions_from_frontend_api_helper tests/test_architecture.py::test_desktop_frontend_api_helper_exposes_input_metadata -q` passed with 5 tests.
- Browser smoke: opened `http://127.0.0.1:5173` through the in-app browser; the app rendered and console output had no warnings or errors.
- Targeted Python checks: `tests/test_architecture.py tests/test_cli.py -q` passed with 75 tests, and `tests/test_sdk_examples.py -q` passed with 20 tests.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_architecture.py`.
- Formatting/diff checks: `rtk bash scripts/flake.bash --ci` and `rtk git diff --check`.
- Full suite: `rtk bash scripts/test.bash` passed with 496 tests.
- Package build: `rtk uv build`.
- Desktop TypeScript build: `rtk npm --prefix apps/desktop run build`.

## Risks Or Blockers

- The desktop shell still plans option requests only. It does not execute option resolution, normalize submitted values, produce REST execution plans in the UI, or mutate projects.
- Option request rows currently show URL and method only; the next UI slice should connect request execution and render returned option labels without moving provider dispatch into React.

## Next

- Execute selected-action option requests through the SDK-owned frontend API options endpoint.
- Feed returned option payloads into field controls, then continue to normalization and REST request planning before adding any write-path execution in the desktop shell.
