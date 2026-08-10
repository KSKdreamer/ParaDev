# Source Slot Regex Guard Progress

Date: 2026-06-07 08:05 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added early validation for regex source-slot patterns in declarative project-local family specs.
- Added matching registry-time validation for Python-backed family `source_slots` and `collection_source_slots`.
- Invalid regex patterns now raise contextual `ProjectManifestError` messages during `Project.load(...)` or `project.families()` instead of surfacing later as raw discovery-time `re.error` exceptions.
- Added regression tests for both `paradev.yaml` declarations and trusted `python_modules` registration.
- Documented that source slot regex patterns are compiled before discovery starts.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_manifest_rejects_invalid_source_slot_regex tests/test_project.py::test_project_families_rejects_python_module_with_invalid_source_slot_regex -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_manifest_rejects_invalid_source_slot_regex tests/test_project.py::test_project_families_rejects_python_module_with_invalid_source_slot_regex -q`
- Valid slot view checks: `rtk uv run pytest tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project.py::test_project_families_returns_asset_contracts -q`
- Valid slot build checks: `rtk uv run pytest tests/test_project_build.py::test_project_build_uses_manifest_declared_simple_family tests/test_project_build.py::test_project_build_uses_registered_family_source_slots tests/test_project_build.py::test_project_build_uses_registered_collection_source_slots -q`
- Broader project/build tests: `rtk uv run pytest tests/test_project.py tests/test_project_build.py -q` passed with 127 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 242 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/extensions.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The change moves malformed regex patterns to the same early validation boundary as other source-slot shape errors.
- Both project-local manifest families and Python-backed family modules now share the same user-facing failure timing.
- Existing valid regex and non-regex slot flows still pass.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue moving malformed compiler-author contracts out of discovery and into contextual SDK validation.
- Shift back toward PDX parser/build graph behavior once the family extension surface is consistently early-failing.
