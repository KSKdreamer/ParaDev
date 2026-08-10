# HeavenBase Catalog Preview Progress

Date: 2026-06-07 04:48 CST

Linear: unavailable; no Linear connector was exposed and `linear` is not on PATH.

## Done

- Replaced the placeholder `paradev.hb` module with a read-only `catalog_preview(...)` helper.
- Added `paradev hb catalog-preview <path> --json` for deterministic HeavenBase-ready rows without database writes.
- Grouped preview rows for project, source files, build artifacts, dependencies, localization, assets, sprites, HOI4 entities, and diagnostics.
- Updated the CLI surface contract and docs with the implemented preview command.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_hb.py -q` failed because `catalog_preview` was missing.
- Focused green: `rtk bash scripts/test.bash tests/test_hb.py -q`
- Related: `rtk bash scripts/test.bash tests/test_hb.py tests/test_cli.py tests/test_project.py tests/test_build_manifest.py tests/test_architecture.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/hb/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_hb.py`
- CLI smoke: `rtk uv run paradev hb catalog-preview demos/assets/projects/minimal --json`
- Whitespace: `rtk git diff --check -- src/paradev/hb/__init__.py src/paradev/cli.py src/paradev/surfaces/cli.py tests/test_hb.py docs/resources/02-heavenbase-architecture.md docs/workflows/build-flow.md docs/progress/2026-06-07-0448-hb-catalog-preview.md`

## Risks Or Blockers

- This is a preview-only bridge; it does not create or write a HeavenBase workspace yet.
- Linear status could not be updated from this environment.

## Next

- Add an in-memory catalog smoke path once the HeavenBase schema-pack boundary is ready.
- Keep catalog rows derived from SDK manifests so CLI, MCP, and desktop surfaces do not duplicate build logic.
