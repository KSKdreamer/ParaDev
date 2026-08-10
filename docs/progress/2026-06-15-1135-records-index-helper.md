# 2026-06-15 11:35 Records index helper

## Scope

- Reused the shared typed index helper for derived collection grouping in `src/paradev/build/records.py`.
- Kept `BuildResult.plan`, `module_collections`, and JSON view behavior unchanged.
- Left unrelated desktop, skill, PIHC3, localization, and logo worktree edits untouched.

## Verification

- Focused `module_collections` and `BuildResult.plan` comparison against `HEAD` passed for derived, explicit-merge, and plan cases.
- `rtk bash scripts/test.bash tests/test_build_records.py -q`
- `rtk uv run python -m py_compile src/paradev/build/records.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/records.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/build/records.py`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only `src/paradev/build/records.py` and this note.
- Do not stage `node_modules/`.
