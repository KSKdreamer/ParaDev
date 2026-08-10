# 2026-06-15 11:12 Build manifest index helper

## Scope

- Reused the shared typed index append helper in `src/paradev/build/manifest.py` for direct manifest row-index buckets.
- Kept build manifest schemas, payload keys, and filtered inspection behavior unchanged.
- Avoided dirty PIHC3 migration paths and desktop files owned by parallel workers.

## Verification

- `rtk uv run python - <<'PY' ...` compared full `manifest_payloads(...)` output against `HEAD` for the minimal demo project.
- `rtk bash scripts/test.bash tests/test_build_manifest.py -q`
- `rtk uv run python -m py_compile src/paradev/build/manifest.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/build/manifest.py`
- `rtk git diff --check -- src/paradev/build/manifest.py docs/progress/2026-06-15-1112-build-manifest-index-helper.md`

## Notes

- Full-suite tests remain deferred to reduce CPU usage while other workers are active.
