# Project Module Discovery Progress

Date: 2026-06-06 19:18 CST

Linear: TAL-294

## Done

- Added `discover_modules(...)` for `source_root/modules/<family>/<module>` discovery.
- Added default module slots for `def.pdx`, root `.loc` files, root image assets, `copy/*`, and `assets/*`.
- Added `Project.discover_modules()` as the SDK boundary over build-layer discovery.
- Updated `Project.build()` to discover modules from `source_roots` when callers do not pass explicit modules.
- Verified the CLI dry-run build now reports discovered demo modules.

## Verification

- `rtk uv run pytest tests/test_project_build.py -q`
- `rtk uv run pytest tests/test_project.py tests/test_project_build.py tests/test_module_sources.py tests/test_simple_source_family.py tests/test_build_slots.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build src/paradev/sdk/project.py tests/test_project_build.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this project-discovery slice.

## Next

- Add an opt-in project build emit path that writes artifacts through registered writers while keeping dry-run as the default CLI mental model.
