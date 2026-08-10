# HeavenBase Catalog Refresh Progress

Date: 2026-06-07 05:32 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added `catalog_refresh(...)` as the explicit replacement path for local SQLite HeavenBase catalogs.
- Added `paradev hb catalog-refresh <path> --json` with optional `--profile` and `--database`.
- Kept `catalog_write(...)` guarded: it still refuses existing `catalog.sqlite`, WAL, or SHM files.
- Implemented refresh as a staged write: build the replacement catalog at a sibling SQLite path, checkpoint it, then replace the final database.
- Returned the old database triplet paths that refresh replaced so the operation is reviewable.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_hb.py -q` failed because `catalog_refresh` was missing.
- Debug reproduction: stale invalid sidecar files previously crashed the process; the staged refresh now returns the refreshed catalog and `catalog_query(..., entity="pdx-symbol")` returns 3 rows.
- Focused green: `rtk bash scripts/test.bash tests/test_hb.py -q`
- CLI smoke: `rtk zsh -lc 'tmp="$(mktemp -d)"; cp -R demos/assets/projects/minimal "$tmp/minimal"; rtk uv run paradev hb catalog-write "$tmp/minimal" --json >/dev/null; rtk uv run paradev hb catalog-refresh "$tmp/minimal" --json >/dev/null; rtk uv run paradev hb catalog-query "$tmp/minimal" --entity pdx-symbol --json'`
- Related: `rtk bash scripts/test.bash tests/test_hb.py tests/test_cli.py tests/test_project.py tests/test_build_manifest.py tests/test_architecture.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/hb/__init__.py src/paradev/cli.py tests/test_hb.py`

## Review

- The refresh path computes the catalog preview before touching the existing database.
- The final database path is not reopened by HeavenBase during refresh; HeavenBase writes the staging file instead.
- The staging database is checkpointed before replacement so read-only `sqlite3` catalog queries can open the final file without requiring staging WAL files.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Direct typed row inspection still reads through the Catalog index only; typed entity table views can follow once schema-pack shape stabilizes.
- Linear status could not be updated from this environment.

## Next

- Use the persisted PDX symbol and build-artifact catalog as the bridge into the generic compilation graph slice.
- Add a small graph inspection surface before broad compiler changes so users can see source-to-artifact relationships without learning internal planner details.
