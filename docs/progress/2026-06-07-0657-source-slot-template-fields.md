# Source Slot Template Fields Progress

Date: 2026-06-07 06:57 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added `{source_slot}` and `{slot}` placeholders to generic module artifact templates.
- Added the same placeholders to generic collection descriptor copy and localization artifact templates.
- Kept existing `{source_name}`, `{source_stem}`, `{source_suffix}`, language, module, collection, and object id placeholders unchanged.
- Documented the source-slot placeholder surface for declarative project-local families.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_simple_source_family_templates_can_use_source_slot tests/test_simple_source_family.py::test_collection_source_family_templates_can_use_source_slot -q` failed with `KeyError: 'source_slot'` in module and collection template rendering.
- Focused green: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_simple_source_family_templates_can_use_source_slot tests/test_simple_source_family.py::test_collection_source_family_templates_can_use_source_slot -q`
- Generic family tests: `rtk bash scripts/test.bash tests/test_simple_source_family.py -q`
- Related project-build tests: `rtk bash scripts/test.bash tests/test_project_build.py tests/test_simple_source_family.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py tests/test_simple_source_family.py`
- Diff hygiene: `rtk git diff --check`

## Review

- This is an additive template-surface change for generic compiler authors; no manifest schema changed.
- Module PDX, module localization, module copy, collection localization, collection copy, and sprite-name templates now receive a source-slot value when the source record has one.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue hardening project-local compiler ergonomics, especially bad template diagnostics and generic family validation errors.
- Move toward the next generic module compilation slice after template rendering is stable.
