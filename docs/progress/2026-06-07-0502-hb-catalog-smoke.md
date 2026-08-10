# HeavenBase Catalog Smoke Progress

Date: 2026-06-07 05:02 CST

Linear: unavailable; no Linear connector was exposed and `linear` is not on PATH.

## Done

- Added `catalog_smoke(...)` to validate catalog preview rows inside a real in-memory HeavenBase workspace.
- Registered one `paradev-*` schema entity per preview row group and upserted every preview row through HeavenBase.
- Added `paradev hb catalog-smoke <path> --json` with row counts, Catalog counts, MetaSchema entity count, and an `ok` flag.
- Updated the HeavenBase architecture and build-flow docs with the smoke command.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_hb.py -q` failed because `catalog_smoke` was missing.
- Focused green: `rtk bash scripts/test.bash tests/test_hb.py -q`
- CLI smoke: `rtk uv run paradev hb catalog-smoke demos/assets/projects/minimal --json`
- Related: `rtk bash scripts/test.bash tests/test_hb.py tests/test_cli.py tests/test_architecture.py tests/test_project.py tests/test_build_manifest.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/hb/__init__.py src/paradev/cli.py tests/test_hb.py`

## Risks Or Blockers

- The smoke path uses in-memory HeavenBase only; the durable SQLite catalog write surface remains future work.
- Linear status could not be updated from this environment.

## Next

- Add a guarded SQLite `catalog-write` path that refuses to overwrite existing `.paradev/hb` database files.
- Keep the preview and smoke payloads as the shared source for future MCP and desktop catalog inspection.
