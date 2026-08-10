# Metadata Key Guard Progress

Date: 2026-06-07 07:50 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added registry-time validation for Python-backed family `metadata_keys`.
- Python-backed metadata key declarations now fail with a contextual `ProjectManifestError` when non-string values would otherwise be filtered out of family inspection and discovery contracts.
- Added a regression test through the trusted `python_modules` path with `SimpleSourceFamily(..., metadata_keys=("scope", 7))`.
- Documented that Python-backed `metadata_keys`, `settings_keys`, and `required_settings` share the same string-list contract.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_metadata_keys -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_invalid_metadata_keys -q`
- Related metadata checks: `rtk uv run pytest tests/test_project_build.py::test_project_build_uses_registered_family_source_slots tests/test_project_build.py::test_project_build_uses_manifest_declared_simple_family -q`
- Family view check: `rtk uv run pytest tests/test_project.py::test_project_families_prefers_family_source_slot_contracts -q`
- Broader project/build tests: `rtk uv run pytest tests/test_project.py tests/test_project_build.py -q` passed with 123 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 238 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The registry now catches malformed Python-backed metadata contracts before clients read `families()` or discovery tries to load custom metadata keys.
- The change reuses the existing family string-list validator, so it keeps behavior aligned with `settings_keys` and `required_settings`.
- Valid registered and manifest-declared metadata-key flows still pass.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue hardening Python-backed generic family declarations around asset constraints and source-slot contracts.
- Keep compiler-author errors early and explicit before expanding the generic module compilation layer.
