# Localization YAML Diagnostics Progress

Date: 2026-06-07 12:53

Linear: TAL-294

## Done

- Added regression coverage for malformed localization YAML in `load_loc_sources(...)`.
- Converted YAML parser failures into `loc.invalid_yaml` diagnostics anchored to the source slot and path.
- Kept existing localization shape diagnostics for valid YAML with invalid file, language, or entry structure.
- Documented the localization YAML diagnostic behavior in `docs/workflows/build-flow.md`.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_localization_loader.py::test_loc_loader_reports_malformed_yaml_as_diagnostic -q` failed with a raw `yaml.parser.ParserError`.
- Green: `rtk bash scripts/test.bash tests/test_localization_loader.py::test_loc_loader_reports_malformed_yaml_as_diagnostic -q` passed.
- Localization suite: `rtk bash scripts/test.bash tests/test_localization_loader.py -q` passed, `6 passed`.
- Related loader path: `rtk bash scripts/test.bash tests/test_localization_loader.py tests/test_build_loaders.py tests/test_module_sources.py tests/test_project_build.py tests/test_simple_source_family.py -q` passed, `110 passed`.
- Style: `rtk git diff --check` passed.
- Style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/loaders.py tests/test_localization_loader.py` passed, `OK: 2 file(s) - no banned imports`.
- Style: `rtk bash scripts/flake.bash --ci` passed, `46 files would be left unchanged`.
- Full: `rtk bash scripts/test.bash` passed, `292 passed`.

## Risks Or Blockers

- Linear sync is blocked by expired auth: fetching `issue:TAL-294` returned `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Next

- Continue hardening generic loader diagnostics for author-facing source errors.
