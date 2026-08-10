# Source Slot Suggested Paths

Date: 2026-06-07 23:29

Issues: TAL-294, TAL-295

## Summary

- Added `suggested_relative_paths` and `suggested_paths` to `paradev.build.source-slots.v1` rows for exact, non-glob, non-regex source slots.
- Kept suggestions on both satisfied and missing rows so GUI, MCP, REST, importer, and script clients can show where an expected file belongs without recomputing family slot rules.
- Covered module slots, missing required slots, collection descriptor slots, and repeated logical slots with exact-plus-glob declarations.
- Updated English and Chinese user/developer docs plus build-flow docs for the richer source-slot inspection payload.

## Tests

- Red: `rtk bash scripts/test.bash tests/test_source_slot_status.py tests/test_project.py::test_project_source_slots_returns_contract_status_payload_without_writing tests/test_project.py::test_project_source_slots_filters_collection_descriptor_status -q`
  - Failed before implementation because source-slot rows lacked suggested path fields.
- Focused green: `rtk bash scripts/test.bash tests/test_source_slot_status.py tests/test_project.py::test_project_source_slots_returns_contract_status_payload_without_writing tests/test_project.py::test_project_source_slots_filters_collection_descriptor_status -q`
  - `4 passed`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/source_slots.py tests/test_source_slot_status.py tests/test_project.py`
  - `OK: 3 file(s) - no banned imports`
- `rtk rg -n 'suggested_relative_paths|suggested_paths|source_slot_status|source-slots|missing file|缺失文件' src/paradev/build/source_slots.py tests/test_source_slot_status.py tests/test_project.py docs/user-manual docs/workflows/build-flow.md`
  - Confirmed implementation, tests, and English/Chinese manual/workflow coverage.
- `rtk git diff --check`
  - Passed.
- `rtk bash scripts/flake.bash --ci`
  - Passed.
- `rtk bash scripts/test.bash`
  - `397 passed`
- `rtk uv build`
  - Built `dist/paradev-0.1.0.0.dev0.tar.gz` and `dist/paradev-0.1.0.0.dev0-py3-none-any.whl`.

## Review

- The change is additive to `paradev.build.source-slots.v1`; existing consumers that only read status, paths, diagnostics, or indexes remain compatible.
- Suggestions are only emitted for exact relative slot matches. Glob and regex slot rows keep the current behavior because there is no single concrete path to recommend.
- Full-suite review found two additional exact payload expectations for repeated slots and CLI-filtered missing slots; both are now covered by the expanded focused test set.
- No PIHC3 migration or GUI implementation code was added.

## Linear

- `TAL-295`: comment `2a2df886-fe22-4c85-a580-46f560e0de4f`.
- `TAL-294`: comment `6148655b-9959-4d39-b0c5-7b35451fbd2e`.
