# PIHC3 Achievement Template Progress

Date: 2026-06-08 16:26 CST

Linear: TAL-298

## Done

- Added the PIHC3 `achievement` simple-source family and `pihc3:achievement/basic` starter template.
- Added SDK coverage for family shorthand creation, primary create fields, exact emitted source files, localization, and build artifacts.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/40-achievements.md` with current legacy evidence and unfinished achievement parity work.

## Verification

- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`
- SDK and desktop template projections for `pihc3:achievement/basic`
- `rtk uv run python - <<'PY' ... Project.load('projects/PIHC3').build().summary() ...`
- `rtk uv run paradev diagnostics projects/PIHC3 --json`
- `rtk git diff --check`
- `rtk git -C projects/PIHC3 diff --check`

## Risks Or Blockers

- This is only an authored starter shell. PIHC2 achievement import, staged `src/achievements` conversion, aggregated custom achievement pack emission, icon DDS/grey/not-eligible generation, interface achievement ribbon work, and multi-language parity remain unfinished.
- The existing PIHC3 achievement migration script writes legacy-shaped `def.txt` folders outside `src/modules`, so it is not yet connected to the standard module discovery path.

## Next

- Continue adding starter templates for missing high-value legacy families, or prioritize converting staged achievement folders into standard `src/modules/achievement` sources when achievement parity becomes the active slice.
