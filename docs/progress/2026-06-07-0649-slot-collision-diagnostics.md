# Slot Collision Diagnostics Progress

Date: 2026-06-07 06:49 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added an additive `slots` list to diagnostic payloads for source-slot checks that involve more than one slot.
- Updated slot collision diagnostics to include a deterministic primary `slot` plus the full collided `slots` list.
- Extended diagnostics filtering so `--slot` and `Project.diagnostics(slot=...)` match any slot listed by a multi-slot diagnostic.
- Documented the multi-slot diagnostic filter behavior in the build-flow workflow.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_build_slots.py::test_slot_matching_reports_source_collisions tests/test_project.py::test_project_diagnostics_filters_slot_collision_by_collided_slot -q` failed because collision diagnostics had no slot payload and `slot=loc` returned no diagnostics.
- Focused green: `rtk bash scripts/test.bash tests/test_build_slots.py::test_slot_matching_reports_source_collisions tests/test_project.py::test_project_diagnostics_filters_slot_collision_by_collided_slot tests/test_project.py::test_project_diagnostics_returns_filtered_manifest_payload_without_writing tests/test_project.py::test_project_cli_filters_diagnostics_manifest_json tests/test_build_records.py -q`
- Related tests: `rtk bash scripts/test.bash tests/test_build_slots.py tests/test_project.py tests/test_build_records.py tests/test_build_manifest.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/records.py src/paradev/build/slots.py src/paradev/sdk/project.py tests/test_build_slots.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The diagnostic schema change is additive; existing `slot`, `source_path`, and severity/code indexes stay intact.
- `Diagnostic.slots` was appended to the record definition to avoid shifting existing positional field order.
- Slot-collision rows still carry one primary source object because the manifest resolver has one `slot` anchor; the new `slots` list is the authoritative multi-slot membership.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue tightening generic compiler diagnostics where a check spans multiple source records.
- Move toward the next generic module compilation slice after diagnostics inspection remains stable.
