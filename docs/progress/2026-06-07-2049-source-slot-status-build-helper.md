# Source Slot Status Build Helper

Date: 2026-06-07 20:49 Asia/Shanghai

Branch: `codex/scaffold-source-root-selection`

Issues: TAL-294, TAL-295

## Summary

- Moved source-slot status row, filter, and index logic from the SDK adapter into `paradev.build.source_slot_status(...)`.
- Exported `SOURCE_SLOTS_SCHEMA` and `source_slot_status` from `paradev.build` as a reusable build-layer contract.
- Kept `Project.source_slots(...)`, `Project.inspect("source-slots", ...)`, and the `paradev source-slots` CLI payload shape unchanged.
- Added direct build-layer tests for module slot state and collection descriptor repeated-slot grouping.
- Updated the English and Chinese developer manual plus build-flow docs to point future surfaces and tests at the reusable helper.

## TDD Notes

- Red first:
  `rtk bash scripts/test.bash tests/test_source_slot_status.py -q`
  failed with `ImportError: cannot import name 'source_slot_status' from 'paradev.build'`.
- Green focused set:
  `rtk bash scripts/test.bash tests/test_source_slot_status.py tests/test_project.py::test_project_source_slots_returns_contract_status_payload_without_writing tests/test_project.py::test_project_source_slots_filters_collection_descriptor_status tests/test_project.py::test_project_source_slots_merges_repeated_slot_declarations tests/test_project.py::test_project_cli_filters_source_slots_json tests/test_project.py::test_project_inspections_describes_sdk_dispatch_contract -q`
  passed 7 tests.

## Verification

- `rtk uv run black src/paradev/build/source_slots.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_source_slot_status.py`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/source_slots.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_source_slot_status.py tests/test_project.py tests/test_architecture.py`
- `rtk git diff --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash` passed 374 tests.
- `rtk uv build`

## Review

Heaven-style diff review found no blocking findings. The useful ownership change is that the SDK is now a thin adapter around a build-layer helper, so future GUI, MCP, REST, or compiler tests can reuse the same source-slot contract without duplicating project-surface logic.

## Next

- Continue TAL-294 toward the next generic module compiler surface rather than PIHC3-specific migration work.
- Keep TAL-295 docs aligned as CLI and SDK inspection contracts stabilize.
