# Metadata Read Diagnostics Progress

Date: 2026-06-07 14:25 CST

Linear: TAL-294

## Done

- Added structured `metadata.unreadable_source` diagnostics for module `meta.yaml` read failures.
- Added structured `collection_metadata.unreadable_source` diagnostics for collection descriptor `meta.yaml` or `collection.yaml` read failures.
- Preserved inferred object identity, module id or collection id, and metadata source path context when reads fail.
- Added regression tests for module and collection metadata read failures.
- Documented the metadata unreadable-source behavior in `docs/workflows/build-flow.md`.

## Verification

- `rtk uv run pytest tests/test_build_loaders.py::test_metadata_loader_reports_unreadable_yaml_as_diagnostic tests/test_build_loaders.py::test_collection_metadata_loader_reports_unreadable_yaml_as_diagnostic`
- `rtk git diff --check`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/loaders.py tests/test_build_loaders.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- Python metadata loader smoke confirmed `metadata.unreadable_source` from `load_metadata`.

## Risks Or Blockers

- Linear sync failed again with `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Next

- Continue hardening first-slot compiler diagnostics and artifact emission ergonomics.
