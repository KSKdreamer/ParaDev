# REST Source Read Progress

Date: 2026-06-08 11:20 CST

Linear: TAL-298, TAL-297

## Done

- Added `read_project_source(...)` to the REST surface for reading one project-contained source file as UTF-8 text.
- Added `GET /projects/{project_id}/sources?path=...` to the OpenAPI seed and optional FastAPI app.
- Exported `read_project_source` from `paradev.api`.
- Added containment coverage so REST rejects source paths outside the loaded project root.
- Updated the surface architecture doc to mark source read as the first implemented read route.

## Verification

- Red check: source-read tests failed first because the OpenAPI path and `read_project_source` helper did not exist.
- `rtk bash scripts/test.bash tests/test_architecture.py -q`: 6 passed, 1 skipped because `fastapi.testclient` is not installed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py src/paradev/api/__init__.py tests/test_architecture.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/rest.py src/paradev/api/__init__.py tests/test_architecture.py`: passed.
- PIHC3 REST probe via `read_project_source(...)`: returned `paradev.rest.source_text.v1`, a `src/modules/.../def.pdx` relative path, and source text containing `IDEA`.
- `rtk uv run paradev build projects/PIHC3 --emit-manifests --json`: 529 modules, 26892 artifacts, 0 diagnostics, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.

## Risks Or Blockers

- `fastapi.testclient` remains absent in the default environment, so the optional FastAPI endpoint path is covered by OpenAPI/helper tests but not by an endpoint integration test here.
- Text edit apply, removal drafts, and image replacement still need REST/OpenAPI mutation routes.

## Next

- Continue toward REST/OpenAPI apply for source-slot edits, removals, and assets.
