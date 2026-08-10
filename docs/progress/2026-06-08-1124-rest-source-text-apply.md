# REST Source Text Apply Progress

Date: 2026-06-08 11:24 CST

Linear: TAL-298, TAL-297

## Done

- Added `apply_project_draft(...)` to the REST surface for applying validated source-text edits.
- Added `POST /projects/{project_id}/drafts/apply` to the OpenAPI seed and optional FastAPI app.
- Exported `apply_project_draft` from `paradev.api`.
- Validated every source edit target before writing, so outside-project paths fail before any source text is applied.
- Updated the surface architecture doc to record source-text apply as the first implemented apply route.

## Verification

- Red check: apply tests failed first because the OpenAPI path and `apply_project_draft` helper did not exist.
- `rtk bash scripts/test.bash tests/test_architecture.py -q`: 8 passed, 1 skipped because `fastapi.testclient` is not installed.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py src/paradev/api/__init__.py tests/test_architecture.py`: passed.
- `rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/rest.py src/paradev/api/__init__.py tests/test_architecture.py`: passed.
- Temporary project REST probe: `apply_project_draft(...)` returned `paradev.rest.draft_apply.v1`, wrote `src/modules/idea/IDEA_REST_APPLY_PROBE/main.loc`, and `read_project_source(...)` read back the edited text.
- `rtk uv run paradev build projects/PIHC3 --emit-manifests --json`: 529 modules, 26892 artifacts, 0 diagnostics, not blocked.
- `rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json`: 0 diagnostics.

## Risks Or Blockers

- `fastapi.testclient` remains absent in the default environment, so the optional FastAPI endpoint path is covered by OpenAPI/helper tests but not by an endpoint integration test here.
- Asset replacement, deletion, and a separate draft validation route remain future REST slices.

## Next

- Wire REST source-text apply into the desktop module editor when the local REST service path is available, or continue with REST asset/remove routes first if backend route coverage is the priority.
