# 2026-06-07 02:22 CST - Collection Localization Artifacts

## Done

- Added generic collection-owned localization artifacts for `CollectionSourceFamily` descriptor localization entries.
- Rendered collection localization paths through the existing `loc_path_template`, using the collection id as `object_id`.
- Preserved collection localization inputs in source-map payloads for SDK, CLI, desktop, and future MCP clients.
- Updated the HOI4 decision family to rely on the generic localization artifact while keeping decision-specific localization validation.
- Documented the collection descriptor localization contract in the build-flow guide.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_collection_source_family_emits_collection_localization_artifacts -q` failed because only the collection PDX artifact was planned.
- Focused green: `rtk bash scripts/test.bash tests/test_simple_source_family.py::test_collection_source_family_emits_collection_localization_artifacts tests/test_project_build.py::test_project_build_uses_registered_collection_source_slots tests/test_project_build.py::test_hoi4_profile_emits_decision_category_localization_artifact -q` passed 3 tests.
- Related suite: `rtk bash scripts/test.bash tests/test_simple_source_family.py tests/test_project_build.py tests/test_project.py tests/test_build_manifest.py tests/test_module_sources.py -q` passed 98 tests.
- Full suite: `rtk bash scripts/test.bash` passed 161 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/families.py src/paradev/games/hoi4/__init__.py tests/test_simple_source_family.py tests/test_project_build.py`
- SDK smoke: `rtk uv run python -c "from pathlib import Path; from tempfile import TemporaryDirectory; ..."` confirmed generic collection loc artifact planning and source-map attribution.
- Whitespace: `rtk git diff --check -- src/paradev/build/families.py src/paradev/games/hoi4/__init__.py tests/test_simple_source_family.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-07-0222-collection-localization-artifacts.md`

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- This slice keeps collection localization on generic collection-source families only. Focus-specific localization remains module-owned until the profile needs collection-owned focus descriptor localization.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue reducing HOI4-specific compiler code by moving reusable collection-source behavior into generic family helpers where the contract is profile-independent.
