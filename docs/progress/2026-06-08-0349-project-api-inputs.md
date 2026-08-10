# Project Frontend API Inputs

Date: 2026-06-08 03:49 CST

Issues: TAL-299, TAL-295

Linear comments:

- TAL-299: `8b295db1-b872-45fb-872e-9ae676c0af11`
- TAL-295: `f6bf8134-8ee1-448d-a3e1-96f1cf017aba`

## Summary

- Added canonical `inputs` metadata to project-management frontend API rows so GUI, importer, and PIHC3-facing code can build forms/actions from the SDK contract instead of copying CLI or OpenAPI parameter names.
- Covered `project.create`, `project.find`, `project.open`, `project.view`, `project.rename`, and frontend-local `project.activate` with stable field names, primitive types, required flags, and defaults.
- Updated the English and Chinese frontend API manual, SDK manual, developer manual, and architecture interface contract to describe the `inputs` convention.

## Verification

- Red test: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations -q` failed on missing `project.create["inputs"]`.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations -q` passed.
- Lookup coverage: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_lookup_helpers_return_canonical_rows -q` passed.
- SDK probe: `rtk uv run python - <<'PY' ... get_frontend_api_operation(...) ... PY` confirmed project operation inputs from the public SDK.
- Docs/source check: `rtk rg -n 'Project-management rows|project 管理相关行|project_create_inputs|_input\("path"|_input\("title"|stable `inputs`' src/paradev/sdk/frontend_api.py tests/test_architecture.py docs/user-manual docs/architecture/interfaces.md`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py tests/test_architecture.py`
- Formatting: `rtk bash scripts/flake.bash --ci`
- Full tests: `rtk bash scripts/test.bash` (`443 passed`)
- Package build: `rtk uv build`

## Review

- The API list remains frontend-facing and canonical: operation metadata is still generated from `src/paradev/sdk/frontend_api.py`, while the manuals explain how GUI code consumes it.
- The new `inputs` rows are intentionally limited to stable project actions first; module, PDX, LSP, build, and diagnostics rows keep their existing contracts until each surface has concrete form/action semantics.
- No REST optional-extra runtime dependency was introduced; this stays compatible with the current SDK/static contract workflow.
