# 2026-06-07 20:01 - HeavenBase Catalog Query Data

## Scope

- Continued generic HeavenBase catalog work on `codex/scaffold-source-root-selection`.
- Focused on the SDK/CLI surface that GUI, importer, and future MCP agents will consume after a catalog search hit.
- No PIHC3 migration behavior or GUI implementation was changed.

## Changes

- Added persisted Catalog row data hydration to `catalog_query(...)`.
- Each `paradev.hb.catalog-query.v1` row now includes `data`, the original preview row stored on the target entity.
- Kept dynamic SQL constrained to ParaDev's known `ENTITY_TYPES`; `paradev-source-file` maps to the persisted `paradev_source_file` table.
- Updated the bilingual user manual and build-flow docs to explain `rows[*].data`.

## Verification

- Red first:
  `rtk bash scripts/test.bash tests/test_hb.py::test_hb_catalog_query_finds_sources_by_loader_tag -q`
  failed with `KeyError: 'data'`.
- Focused green:
  `rtk bash scripts/test.bash tests/test_hb.py::test_hb_catalog_query_finds_sources_by_loader_tag -q`
  passed.
- Related suite:
  `rtk bash scripts/test.bash tests/test_hb.py -q`
  passed `17 passed`.
- CLI smoke:
  `rtk zsh -lc 'tmp="$(mktemp -d)"; cp -R demos/assets/projects/minimal "$tmp/minimal"; rtk uv run paradev hb catalog-refresh "$tmp/minimal" --json >/dev/null; rtk uv run paradev hb catalog-query "$tmp/minimal" --entity source-file --tag loader:pdx --json'`
  returned one `paradev-source-file` row with populated `data`.
- Heaven-style scan:
  `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/hb/__init__.py tests/test_hb.py`
  passed.
- Whitespace:
  `rtk git diff --check`
  passed.
- Lint:
  `rtk bash scripts/flake.bash --ci`
  passed.
- Full tests:
  `rtk bash scripts/test.bash`
  passed `365 passed`.
- Package build:
  `rtk uv build`
  built the sdist and wheel.
- Heaven-style review:
  Reviewed the final diff against the code-review checklist; no blocking findings.

## Notes

- This keeps the minimal user mental model: search the local catalog once, then render the returned row's `data` instead of making a second SDK discovery call.
- The same hydration path applies to artifacts, PDX documents, symbols, graph rows, diagnostics, assets, sprites, and project rows because every preview-backed entity uses the same `data` field.

## Next

- Continue aligning `sources`, `source-map`, `build-graph`, diagnostics, and catalog query results so external agents can build UI/import workflows without duplicating compiler logic.
