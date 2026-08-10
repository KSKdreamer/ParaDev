# 2026-06-20 15:24 - PIHC3 review script folder cleanup

## Summary

Tightened the PIHC3 script layout so top-level `projects/PIHC3/scripts/` contains migration importers and private shared helpers only. Parity review utilities now live under `projects/PIHC3/scripts/review/`, which keeps review-only tooling separate from one-shot migration scripts without deleting useful PIHC_dev shadow-parity checks.

## Changed

- Moved idea and trait shadow-parity review scripts into `projects/PIHC3/scripts/review/`.
- Fixed the moved scripts' `PROJECT_ROOT` calculation for the deeper folder.
- Added a PIHC3 contract test that rejects non-migration top-level scripts and imports both moved review utilities.
- Updated PIHC3 README and migration notes to use the new review script paths.

## Verification

- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'scripts_group_review_utilities'`
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'scripts_group_review_utilities or project_build_wrappers or source_root or idea_importer'`
- `rtk uv run black --check projects/PIHC3/scripts/review/idea_shadow_parity.py projects/PIHC3/scripts/review/trait_shadow_parity.py tests/test_pihc3_migration_contracts.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/review/idea_shadow_parity.py projects/PIHC3/scripts/review/trait_shadow_parity.py tests/test_pihc3_migration_contracts.py`
- `rtk git diff --check -- tests/test_pihc3_migration_contracts.py projects/PIHC3/README.md projects/PIHC3/docs/migration/03-ideas.md projects/PIHC3/docs/migration/04-traits.md projects/PIHC3/scripts/review/idea_shadow_parity.py projects/PIHC3/scripts/review/trait_shadow_parity.py projects/PIHC3/scripts/review_idea_shadow_parity.py projects/PIHC3/scripts/review_trait_shadow_parity.py`
