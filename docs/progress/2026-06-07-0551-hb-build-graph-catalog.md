# HeavenBase Build Graph Catalog Progress

Date: 2026-06-07 05:51 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added `build-graph-node` and `build-graph-edge` rows to `catalog_preview(...)`.
- Carried graph rows through `catalog_smoke(...)`, `catalog_write(...)`, `catalog_refresh(...)`, and `catalog_query(...)` using the existing generic `paradev-*` entity path.
- Tagged graph edges by kind, source, and target so persisted catalog queries can find relationships such as `--entity build-graph-edge --tag requires`.
- Updated the HeavenBase architecture and build workflow docs to show graph rows as part of the catalog bridge.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_hb.py -q` failed because graph node and edge catalog rows were missing.
- Focused green: `rtk bash scripts/test.bash tests/test_hb.py -q`
- CLI smoke: `rtk zsh -lc 'tmp="$(mktemp -d)"; cp -R demos/assets/projects/minimal "$tmp/minimal"; rtk uv run paradev hb catalog-write "$tmp/minimal" --json >/dev/null; rtk uv run paradev hb catalog-query "$tmp/minimal" --entity build-graph-edge --tag requires --json'`
- Related: `rtk bash scripts/test.bash tests/test_hb.py tests/test_project.py tests/test_build_manifest.py tests/test_build_records.py tests/test_cli.py tests/test_architecture.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/hb/__init__.py tests/test_hb.py`

## Review

- Graph catalog rows reuse `paradev.build.graph.v1` node and edge payload shapes instead of adding a second graph model.
- The existing catalog write, refresh, smoke, and query paths handle the new entity groups without a new storage API.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- The graph rows are stored as generic preview-backed HeavenBase entities; typed graph schema entities can follow once query needs are clearer.
- Linear status could not be updated from this environment.

## Next

- Add graph-aware diagnostics/explainability over the generic module compilation flow.
- Consider a typed graph query surface after real UI/MCP usage shows which graph traversal questions matter most.
