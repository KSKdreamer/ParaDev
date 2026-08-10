# PIHC3 Superevent Template Progress

Date: 2026-06-08 16:52 CST

Linear: TAL-298

## Done

- Added the PIHC3 `superevent` simple-source family and `pihc3:superevent/basic` starter template.
- Added SDK coverage for family shorthand creation, primary create fields, exact emitted source files, localization, and build artifacts.
- Updated the PIHC3 user manual, legacy superevent evidence, entity catalog, and project migration note with current starter scope and unfinished parity work.

## Verification

- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`
- `rtk uv run python - <<'PY' ... Project.load('projects/PIHC3').build().summary() ...`
- `rtk uv run paradev diagnostics projects/PIHC3 --json`
- `rtk git diff --check`
- `rtk git -C projects/PIHC3 diff --check`

## Risks Or Blockers

- This is only an authored starter shell for a hidden `SUPER.*` country event, paired `SUPER_NEWS.*` news event, and localization contract.
- PIHC2 superevent import, aggregate `SUPER.txt`/`SUPER_NEWS.txt` emission, GUI/scripted-localisation assembly, event/news image DDS and sprite generation, music asset wiring, close-button behavior, and multi-language parity remain unfinished.
- Existing generated PIHC3 superevent artifacts still come from the current migration/copy pipeline, not from standard `src/modules/superevent` sources.

## Next

- Continue adding starter templates for missing high-value legacy families, or prioritize full PIHC2 superevent importer work when superevent parity becomes the active slice.
