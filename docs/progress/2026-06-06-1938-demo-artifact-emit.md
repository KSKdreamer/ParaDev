# Demo Artifact Emit Progress

Date: 2026-06-06 19:38 CST

Linear: TAL-294

## Done

- Added CLI coverage for `paradev build --emit-artifacts` using a temporary copy of the minimal demo project.
- Verified generated PDX output under `build/mod/common/national_focus/`.
- Verified generated localization output under `build/mod/localisation/english/`.
- Kept generated files out of the committed demo tree.

## Verification

- `rtk uv run pytest tests/test_project.py -q`
- `rtk uv run pytest tests/test_project.py tests/test_project_build.py tests/test_simple_source_family.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_project.py`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this demo-emission test slice.

## Next

- Add localization escaping/validation coverage for quotes and backslashes before broader HOI4 localization rules.
