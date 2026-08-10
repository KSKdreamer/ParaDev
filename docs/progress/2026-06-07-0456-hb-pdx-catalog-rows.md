# HeavenBase PDX Catalog Rows Progress

Date: 2026-06-07 04:56 CST

Linear: unavailable; no Linear connector was exposed and `linear` is not on PATH.

## Done

- Extended the read-only HeavenBase catalog preview with `pdx-document` rows for parsed PDX sources.
- Added `pdx-symbol` rows for keyed PDX entries with key path, source span, kind, and scalar values where available.
- Kept rows derived from existing build loader payloads, so preview generation does not reparse files or write a workspace database.
- Updated the catalog preview docs with the new PDX row groups.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_hb.py -q` failed because `pdx-document` and `pdx-symbol` rows were absent.
- Focused green: `rtk bash scripts/test.bash tests/test_hb.py -q`
- Related: `rtk bash scripts/test.bash tests/test_hb.py tests/test_cli.py tests/test_pdx_roundtrip.py tests/test_pdx_token.py tests/test_build_manifest.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/hb/__init__.py tests/test_hb.py`
- CLI smoke: `rtk uv run paradev hb catalog-preview demos/assets/projects/minimal --json`

## Risks Or Blockers

- PDX symbols are structural parser rows only; `pdx-reference` rows remain a later semantic indexing slice.
- Linear status could not be updated from this environment.

## Next

- Add an in-memory catalog smoke path once the HeavenBase schema-pack boundary is ready.
- Expand PDX catalog references from known dependency shapes after the parser and source graph expose enough semantic context.
