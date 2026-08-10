# Source Loaders Progress

Date: 2026-06-06 18:55 CST

Linear: TAL-294

## Done

- Added `load_metadata(...)` for `meta.yaml` plus inferred folder identity (`object_id` and optional note).
- Preserved the active metadata model: `type`, optional `game_id`, `collection`, `owner`, `priority`, tags, settings, and dependency fields.
- Added type-mismatch and unknown-key metadata diagnostics.
- Added `load_pdx_sources(...)` using `PDXBlock.from_file`, preserving file extension annotations and converting parser failures into build diagnostics.

## Verification

- `rtk uv run pytest tests/test_build_loaders.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build tests/test_build_loaders.py`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this source-loader slice.

## Next

- Add localization `.loc` loader and static copy records/hash metadata.
