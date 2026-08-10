# Demo Localization Fixture Progress

Date: 2026-06-06 19:35 CST

Linear: TAL-294

## Done

- Added `main.loc` to the minimal demo focus module.
- Added CLI coverage proving the demo project now reports both PDX and localization source slots.
- Verified the default HOI4 scaffold profile plans both `common/national_focus/GER_sample.txt` and `localisation/english/GER_sample_l_english.yml`.
- Kept the build path as dry-run by default for the CLI mental model.

## Verification

- `rtk uv run pytest tests/test_project.py -q`
- `rtk uv run pytest tests/test_project.py tests/test_project_build.py tests/test_localization_loader.py tests/test_simple_source_family.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_project.py`
- `rtk uv run paradev build demos/assets/projects/minimal --json`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this demo-fixture slice.

## Next

- Add CLI coverage for `--emit-artifacts` on the demo project and verify the generated PDX and localization files without committing generated outputs.
