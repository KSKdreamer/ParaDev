# Frontend API Input Normalizer

Date: 2026-06-08 04:34 CST

Issues: TAL-299, TAL-295

Linear comments:

- TAL-299: `f4131645-be1c-4930-b62e-a9ebbd6d513a`
- TAL-295: `fb9ac044-9f1a-45d4-9885-d5e1e248c9d3`

## Summary

- Added SDK-owned `normalize_frontend_api_inputs(operation_id, values)` with schema `paradev.sdk.frontend-api.inputs.v1`.
- Added field-level `target` buckets to derived frontend form fields: `project`, `parameters`, `selectors`, and `projections`.
- Preserved project path and action parameter separation for project-backed rows, especially `build.artifacts` where frontend `artifact_path` maps to `parameters.path` without overwriting project `path`.
- Exported `FRONTEND_API_INPUTS_SCHEMA` and `normalize_frontend_api_inputs(...)` from the public SDK.
- Updated the English and Chinese frontend API manual, SDK manual, developer manual, and architecture interface contract.

## Verification

- Red test: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_form_contract_is_derived_from_operation_inputs tests/test_architecture.py::test_frontend_api_input_normalizer_maps_form_values_to_adapter_buckets -q` failed on missing field `target` and missing `normalize_frontend_api_inputs`.
- Focused green: `rtk bash scripts/test.bash tests/test_architecture.py::test_frontend_api_contract_lists_canonical_operations tests/test_architecture.py::test_frontend_api_lookup_helpers_return_canonical_rows tests/test_architecture.py::test_frontend_api_form_contract_is_derived_from_operation_inputs tests/test_architecture.py::test_frontend_api_input_normalizer_maps_form_values_to_adapter_buckets -q` passed.
- SDK probe: `rtk uv run python - <<'PY' ... normalize_frontend_api_inputs(...) ... PY` confirmed module edit, build artifact, and frontend API selector/projection buckets.
- Docs/source check: `rtk rg -n 'normalize_frontend_api_inputs|FRONTEND_API_INPUTS_SCHEMA|target buckets|project.*parameters|artifact_path ->|parameters\.path|frontend-api.inputs|target"\]' src tests docs/user-manual docs/architecture/interfaces.md`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py src/paradev/sdk/__init__.py tests/test_architecture.py`
- Formatting: `rtk bash scripts/flake.bash --ci`
- Normalizer probe: `rtk uv run python - <<'PY' ... FRONTEND_API_INPUTS_SCHEMA ... PY`
- Full tests: `rtk bash scripts/test.bash` (`446 passed`)
- Package build: `rtk uv build`

## Review

- The normalizer is derived from the canonical operation form contract; it does not create a second API list.
- `path` remains explicit: project-backed rows put loaded workspace path in `project`, while aliased action filters such as `artifact_path` land in `parameters`.
- This is SDK metadata and adapter-preparation behavior only; it does not invoke project mutation, build execution, parser behavior, or catalog persistence.
