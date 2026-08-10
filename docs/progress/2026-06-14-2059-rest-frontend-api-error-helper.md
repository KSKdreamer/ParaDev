# REST Frontend API Error Helper

Date: 2026-06-14 20:59 Asia/Shanghai

## Summary

- Added one local FastAPI helper for frontend API `ValueError` to HTTP 400 shaping.
- Reused it across frontend API contract, action, normalize, rest-request, options, and binding routes.
- Preserved route paths, request bodies, status codes, error detail text, and SDK payload behavior.

## Verification

- `rtk uv run python -m py_compile src/paradev/surfaces/rest.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/surfaces/rest.py`
- `rtk bash scripts/flake.bash --all --paths src/paradev/surfaces/rest.py`
- Targeted frontend API REST route tests for options, action detail, binding lookup, and REST request planning.
- Direct FastAPI probe for valid binding lookup and invalid binding-surface 400 detail.

## Notes

- This is a behavior-preserving maintainability refactor inside the GUI-facing REST frontend API route boundary.
- Full-suite tests are intentionally skipped to reduce CPU contention while PIHC3 migration work continues in parallel.
