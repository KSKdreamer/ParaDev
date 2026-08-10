# 2026-06-20 05:23 - Architecture API CLI Selectors

## Slice

- Added `--symbol` and `--index/--key` selectors to `paradev architecture --api-table`.
- Updated the CLI contract table so `architecture --api-table` maps to `get_architecture_api_selection`.
- Documented the selector path in `docs/architecture/interfaces.md`.
- Regenerated the CLI API reference from a clean staged-index checkout.

## Verification

- `rtk uv run pytest -q tests/test_architecture_api_cli_selectors.py tests/test_cli_api_reference_selectors.py`
- Full-suite verification was intentionally skipped to reduce CPU usage while PIHC3 workers continue their migration slices.
