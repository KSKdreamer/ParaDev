# Project Artifact Emission Progress

Date: 2026-06-06 19:22 CST

Linear: TAL-294

## Done

- Added `Project.build(..., emit_artifacts=True)` to write planned artifacts through registered artifact writers.
- Kept normal `Project.build()` and CLI `paradev build` behavior as dry-run by default.
- Return `dry_run: false` only for builds that opt into artifact emission.
- Added `--emit-artifacts` to the CLI build command.
- Updated the CLI surface contract to include the existing `build` command.

## Verification

- `rtk uv run pytest tests/test_project_build.py -q`
- `rtk uv run pytest tests/test_project.py tests/test_project_build.py tests/test_artifact_writers.py tests/test_simple_source_family.py tests/test_architecture.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py src/paradev/sdk/project.py src/paradev/surfaces/cli.py tests/test_project_build.py`
- `rtk uv run paradev build demos/assets/projects/minimal --emit-artifacts --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Default CLI builds discover modules but still emit zero artifacts until project/game profiles register emitting families and writers.
- Existing local desktop and README edits remain outside this project-emission slice.

## Next

- Add a minimal game/profile registry path so a project can request a profile and receive default families/writers without passing a registry from Python.
