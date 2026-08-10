# Source Slot Status Inspection

Date: 2026-06-07 20:36 Asia/Shanghai

Branch: `codex/scaffold-source-root-selection`

Issues: TAL-294, TAL-295

## Summary

- Added `Project.source_slots(...)` with schema `paradev.build.source-slots.v1`.
- Added `Project.inspect("source-slots", ...)` and `paradev source-slots`.
- Joined registered family source-slot contracts with the current dry build's source inventory and diagnostics.
- Returned one logical row per module or collection descriptor slot with `satisfied`, `missing`, `empty`, or `diagnostic` status.
- Collapsed repeated declarations for the same logical slot and exposed `matches` when more than one source pattern contributes.
- Updated CLI surface metadata plus English and Chinese user/developer manuals.

## TDD Notes

- Red first:
  `rtk bash scripts/test.bash tests/test_project.py::test_project_source_slots_returns_contract_status_payload_without_writing tests/test_project.py::test_project_cli_filters_source_slots_json tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands -q`
  failed because `Project.source_slots`, `Project.inspect("source-slots")`, and `paradev source-slots` did not exist.
- Red edge case:
  `rtk bash scripts/test.bash tests/test_project.py::test_project_source_slots_merges_repeated_slot_declarations -q`
  failed because repeated slot declarations emitted duplicate logical rows.
- Green focused set:
  `rtk bash scripts/test.bash tests/test_project.py::test_project_source_slots_returns_contract_status_payload_without_writing tests/test_project.py::test_project_source_slots_filters_collection_descriptor_status tests/test_project.py::test_project_source_slots_merges_repeated_slot_declarations tests/test_project.py::test_project_cli_filters_source_slots_json tests/test_project.py::test_project_sources_returns_filtered_compiler_input_payload_without_writing tests/test_project.py::test_project_cli_filters_sources_manifest_json tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract tests/test_project.py::test_project_cli_outputs_inspections_contract_json tests/test_architecture.py::test_cli_surface_contract_lists_sdk_owned_adapter_commands -q`
  passed 9 tests.

## Verification

- `rtk uv run black src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_project.py tests/test_architecture.py`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_project.py tests/test_architecture.py`
- `rtk git diff --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash` passed 372 tests.
- `rtk uv run paradev source-slots demos/assets/projects/minimal --slot def --json`
- `rtk uv run python -c "from paradev.sdk import Project; payload = Project.load('demos/assets/projects/minimal').inspect('source-slots', module_id='focus/GER_sample', slot='def'); assert payload['source_slots'][0]['status'] == 'satisfied'; print(payload['source_slots'][0]['slot'], payload['source_slots'][0]['status'])"`
- `rtk uv build`

## Review

Heaven-style diff review found no blocking findings after the repeated-slot duplicate-row bug was fixed before commit. Residual risk is limited to payload shape churn while downstream GUI/MCP clients are still early; the command is SDK-owned and discoverable through `Project.inspections()`.

## Next

- Continue TAL-294 generic compiler stabilization by moving from inspection ergonomics to the next reusable writer/compiler gap.
- Keep PIHC3-specific migration work out of this branch unless it exposes a generic family or source-slot requirement.
