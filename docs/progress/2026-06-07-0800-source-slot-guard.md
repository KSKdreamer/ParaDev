# Source Slot Guard Progress

Date: 2026-06-07 08:00 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added registry-time validation for Python-backed family `source_slots` and `collection_source_slots`.
- Python-backed source slots now reject invalid slot lists, empty `name` or `match` values, non-boolean flags, and invalid `kind` values before family inspection or discovery.
- Added a regression test through the trusted `python_modules` path with `SimpleSourceFamily(..., source_slots=(Slot("", "def.pdx"),))`.
- Documented the Python-backed slot contract beside the existing registry extension workflow.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_source_slot -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_source_slot -q`
- Registered slot build checks: `rtk uv run pytest tests/test_project_build.py::test_project_build_uses_registered_family_source_slots tests/test_project_build.py::test_project_build_uses_registered_collection_source_slots -q`
- Broader project/build tests: `rtk uv run pytest tests/test_project.py::test_project_families_prefers_family_source_slot_contracts tests/test_project.py tests/test_project_build.py -q` passed with 125 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 240 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The guard keeps malformed Python-backed slots from leaking into discovery, family capability views, and source-map contracts.
- Existing registered module and collection source-slot flows still pass.
- The implementation preserves the small public model: family authors still use `Slot`; invalid values simply fail earlier and with context.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue hardening the registered family path, then shift back toward parser/build graph behavior once family extension contracts are consistently early-failing.
- Keep explicit SDK errors ahead of generic module compilation expansion.
