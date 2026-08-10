# Metadata YAML Diagnostics Progress

Date: 2026-06-07 13:01

Linear: TAL-294

## Done

- Added regression coverage for malformed module `meta.yaml` and collection descriptor metadata.
- Converted YAML parser failures into `metadata.invalid_yaml` and `collection_metadata.invalid_yaml` diagnostics.
- Preserved inferred module and collection identity when metadata cannot be parsed.
- Kept valid YAML with non-mapping metadata on the existing invalid-mapping diagnostic path.
- Documented the metadata YAML diagnostic behavior in `docs/workflows/build-flow.md`.

## Verification

- Red: `rtk bash scripts/test.bash tests/test_build_loaders.py::test_metadata_loader_reports_malformed_yaml_as_diagnostic tests/test_build_loaders.py::test_collection_metadata_loader_reports_malformed_yaml_as_diagnostic -q` failed with raw `yaml.parser.ParserError` exceptions.
- Green: `rtk bash scripts/test.bash tests/test_build_loaders.py::test_metadata_loader_reports_malformed_yaml_as_diagnostic tests/test_build_loaders.py::test_collection_metadata_loader_reports_malformed_yaml_as_diagnostic -q` passed.
- Build loader suite: `rtk bash scripts/test.bash tests/test_build_loaders.py -q` passed, `12 passed`.
- Related loader path: `rtk bash scripts/test.bash tests/test_build_loaders.py tests/test_module_sources.py tests/test_project_build.py tests/test_simple_source_family.py -q` passed, `106 passed`.
- Style: `rtk git diff --check` passed.
- Style: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/loaders.py tests/test_build_loaders.py` passed, `OK: 2 file(s) - no banned imports`.
- Style: `rtk bash scripts/flake.bash --ci` passed, `46 files would be left unchanged`.
- Full: `rtk bash scripts/test.bash` passed, `294 passed`.

## Risks Or Blockers

- Linear sync is blocked by expired auth: fetching `issue:TAL-294` returned `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Next

- Continue hardening generic loader diagnostics for author-facing source errors.
