# 2026-06-07 14:00 - Slot Regex Diagnostics

## Scope

- Hardened direct `match_slots(...)` SDK calls so malformed regex slots return a structured `slot.invalid_regex` diagnostic instead of leaking `re.error`.
- Added focused source-slot coverage for invalid regex diagnostics, including module and slot anchoring.
- Kept project manifest, Python-backed family, and registry validation behavior intact; those paths still reject malformed regexes before discovery starts.
- Updated the build workflow docs to describe direct SDK regex diagnostics.

## Verification

- Red: `rtk uv run pytest tests/test_build_slots.py::test_slot_matching_reports_invalid_regex_slots` failed with a raw `re.error`.
- Green: `rtk uv run pytest tests/test_build_slots.py::test_slot_matching_reports_invalid_regex_slots` passed.
- Related: `rtk uv run pytest tests/test_build_slots.py tests/test_build_registry.py` passed with 12 tests.
- Related: `rtk uv run pytest tests/test_build_slots.py tests/test_build_registry.py tests/test_project_build.py` passed with 77 tests.
- Diff hygiene: `rtk git diff --check` passed.
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/slots.py tests/test_build_slots.py` passed with `OK: 2 file(s) - no banned imports`.
- Flake: `rtk bash scripts/flake.bash --ci` passed with 47 files unchanged.
- Full tests: `rtk bash scripts/test.bash` passed with 309 tests.

## Review Notes

- This keeps direct SDK slot matching diagnostic-oriented, matching the user-facing build surfaces instead of exposing a Python regex exception.
- Regex slots are now compiled once per slot during matching and the compiled pattern is reused for path checks.
- Linear sync to TAL-294 was attempted, but the API session is expired and returned `UNAUTHORIZED`; local progress continues until the session is refreshed.
