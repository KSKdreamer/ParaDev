# SDK Selector Facade Progress

Date: 2026-06-20 04:45 +0800

Linear: N/A

## Done

- Exposed `get_sdk_api_selection` through the top-level `paradev.sdk` facade and `__all__`.
- Added a focused facade-export assertion to `tests/test_sdk_api_selection.py`.
- Staged a sanitized `docs/user-manual/sdk-api-reference.md` update that documents `get_sdk_api_selection` and refreshes previously shipped selector row counts, while leaving unrelated `MODULE_BATCH_EDIT_SCHEMA` doc rows unstaged.

## Verification

- Red: `rtk uv run pytest -q tests/test_sdk_api_selection.py` failed because `get_sdk_api_selection` was missing from `paradev.sdk.__all__`.
- Green: `rtk uv run pytest -q tests/test_sdk_api_selection.py tests/test_api_table_contracts.py` passed with 4 tests.

## Risks Or Blockers

- The working tree still contains unrelated `MODULE_BATCH_EDIT_SCHEMA` changes in `src/paradev/sdk/__init__.py` and generated SDK docs; this slice stages only selector-related hunks.
- Skipped the full suite to keep CPU available for concurrent PIHC2/PIHC3 migration work.

## Next

- Let the `module-batch-edit` owner land or clear their SDK facade/reference changes, then rerun the generated-reference parity checks across SDK, Project, and CLI API references.
