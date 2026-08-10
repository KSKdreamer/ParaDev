# 2026-06-07 13:55 - Registry Slot Validation

## Scope

- Hardened `BuildRegistry` so profile-level `source_slots` and `collection_source_slots` defaults are validated at construction time.
- Reused the same slot contract as Python-backed family-owned slots: non-empty `name` and `match`, boolean flags, valid regexes, rooted non-regex matches, and optional non-empty `kind`.
- Added focused registry tests for invalid default module source slots and collection descriptor slots.
- Updated the build workflow docs to tell profile/plugin authors that registry defaults are validated before family inspection or discovery.

## Verification

- Red: `rtk uv run pytest tests/test_build_registry.py` failed because invalid registry default slots did not raise.
- Green: `rtk uv run pytest tests/test_build_registry.py` passed.
- Related: `rtk uv run pytest tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_project_families_exposes_collection_source_slot_contracts` passed with 3 tests.
- Related: `rtk uv run pytest tests/test_project_build.py tests/test_build_slots.py` passed with 74 tests.
- Diff hygiene: `rtk git diff --check` passed.
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_build_registry.py` passed with `OK: 2 file(s) - no banned imports`.
- Flake: `rtk bash scripts/flake.bash --ci` passed with 47 files unchanged.
- Full tests: `rtk bash scripts/test.bash` passed with 308 tests.

## Review Notes

- This closes a profile extension gap: family-owned slots were validated, but registry default slots could still leak invalid contracts into family inspection and discovery.
- Existing valid profile defaults and family-specific override behavior are covered by the related family inspection and project build tests.
- Linear sync to TAL-294 was attempted, but the API session is expired and returned `UNAUTHORIZED`; local progress continues until the session is refreshed.
