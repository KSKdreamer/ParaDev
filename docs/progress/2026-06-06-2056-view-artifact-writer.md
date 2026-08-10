# View Artifact Writer Progress

Date: 2026-06-06 20:56 CST

Linear: TAL-293

## Done

- Added a generic `JsonViewWriter` for `view` artifacts.
- Exported the writer through `paradev.build`.
- Registered the writer in the HOI4 scaffold registry without enabling default focus-tree view emission.
- Covered JSON view artifact writing and HOI4 registry exposure with tests.

## Verification

- `rtk bash scripts/test.bash tests/test_artifact_writers.py tests/test_project_build.py -q`
- `rtk bash scripts/test.bash tests/test_artifact_writers.py tests/test_project_build.py tests/test_simple_source_family.py tests/test_build_manifest.py tests/test_project.py tests/test_sdk_examples.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/artifacts.py src/paradev/build/__init__.py src/paradev/games/hoi4/__init__.py tests/test_artifact_writers.py tests/test_project_build.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- The default HOI4 profile registers the writer but still does not emit focus-tree view artifacts until the family opts into `view_path_template`.
- Existing local desktop and README edits remain outside this writer slice.

## Next

- Enable focus-tree view emission in the HOI4 scaffold or add CLI/manifest examples for explicit SDK opt-in.
