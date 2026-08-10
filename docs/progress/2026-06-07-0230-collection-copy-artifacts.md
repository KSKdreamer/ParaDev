# 2026-06-07 02:30 CST - Collection Copy Artifacts

## Done

- Added collection descriptor copy-slot loading for explicit `kind="copy"` collection source slots.
- Added collection-owned static copy artifacts for generic `CollectionSourceFamily` descriptor copy sources.
- Included collection copy sources in source-map and asset payloads with collection id, family, slot, hash, and size metadata.
- Documented descriptor copy artifacts in the build-flow guide.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_module_sources.py::test_load_collection_sources_uses_copy_slot_loader_role tests/test_simple_source_family.py::test_collection_source_family_emits_collection_copy_artifacts -q` failed because `CollectionSourceBundle` had no `copy_sources` and collection artifacts only included PDX.
- Focused green: `rtk bash scripts/test.bash tests/test_module_sources.py::test_load_collection_sources_uses_copy_slot_loader_role tests/test_simple_source_family.py::test_collection_source_family_emits_collection_copy_artifacts tests/test_project_build.py::test_project_build_tracks_registered_collection_copy_source_slots -q` passed 3 tests.
- Related suite: `rtk bash scripts/test.bash tests/test_module_sources.py tests/test_simple_source_family.py tests/test_project_build.py tests/test_project.py tests/test_build_manifest.py -q` passed 101 tests.
- Full suite: `rtk bash scripts/test.bash` passed 164 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/loaders.py src/paradev/build/families.py src/paradev/build/manifest.py src/paradev/build/records.py tests/test_module_sources.py tests/test_simple_source_family.py tests/test_project_build.py`
- SDK smoke: `rtk uv run python -c "from pathlib import Path; from tempfile import TemporaryDirectory; ..."` confirmed collection copy asset hash metadata and source attribution.
- Whitespace: `rtk git diff --check -- src/paradev/build/loaders.py src/paradev/build/families.py src/paradev/build/manifest.py src/paradev/build/records.py tests/test_module_sources.py tests/test_simple_source_family.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-07-0230-collection-copy-artifacts.md`

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Collection copy slots are explicit opt-in via `kind="copy"` on `collection_source_slots`; default collection discovery remains `def.pdx` plus `*.loc`.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue aligning manifest indexes and filters so collection-owned and module-owned compiler outputs are equally discoverable.
