# Source Missing Diagnostics Progress

Date: 2026-06-07 13:09

Linear: TAL-294

## Done

- Added regression coverage for missing matched PDX and localization source files.
- Converted missing PDX source reads into `pdx.missing_source` diagnostics.
- Converted missing localization source reads into `loc.missing_source` diagnostics.
- Documented the missing-source diagnostic behavior in `docs/workflows/build-flow.md`.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_build_loaders.py::test_pdx_loader_reports_missing_source_as_diagnostic tests/test_localization_loader.py::test_loc_loader_reports_missing_source_as_diagnostic -q` failed with raw `FileNotFoundError` exceptions.
- Green: `rtk bash scripts/test.bash tests/test_build_loaders.py::test_pdx_loader_reports_missing_source_as_diagnostic tests/test_localization_loader.py::test_loc_loader_reports_missing_source_as_diagnostic -q` passed.
- Related loader path: `rtk bash scripts/test.bash tests/test_build_loaders.py tests/test_localization_loader.py tests/test_module_sources.py tests/test_project_build.py tests/test_simple_source_family.py -q` passed, `114 passed`.
- Style: `rtk git diff --check` passed.
- Style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/loaders.py tests/test_build_loaders.py tests/test_localization_loader.py` passed, `OK: 3 file(s) - no banned imports`.
- Style: `rtk bash scripts/flake.bash --ci` passed, `46 files would be left unchanged`.
- Full: `rtk bash scripts/test.bash` passed, `296 passed`.

## Risks Or Blockers

- Linear sync is blocked by expired auth: fetching `issue:TAL-294` returned `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Next

- Continue hardening source-slot loaders and artifact writers against author-facing source errors.
