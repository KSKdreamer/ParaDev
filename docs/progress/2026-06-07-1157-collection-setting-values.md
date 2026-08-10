# Collection Setting Values Progress

Date: 2026-06-07 11:57

Linear: TAL-294. Read attempt returned `UNAUTHORIZED; Session expired. Please re-authenticate.`, so the Linear issue still needs manual re-authentication before this slice can be synced there.

## Summary

- Added collection descriptor setting value validation for collection-owned generic families.
- `CollectionPDXFamily` and `CollectionSourceFamily` now reject authored descriptor `settings` values that are outside declared `settings_values`.
- Diagnostics point at the descriptor metadata file (`meta.yaml` or `collection.yaml`) and remain visible through filtered `Project.diagnostics(...)` payloads with source metadata.
- Updated the build-flow guide to clarify that descriptor settings are value-checked when present, while `required_settings` remains the module/source-side contract.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_validates_manifest_collection_setting_values -q` failed because invalid descriptor settings did not block the build.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_validates_manifest_collection_setting_values -q` passed.
- Related suite: `rtk bash scripts/test.bash tests/test_simple_source_family.py tests/test_project_build.py tests/test_project.py tests/test_build_manifest.py -q` passed `191 passed`.
- Whitespace: `rtk git diff --check` passed.
- Flake: `rtk bash scripts/flake.bash --ci` passed.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py tests/test_project_build.py` passed.
- Full tests: `rtk bash scripts/test.bash` passed `286 passed in 68.94s`.

## Review Notes

- This slice intentionally does not enforce `required_settings` on collection descriptors. Empty descriptor scaffolds should remain usable while module sources carry required compiler settings.
- Existing local README and desktop app edits were left outside this compiler contract slice.

## Next

- Continue aligning collection descriptor behavior with module source behavior where it improves user-facing diagnostics without forcing placeholder descriptor files to become full modules.
- Resume the generic module compilation system once descriptor contracts are consistent across metadata, localization, assets, and settings.
