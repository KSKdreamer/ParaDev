# 2026-06-07 21:23 CST - Family Build View

## Scope

- Continued the generic SDK/build modularity track for GUI, MCP, importer, and migration agents.
- Added `paradev.build.families_view(...)` as the reusable build-layer wrapper for the `paradev.build.families.v1` family contract payload.
- Kept `Project.families(...)` and `paradev families` payload-compatible by delegating to the build-layer helper.
- Updated the English and Chinese manuals plus build workflow docs to distinguish the user-facing SDK call from the reusable build-layer helper.

## TDD

- Red test:
  - `rtk bash scripts/test.bash tests/test_build_registry.py -q`
  - Failed as expected with `ImportError: cannot import name 'families_view' from 'paradev.build'`.
- Added a direct build-layer test for `families_view(...)` that verifies schema, project/profile wrapper fields, authoring roots/templates, family rows, writer rows, filters, and rebuilt indexes.

## Verification

- `rtk uv run black src/paradev/build/views.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_build_registry.py`
- `rtk bash scripts/test.bash tests/test_build_registry.py tests/test_project.py -q`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/views.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_build_registry.py tests/test_project.py`
- `rtk git diff --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv build`

Result: focused registry/project tests passed, Heaven-style scan passed, diff whitespace passed, flake passed, full suite passed with 380 tests, and package build produced the source distribution plus wheel.

## Review

- Heaven-style diff review found no blocking findings.
- The change does not alter the CLI/SDK payload shape; it centralizes wrapper assembly around the build registry contract.
- The helper keeps family contract reuse explicit for adapters that already hold a registry and project context.

## Next

- Continue moving reusable read-only projections and compiler orchestration helpers into build-owned APIs before adding broader family compilers.
- Keep TAL-294 aligned with the generic compiler foundation and TAL-295 aligned with user-facing SDK/manual stability.
