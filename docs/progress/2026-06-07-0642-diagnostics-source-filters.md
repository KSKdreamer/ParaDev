# Diagnostics Source Filters Progress

Date: 2026-06-07 06:42 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Extended SDK diagnostic filtering to match resolved source metadata as well as diagnostic row fields.
- Covered SDK and CLI filters using the resolved authored source path and resolved source slot from the diagnostics payload.
- Updated the build-flow diagnostics workflow to document the broader owner, source, and slot filter behavior.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_project.py::test_project_diagnostics_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_diagnostics_manifest_json -q` failed because resolved source path plus `slot=def` returned no diagnostics.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_diagnostics_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_diagnostics_manifest_json tests/test_project_build.py::test_hoi4_profile_blocks_missing_decision_category_localization_keys -q`
- Related project/build tests: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_build_manifest.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The manifest format did not need to change because diagnostics already include a resolved `source` object.
- The filter remains backward compatible with logical diagnostic fields such as `slot=loc` while also supporting the authored source slot such as `slot=def`.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue tightening diagnostics around source slots for compiler-family checks.
- Start the next generic compiler-system slice from the short-term plan once the diagnostic inspection surface is stable.
