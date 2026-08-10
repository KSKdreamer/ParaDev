# HeavenBase Artifact Provenance Progress

Date: 2026-06-07 10:41

Linear: TAL-293 (read and write updates attempted; Linear connector returned `UNAUTHORIZED; Session expired. Please re-authenticate.`)

## Done

- Promoted build-artifact provenance into HeavenBase catalog preview rows with top-level `module_ids` and `collection_ids`.
- Added Catalog tags for list-valued provenance fields so written build artifacts can be queried by contributing module id or related collection id.
- Updated `docs/workflows/build-flow.md` with the provenance fields and `build-artifact` tag query example.

## Verification

- Red first: HB preview lacked `module_ids`, and a persisted `build-artifact` Catalog query by `focus/GER_sample` returned 0 rows.
- `rtk bash scripts/test.bash tests/test_hb.py::test_hb_catalog_preview_projects_build_rows_without_writing tests/test_hb.py::test_hb_catalog_query_finds_artifacts_by_module_tag -q` -> 2 passed.
- `rtk bash scripts/test.bash tests/test_hb.py -q` -> 16 passed.
- `rtk bash scripts/test.bash tests/test_hb.py tests/test_build_manifest.py tests/test_project.py tests/test_project_build.py -q` -> 170 passed.
- `rtk bash scripts/flake.bash --ci` -> passed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/hb/__init__.py tests/test_hb.py` -> passed.
- `rtk bash scripts/test.bash` -> 270 passed.

## Risks Or Blockers

- Linear OAuth is expired in this Codex session, so issue comments cannot be created until the app is re-authenticated.

## Next

- Continue carrying the same low-friction provenance model into build explanation and generic compiler catalog rows, so users can navigate from module to generated output across CLI, SDK, and HeavenBase-backed surfaces.
