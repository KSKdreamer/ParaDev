# Frontend API Input Normalizer Helpers

Date: 2026-06-14 18:48 Asia/Shanghai

## Summary

- Split `normalize_frontend_api_inputs` into focused private helpers for form field extraction, unknown input rejection, bucket initialization, field value/default handling, normalized bucket insertion, and final payload assembly.
- Kept the public normalizer schema, bucket names, alias handling, validation calls, and error messages unchanged.
- Left generated frontend API Markdown and TypeScript contracts behavior-preserving.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API normalizer, REST planner, renderer parity, and CLI tests.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a maintainability-only refactor scoped to SDK-owned frontend form normalization.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
