# 2026-06-07 21:36 CST - Authoring Build Views

## Scope

- Continued the generic SDK/build contract track for GUI, MCP, importer, and migration agents.
- Added reusable build-layer authoring helpers:
  - `paradev.build.authoring_view(...)`
  - `paradev.build.authoring_path_view(...)`
- Kept `Project.authoring_path(...)`, `Project.templates()`, and the CLI `authoring-path` payloads compatible by delegating shared source-root/path payload assembly to the build layer.
- Updated English and Chinese manual sections plus the build workflow docs to distinguish normal SDK usage from lower-level adapter helper usage.

## TDD

- Red test:
  - `rtk bash scripts/test.bash tests/test_authoring_views.py -q`
  - Failed as expected with `ImportError: cannot import name 'authoring_path_view' from 'paradev.build'`.
- Added direct build-layer tests for:
  - authoring source-root/template payloads;
  - module and collection authoring path payloads;
  - unknown source-root errors;
  - relative source roots resolved from the project root.
- During review, added the relative-source-root edge test before fixing the helper. It failed with `source_root == 'src'` instead of the resolved project source root, then passed after normalization.

## Verification

- `rtk uv run black src/paradev/build/views.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_authoring_views.py`
- `rtk bash scripts/test.bash tests/test_authoring_views.py tests/test_project.py tests/test_cli.py tests/test_build_registry.py -q`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/views.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_authoring_views.py tests/test_project.py tests/test_cli.py tests/test_build_registry.py`
- `rtk git diff --check`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv build`

Result: focused/broader tests passed, Heaven-style scan passed, diff whitespace passed, flake passed, full suite passed with 384 tests, and package build produced the source distribution plus wheel.

## Review

- Heaven-style diff review found no blocking findings after the relative source-root fix.
- Public SDK and CLI payload shapes remain unchanged.
- The reusable authoring payloads are now available without duplicating `Project` internals.

## Next

- Continue extracting reusable read-only project/build projections for adapter agents before broadening compiler-family behavior.
- Keep TAL-294 focused on generic compiler/build foundation and TAL-295 focused on manual and SDK usability.
