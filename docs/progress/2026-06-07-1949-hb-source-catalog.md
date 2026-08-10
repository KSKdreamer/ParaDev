# 2026-06-07 19:49 - HeavenBase Source Catalog

## Scope

- Continued TAL-295 user/developer manual stabilization on `codex/scaffold-source-root-selection`.
- Kept the work generic: no PIHC3 migration behavior, no GUI-specific discovery path.
- Read TAL-295 from Linear. It remains `Continuous` and asks the manual to document public CLI/SDK workflows for HoI4 modders.

## Changes

- Changed HeavenBase `source-file` catalog preview rows to derive from the canonical `sources.json` manifest.
- Preserved the existing `source-file` entity name while adding richer source inventory fields: owner kind, root, relative path, loader, status, and loader-specific summaries.
- Added source catalog tags for searchable tool integrations, including `module:<id>`, `collection:<id>`, `family:<family>`, `slot:<slot>`, `loader:<loader>`, and `status:<status>`.
- Updated the bilingual user manual with CLI and SDK examples for querying PDX sources from the local catalog.
- Updated the developer manual and build-flow contract so future loaders extend `sources.json` instead of creating a parallel catalog path.

## Verification

- Red first:
  `rtk bash scripts/test.bash tests/test_hb.py::test_hb_catalog_preview_projects_build_rows_without_writing tests/test_hb.py::test_hb_catalog_query_finds_sources_by_loader_tag -q`
  failed because catalog preview rows lacked source inventory metadata and `loader:pdx` matched zero rows.
- Focused green:
  `rtk bash scripts/test.bash tests/test_hb.py::test_hb_catalog_preview_projects_build_rows_without_writing tests/test_hb.py::test_hb_catalog_query_finds_sources_by_loader_tag -q`
  passed `2 passed`.
- Related suite:
  `rtk bash scripts/test.bash tests/test_hb.py -q`
  passed `17 passed`.
- CLI smoke:
  `rtk zsh -lc 'tmp="$(mktemp -d)"; cp -R demos/assets/projects/minimal "$tmp/minimal"; rtk uv run paradev hb catalog-refresh "$tmp/minimal" --json >/dev/null; rtk uv run paradev hb catalog-query "$tmp/minimal" --entity source-file --tag loader:pdx --json'`
  returned one `paradev-source-file` row with `loader:pdx`.
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

- This slice keeps the user mental model small: `paradev sources` shows compiler inputs directly; `paradev hb catalog-query --entity source-file` searches the same inputs after catalog refresh/write.
- The catalog tag vocabulary is additive, so existing module/family/slot tags remain valid while prefixed tags give adapters safer exact filters.

## Next

- Keep moving generic compiler surfaces toward one inspection contract: source inventory, source map, build graph, diagnostics, and catalog rows should remain different views of the same SDK-owned dry build.
- Continue manual coverage whenever a CLI or SDK behavior becomes public.
