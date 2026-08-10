# Localization And Copy Loader Progress

Date: 2026-06-06 19:00 CST

Linear: TAL-294

## Done

- Added deterministic localization loading for YAML-backed `.loc` source slots.
- Added localization diagnostics for invalid file, language, and entry shapes.
- Added static copy source records with relative output path, byte size, and SHA-256 metadata.
- Exported the new loader records and functions from `paradev.build`.
- Covered the slice with TDD-focused loader tests.

## Verification

- `rtk uv run pytest tests/test_localization_loader.py -q`
- `rtk uv run pytest tests/test_build_loaders.py tests/test_localization_loader.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build tests/test_localization_loader.py`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Existing local desktop and README edits remain outside this source-loader slice.

## Next

- Wire typed module compilers to consume metadata, PDX, localization, and copy loader records.
