# Project Discovery Progress

Date: 2026-06-06 18:40 CST

Linear: TAL-292

## Done

- Added a strict `Project.load(path)` contract that discovers `paradev.yaml` from a root or nested path.
- Loaded the first manifest schema: `project_id`, `title`, `game`, `source_roots`, `output_root`, and `build_root`.
- Exposed JSON-safe project views through the SDK, `paradev.project`, and `paradev project <path> --json`.
- Added a minimal demo project under `demos/assets/projects/minimal/`.
- Documented the manifest schema in `docs/resources/05-project-manifest.md` and linked it from the docs menu.

## Verification

- `rtk uv run pytest tests/test_project.py tests/test_architecture.py::test_project_view_is_sdk_owned -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/project.py src/paradev/sdk/__init__.py src/paradev/project/__init__.py src/paradev/__init__.py src/paradev/cli.py tests/test_project.py tests/test_architecture.py`
- `rtk uv run paradev project demos/assets/projects/minimal --json`
- `rtk uv run paradev project demos/assets/projects/minimal/src/modules/focus/GER_sample/def.pdx --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this project-discovery slice.

## Next

- Start TAL-293 build records: `Module`, `Collection`, `Artifact`, `Diagnostic`, `BuildResult`, dry-run planning, and manifest collision diagnostics.
