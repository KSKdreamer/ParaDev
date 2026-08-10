# Focus Tree View Artifact Progress

Date: 2026-06-06 20:52 CST

Linear: TAL-293

## Done

- Added optional focus collection `view_path_template` support.
- Planned a collection-owned `focus-tree.view.v1` artifact with deterministic node order.
- Included focus ids, module ids, source paths, source spans, and project-local prerequisites in view metadata.
- Kept the default HOI4 scaffold output unchanged by leaving the view template opt-in.

## Verification

- `rtk bash scripts/test.bash tests/test_simple_source_family.py -q`
- `rtk bash scripts/test.bash tests/test_simple_source_family.py tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py tests/test_sdk_examples.py tests/test_build_records.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py tests/test_simple_source_family.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- The view artifact has no writer yet; it is currently a dry-plan/manifest payload for SDK and future UI consumers.
- Existing local desktop and README edits remain outside this focus-tree view slice.

## Next

- Add a JSON/view artifact writer or enable the view artifact in the HOI4 scaffold once writer behavior is explicit.
