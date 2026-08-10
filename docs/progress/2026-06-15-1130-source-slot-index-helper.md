# 2026-06-15 11:30 Source-slot index helper

## Scope

- Reused the shared typed index helpers in `src/paradev/build/source_slots.py`.
- Kept the `paradev.build.source-slots.v1` payload schema, row sorting, and index ordering unchanged.
- Left unrelated PIHC3, desktop, localization, and skill worktree edits untouched.

## Verification

- Focused source-slot payload comparison against `HEAD` passed for module, status-filtered, and collection cases.
- `rtk bash scripts/test.bash tests/test_source_slot_status.py -q`
- `rtk uv run python -m py_compile src/paradev/build/source_slots.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/source_slots.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/build/source_slots.py`
- Full test suite deferred to reduce CPU while other migration workers are active.

## Git hygiene

- Stage only `src/paradev/build/source_slots.py` and this note.
- Do not stage `node_modules/`.
