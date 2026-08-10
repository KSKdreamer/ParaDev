# 2026-06-15 11:17 Authoring view index helper

## Scope

- Reused the shared typed index append helper in `src/paradev/build/views.py` for authoring-plan slot grouping and row-index buckets.
- Kept `paradev.sdk.authoring_plan.v1` payloads and indexes unchanged.
- Avoided dirty PIHC3 migration paths and desktop files owned by parallel workers.

## Verification

- `rtk uv run python - <<'PY' ...` compared module and collection `authoring_plan_view(...)` payloads against `HEAD`.
- `rtk bash scripts/test.bash tests/test_authoring_views.py -q`
- `rtk uv run python -m py_compile src/paradev/build/views.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/views.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/build/views.py`
- `rtk git diff --check -- src/paradev/build/views.py docs/progress/2026-06-15-1117-authoring-view-index-helper.md`

## Notes

- Full-suite tests remain deferred to reduce CPU usage while other workers are active.
