# 2026-06-15 11:05 Build registry index helper

## Scope

- Reused the shared typed index append helper inside `src/paradev/build/registry.py` for build registry API index buckets.
- Kept `Project.families(...)` and the registry contract indexes behavior unchanged.
- Avoided dirty PIHC3 migration paths and desktop files owned by parallel workers.

## Verification

- `rtk uv run python - <<'PY' ...` compared registry indexes against `HEAD` for default, family/source-slot, kind/source-slot, route, and artifact-type family payloads.
- `rtk bash scripts/test.bash tests/test_project.py::test_project_families_returns_profile_family_contracts tests/test_project.py::test_project_families_filters_profile_family_contracts -q`
- `rtk uv run python -m py_compile src/paradev/build/registry.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/build/registry.py`
- `rtk git diff --check -- src/paradev/build/registry.py docs/progress/2026-06-15-1105-build-registry-index-helper.md`

## Notes

- Full-suite tests remain deferred to reduce CPU usage while other workers are active.
