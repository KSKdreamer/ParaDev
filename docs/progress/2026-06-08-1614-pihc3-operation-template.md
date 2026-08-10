# PIHC3 Operation Template Progress

Date: 2026-06-08 16:14 CST

Linear: TAL-298

## Done

- Added the PIHC3 `operation` simple-source family and `pihc3:operation/basic` starter template.
- Added SDK coverage for family shorthand creation, primary create fields, exact emitted source files, localization, and build artifacts.
- Updated the PIHC3 user manual and added `projects/PIHC3/docs/migration/39-operations.md` with current evidence and unfinished operation parity work.

## Verification

- `rtk bash scripts/test.bash tests/test_sdk_examples.py -q`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py`
- `rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py`
- SDK and desktop template projections for `pihc3:operation/basic`
- `rtk uv run python - <<'PY' ... Project.load('projects/PIHC3').build().summary() ...`
- `rtk uv run paradev diagnostics projects/PIHC3 --json`

## Risks Or Blockers

- This is only an authored starter shell. PIHC2 operation import, full operation roster parity, token awarding, target selection, AI operation strategies, equipment costs, outcome effects, and multi-language parity remain unfinished.
- The current evidence uses vanilla operation files plus copied/compiled PIHC operation outputs; no dedicated operation generator was found in the available `HOI4DEV/demo/PIHC2` checkout during this slice.

## Next

- Continue converting high-value PIHC3 authored families or begin operation parity review once operation importer scope is prioritized.
