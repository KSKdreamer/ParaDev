# Default Focus Tree View Progress

Date: 2026-06-06 21:08 CST

Linear: TAL-293

## Done

- Enabled default HOI4 focus collection view emission through the scaffold registry.
- Kept focus-tree view artifact paths build-root relative as `views/focus-tree/{collection_id}.json`.
- Updated SDK, CLI, writer, and family tests for the three-artifact demo plan.
- Updated build-flow docs to explain game-output versus build-root view emission.

## Verification

- `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_game_profile_registry_when_registry_is_not_supplied -q`
- `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_sdk_examples.py tests/test_simple_source_family.py tests/test_artifact_writers.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/games/hoi4/__init__.py tests/test_project.py tests/test_project_build.py tests/test_sdk_examples.py tests/test_simple_source_family.py tests/test_artifact_writers.py`
- `rtk uv run paradev build demos/assets/projects/minimal --emit-artifacts --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Focus-tree view payloads are still structural planning data; layout coordinates and GUI writeback remain future slices.
- Existing local desktop and README edits remain outside this HOI4 scaffold slice.

## Next

- Add richer focus-tree view fields only after the next validation/layout contract is explicit.
