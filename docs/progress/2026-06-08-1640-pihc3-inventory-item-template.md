# PIHC3 Inventory Item Template Progress

Date: 2026-06-08 16:40 CST

Linear: TAL-298

## Done

- Added the PIHC3 `inventory_item` simple-source family and `pihc3:inventory_item/basic` starter template.
- Added SDK coverage for family shorthand creation, primary create fields, exact emitted source files, localization, and build artifacts.
- Updated the PIHC3 user manual, legacy inventory evidence, domain catalog, and project migration note with current inventory scope and unfinished parity work.

## Verification

- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`
- `rtk uv run python - <<'PY' ... Project.load('projects/PIHC3').build().summary() ...`
- `rtk uv run paradev diagnostics projects/PIHC3 --json`
- `rtk git diff --check`
- `rtk git -C projects/PIHC3 diff --check`

## Risks Or Blockers

- This is only an authored starter shell for the scripted-effect helper and localization contract.
- PIHC2 inventory item import, scripted trigger emission, `PIHC_INVENTORY` scan/debug aggregation, scripted GUI/interface assembly, operation button handling, icon DDS/sprite generation, scripted localisation selectors, and multi-language parity remain unfinished.
- Existing generated PIHC3 inventory artifacts are still coming from the current migration/copy pipeline, not from standard `src/modules/inventory_item` sources.

## Next

- Continue adding starter templates for missing high-value legacy families, or prioritize the full PIHC2 inventory importer when inventory parity becomes the active slice.
