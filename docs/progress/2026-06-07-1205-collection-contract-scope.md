# Collection Contract Scope Progress

Date: 2026-06-07 12:05

Linear: TAL-294. Read attempt returned `UNAUTHORIZED; Session expired. Please re-authenticate.`, so the Linear issue still needs manual re-authentication before this slice can be synced there.

## Summary

- Fixed collection descriptor contract checks so they only validate descriptors owned by the current family.
- Settings values, required localization keys, and copy asset constraints no longer cross-validate unrelated collection families that reuse the same setting or slot names.
- Added a manifest-backed regression with descriptor-only `bulletin` and `dossier` collections that use different `settings.layout`, localization requirements, and media formats.
- Updated the build-flow guide to document family-scoped descriptor contracts for SDK, GUI, MCP, and script clients.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_scopes_manifest_collection_descriptor_contracts_by_family -q` failed because unrelated collection families blocked each other.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_scopes_manifest_collection_descriptor_contracts_by_family -q` passed.
- Contract cluster: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_validates_manifest_collection_setting_values tests/test_project_build.py::test_project_build_validates_collection_required_localization_keys tests/test_project_build.py::test_project_build_validates_manifest_collection_asset_constraints tests/test_simple_source_family.py::test_collection_source_family_reports_missing_collection_required_localization_keys tests/test_simple_source_family.py::test_collection_source_family_reports_collection_asset_constraint_diagnostics -q` passed `5 passed`.
- Related suite: `rtk bash scripts/test.bash tests/test_simple_source_family.py tests/test_project_build.py tests/test_project.py tests/test_build_manifest.py -q` passed `192 passed`.
- Whitespace: `rtk git diff --check` passed.
- Flake: `rtk bash scripts/flake.bash --ci` passed.
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py tests/test_project_build.py` passed.
- Full tests: `rtk bash scripts/test.bash` passed `287 passed in 68.99s`.

## Review Notes

- The build planner still passes all collections to family hooks. The family helpers now enforce the ownership boundary internally, matching the existing artifact emission path.
- Existing local README and desktop app edits were left outside this compiler contract slice.

## Next

- Continue tightening generic compiler boundaries where collection-owned behavior shares helper code across families.
- Move back toward generic module compilation after descriptor contracts remain predictable under multi-family projects.
