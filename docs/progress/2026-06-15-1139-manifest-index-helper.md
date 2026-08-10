# 2026-06-15 11:39 Manifest index helper

## Scope

- Reused existing typed index helpers in `src/paradev/build/manifest.py`.
- Kept build manifest schemas, payload keys, sorting, and source-map duplicate behavior unchanged.
- Left unrelated desktop, skill, PIHC3, localization, and logo worktree edits untouched.

## Verification

- Focused `manifest_payloads` comparison against `HEAD` passed for module diagnostics/source rows.
- Focused `_source_index` comparison against `HEAD` passed with non-empty module source rows.
- `rtk bash scripts/test.bash tests/test_build_manifest.py tests/test_api_table.py -q`
- `rtk uv run python -m py_compile src/paradev/build/manifest.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/manifest.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/build/manifest.py`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only `src/paradev/build/manifest.py` and this note.
- Do not stage `node_modules/`.
