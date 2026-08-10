# 2026-06-15 11:24 Nested index helper

## Scope

- Added a generic typed nested-index append helper in `src/paradev/_api_table.py`.
- Reused it in `src/paradev/build/manifest.py` for deterministic manifest `outer -> inner -> row indexes` maps.
- Kept manifest payload schemas, keys, row ordering, and filtered inspection behavior unchanged.
- Avoided dirty PIHC3 migration paths and desktop files owned by parallel workers.

## Verification

- `rtk uv run python - <<'PY' ...` compared full `manifest_payloads(...)` output against `HEAD` for the minimal demo project.
- `rtk bash scripts/test.bash tests/test_api_table.py tests/test_build_manifest.py -q`
- `rtk uv run python -m py_compile src/paradev/_api_table.py src/paradev/build/manifest.py tests/test_api_table.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/_api_table.py src/paradev/build/manifest.py tests/test_api_table.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/_api_table.py src/paradev/build/manifest.py tests/test_api_table.py`
- `rtk git diff --check -- src/paradev/_api_table.py src/paradev/build/manifest.py tests/test_api_table.py docs/progress/2026-06-15-1124-nested-index-helper.md`

## Notes

- Full-suite tests remain deferred to reduce CPU usage while other workers are active.
