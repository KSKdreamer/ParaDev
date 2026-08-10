# Profile Registry Progress

Date: 2026-06-06 19:27 CST

Linear: TAL-294

## Done

- Added `registry_for_profile(...)` under `paradev.games`.
- Added an initial `hoi4` scaffold profile registry.
- Wired `Project.build(profile=...)` to use the selected profile registry when no explicit registry is supplied.
- Added CLI `--profile` for build profile overrides.
- Updated the default demo dry run to plan a `common/national_focus/{object_id}.txt` artifact from discovered focus modules.

## Verification

- `rtk uv run pytest tests/test_project_build.py -q`
- `rtk uv run pytest tests/test_project.py tests/test_project_build.py tests/test_artifact_writers.py tests/test_simple_source_family.py tests/test_architecture.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/sdk/project.py src/paradev/games tests/test_project_build.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- The `hoi4` profile is a scaffold proof for generic source families and writers; collection-aware HOI4 focus-tree compilation is still future work.
- Existing local desktop and README edits remain outside this profile-registry slice.

## Next

- Add localization artifact writing so profile-planned builds can emit `.yml` localization outputs from loaded `.loc` entries.
