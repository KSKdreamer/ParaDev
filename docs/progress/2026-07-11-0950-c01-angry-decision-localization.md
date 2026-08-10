# 2026-07-11 - C01 angry decision localization

## Summary

Audited the four decisions in Cozy Glow's anger system across the PIHC2 resource tree, the migrated PIHC3 project, the local compiled `PIHC_dev` mod, the current PIHC3 output, the compiled GitHub repository and its available history, and Workshop item `3154495198`. `DECISION_C01_ANGRY_ADD` and `DECISION_C01_ANGRY_DEL` have always had English and Simplified Chinese names; `DECISION_C01_ANGRY_EXP` and `DECISION_C01_ANGRY_PROD` have no surviving localization in any checked source.

Added reconstructed English and Simplified Chinese titles and descriptions based on the category description and decision effects. The broad anger-powered economic, ideological, and logistical boost is now `Harness the Fury` / `驾驭怒火`; the industrial surge, which is linked to the existing `Accelerated Production` idea, is now `Fury-Fueled Production` / `怒火驱动生产`. Updated module metadata and added a regression contract for both languages.

The identifier reported as `DECISION_ANGRY_C01_EXP` does not occur in the checked sources; the emitted game identifier is `DECISION_C01_ANGRY_EXP`.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_c01_angry_decisions_have_reconstructed_localized_titles -q`
- `rtk bash projects/PIHC3/compile.bash --plan-only --json` was attempted, but the current workspace is blocked before project loading by an unrelated HeavenBase config error: an interpolated object is being passed as the database dialect identifier.
- `rtk git diff --check && rtk git -C projects/PIHC3 diff --check`
