# Python Sprite Template Guard Progress

Date: 2026-06-07 08:24 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added registry-time validation for Python-backed sprite declaration completeness.
- Python-backed simple-source sprite declarations now require a copied texture template, sprite GFX template, sprite name template, and at least one `sprite_slots` entry, matching declarative project-local family validation.
- Added a regression test through the trusted `python_modules` path with sprite templates but no copy template or sprite slots.
- Cleaned up an older source-slot contract fixture that used incomplete sprite templates even though sprite behavior is covered by a dedicated complete sprite-slot contract test.
- Documented the Python-backed sprite declaration requirements in the build workflow guide.

## Verification

- Red check: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_incomplete_sprite_templates -q` failed because no `ProjectManifestError` was raised.
- Focused green: `rtk uv run pytest tests/test_project.py::test_project_families_rejects_python_module_with_incomplete_sprite_templates -q`
- Related project checks: `rtk uv run pytest tests/test_project.py::test_project_manifest_rejects_incomplete_sprite_templates tests/test_project.py::test_project_families_returns_asset_contracts -q`
- Sprite build checks: `rtk uv run pytest tests/test_project_build.py::test_project_build_uses_manifest_declared_sprite_templates tests/test_project_build.py::test_project_build_blocks_manifest_duplicate_sprite_names -q`
- Broader project/build tests: `rtk uv run pytest tests/test_project.py tests/test_project_build.py -q` passed with 130 tests.
- Full suite: `rtk bash scripts/test.bash` passed with 245 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- The new guard moves incomplete Python-backed sprite declarations to the registry boundary instead of letting them silently emit no sprites.
- Existing complete sprite-slot views and sprite artifact generation still pass.
- The source-slot fixture now avoids mixing an unrelated incomplete sprite declaration into a source-slot contract test.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.

## Next

- Continue moving plugin/compiler author mistakes to contextual SDK errors.
- Revisit remaining Python-backed contracts, then shift back toward PDX parser and generic build graph behavior.
