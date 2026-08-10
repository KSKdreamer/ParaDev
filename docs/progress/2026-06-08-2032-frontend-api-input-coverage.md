# Frontend API Input Coverage

Date: 2026-06-08 20:32 CST

Issues: TAL-299, TAL-295

Linear comments: TAL-299 `4cc26f2f-4f9a-45de-80be-42030f113fb0`, TAL-295 `325a5b7c-800f-431f-914c-cd3c2fd6fde2`

## Summary

This slice tightens the canonical frontend API list after the source-bridge rows landed. The contract now makes every REST-backed frontend operation explicit about its input shape: rows either publish concrete input fields or intentionally publish an empty `inputs` list.

The generic `project.inspect` row now exposes `path` and SDK inspection `kind` as derived form fields. `kind` uses choices from `get_project_inspection_contract()`, so dispatcher clients can plan `GET /projects/inspect` without copying the inspection kind vocabulary. Detailed filter forms remain on concrete rows such as `module.list`, `build.graph`, `build.diagnostics`, and `catalog.query`; the generic dispatcher row does not become a second filter registry.

Form-less meta routes, currently `surface.frontend_api.workspace` and `surface.architecture`, now publish `inputs=[]`. That lets generated clients and maintenance audits distinguish "this route needs no values" from "this route is missing input metadata."

## Files Changed

- Updated `src/paradev/sdk/frontend_api.py` with SDK-derived inspection-kind choices, `project.inspect` inputs, intentional empty input lists for no-value REST meta rows, and `_op(..., inputs=[])` preservation.
- Updated `tests/test_architecture.py` to assert `project.inspect` input metadata and guard that no REST-backed frontend row omits the `inputs` key.
- Regenerated `apps/desktop/src/generated/frontendApi.ts` and `docs/user-manual/frontend-api-reference.md`.
- Updated English/Chinese frontend API, developer, and architecture docs to document the generic dispatcher boundary.

## Verification

- `rtk python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/test.bash tests/test_architecture.py tests/test_cli.py -q` -> 86 passed, 3 skipped because optional `fastapi.testclient` is absent.
- `rtk npm --prefix apps/desktop run test:unit` -> 7 files passed, 31 tests passed.
- `rtk uv run paradev frontend-api --operation project.inspect --form --json`
- `rtk uv run paradev frontend-api --operation project.inspect --values-json '{"path":"demos/assets/projects/minimal","kind":"modules"}' --rest-request --json`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py` -> no banned imports.
- `rtk bash scripts/flake.bash --ci` -> 55 files would be left unchanged.
- `rtk git diff --check`
- Contract probe: `rest_without_inputs []`, `empty_input_rows ['surface.frontend_api.workspace', 'surface.architecture']`.

## Review Notes

- `project.inspect.kind` choices are derived from the SDK inspection contract rather than duplicated by hand.
- `surface.frontend_api.workspace` and `surface.architecture` remain no-form actions because empty `inputs` does not set workspace `form=true`.
- The default environment still skips FastAPI endpoint smokes when `fastapi.testclient` is not installed; helper and contract coverage passed.
