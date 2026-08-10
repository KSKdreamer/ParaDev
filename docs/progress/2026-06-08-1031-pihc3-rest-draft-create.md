# PIHC3 REST Draft Create Progress

Date: 2026-06-08 10:31

Linear: TAL-297

## Done

- Added `POST /projects/{project_id}/modules/{family_id}/drafts` to the static OpenAPI seed.
- Added `create_module_draft(...)` as the SDK-backed REST helper and re-exported it from `paradev.api`.
- The helper resolves browser family ids such as `ideas` through the SDK browser payload before calling `Project.scaffold_module(...)`, so GUI clients do not need HoI4 family normalization logic.
- The helper returns a `paradev.rest.module_draft.v1` wrapper around the SDK scaffold plan with a stable `draft_id`.
- Added the optional FastAPI route. The endpoint test is present but skipped in the default environment because the optional `fastapi` extra is not installed.
- SDK scaffold plans now include resolved `values`, which lets REST, CLI, and GUI clients inspect rendered defaults such as `{family_tag}`.
- Updated REST architecture docs and the build-flow scaffold contract docs.

## Verification

```bash
rtk bash scripts/test.bash tests/test_architecture.py tests/test_project.py tests/test_sdk_examples.py tests/test_cli.py -q
rtk bash scripts/flake.bash --ci --paths src/paradev/surfaces/rest.py src/paradev/api/__init__.py src/paradev/sdk/templates.py tests/test_architecture.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py src/paradev/api/__init__.py src/paradev/sdk/templates.py tests/test_architecture.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json
```

Observed results:

- REST/OpenAPI/scaffold/CLI/example tests: 146 passed, 1 skipped for missing optional `fastapi.testclient`.
- Flake/format gate: 4 Python files unchanged after formatting.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26892`, `diagnostic_count: 0`, `error_count: 0`, `blocked: false`.
- Copy-root shadows: 0.

## Risks Or Blockers

- The default dev environment does not install the REST extra, so FastAPI endpoint execution is not covered unless `fastapi` is installed.
- Draft apply, slot patch, asset replacement, and deletion routes are still future work.

## Next

- Add frontend service wiring from `drafts.create` to the REST draft-create endpoint once the local REST process is available to the Tauri shell.
