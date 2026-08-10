# Frontend API Input Normalizer Collection

Date: 2026-06-14 19:58 Asia/Shanghai

## Summary

- Split frontend input value collection out of `normalize_frontend_api_inputs`.
- Moved missing-required-input error construction into a private helper.
- Preserved normalized payload shape, default handling, alias bucket mapping, validation ordering, missing-input errors, and collision behavior.

## Verification

- `rtk uv run python -m py_compile src/paradev/sdk/frontend_api.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/sdk/frontend_api.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/sdk/frontend_api.py`
- Targeted frontend API input normalizer, REST planner, renderer parity, and CLI binding tests.
- Direct SDK probe for defaults, aliases, missing required fields, unknown inputs, and invalid choices.
- Renderer digest check for `render_frontend_api_reference_markdown`, `render_frontend_api_sdk_cli_markdown`, and `render_frontend_api_typescript`.

## Notes

- This is a maintainability-only refactor inside the SDK-owned frontend form normalization path.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
