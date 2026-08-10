# AI Profile Project Scope Progress

Date: 2026-06-30 11:33 CST
Linear: active usability goal

## Done

- Made SDK-managed AI chat profile overrides project-scoped when callers pass `project_root`, matching the Python SDK, REST, Tauri, and GUI API shape.
- Kept the existing global `paradev.ai.chat.profiles.profiles` bucket for no-project callers and legacy/default overrides.
- Added a project bucket under the same config key so PIHC3 and another project can edit the same profile without overwriting each other.
- Updated desktop chat role lookup so actual chat prompts use the active project's profile override.
- Tightened three CLI config tests so they hold the shared `CM_PARADEV` lock and isolate `paradev.project.name`; the parallel fast gate exposed the race while native-web bridge tests were writing `PIHC3 Workbench`.

## Verification

- Red first: `rtk uv run pytest tests/test_desktop_api_selection.py -k "profile_overrides_are_project_scoped"` failed because the second project write overwrote PIHC3's `explain` prompt.
- Focused AI profile group: `rtk uv run pytest tests/test_desktop_api_selection.py -k "ai_chat_profile"` passed, 6 tests.
- Full desktop API selection suite: `rtk uv run pytest tests/test_desktop_api_selection.py` passed, 58 tests.
- Direct SDK sanity check under isolated `PARADEV_ROOT`: PIHC3 returned `PIHC3 prompt`, Demo returned `Demo prompt`, and PIHC3 reset returned default `["project", "selection"]` sources.
- Targeted CLI config isolation tests: `rtk uv run pytest tests/test_cli.py -k "config_list_accepts_local_json_option or config_get_serializes_scalar_json_option or cli_output_config_enables_json_by_default"` passed, 3 tests.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/desktop/local.py tests/test_desktop_api_selection.py tests/test_cli.py` passed.
- Flake gate: `rtk bash scripts/flake.bash --ci` passed.
- Fast repo gate: first run exposed the `paradev.project.name` test isolation race; after the CLI test lock fix, `rtk bash scripts/test.bash` passed, 1229 tests with 2 warnings.

## Risks Or Blockers

- Project-specific resets currently remove the project override and then reveal any global inherited override; the UI does not yet label inherited/global profile state.
- Runtime `sourceKindRows` still need to be threaded through the GUI so source labels and future SDK source kinds stay SDK-owned.

## Next

- Add a small UI/API affordance or copy so profile overrides clearly indicate whether they are project-specific or inherited.
- Pass `sourceKindRows` through Config and the floating chat shell.
