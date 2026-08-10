# PIHC3 Generic Family Import Progress

Date: 2026-06-13 23:48 +0800

Linear: none

## Done

- Rehomed non-map PIHC2 importers for modifiers, equipment, doctrines, special projects, special project rewards, achievements, and intelligence agencies into `projects/PIHC3/src/modules/<family>/`.
- Added shared legacy localization expansion for scoped `@` keys and reused generic PDX, loc, metadata, and copy slots instead of bespoke family code.
- Added project-local generic family config for icon copy slots and routed doctrine output paths.
- Fixed the shared localization loader so HOI4 scripted localization brackets inside section text are not parsed as broken headers.

## Verification

- `rtk bash scripts/test.bash tests/test_localization_loader.py -q`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/loaders.py tests/test_localization_loader.py projects/PIHC3/scripts/_entity_migration_common.py projects/PIHC3/scripts/migrate_pihc2_modifiers.py projects/PIHC3/scripts/migrate_pihc2_equipments.py projects/PIHC3/scripts/migrate_pihc2_doctrines.py projects/PIHC3/scripts/migrate_pihc2_special_projects.py projects/PIHC3/scripts/migrate_pihc2_achievements.py projects/PIHC3/scripts/migrate_pihc2_intel_agencies.py`
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
- `rtk uv run paradev summary projects/PIHC3 --json`
- Emitted PIHC3 artifacts and manifests through `Project.build(emit_artifacts=True, emit_manifests=True)`.

## Risks Or Blockers

- PIHC3 build has zero errors and is unblocked, with 980 copy-root shadow warnings from generated artifacts replacing files copied from the legacy mod root.
- Forty-three imported doctrine modules used fallback generated bodies because no compiled doctrine block was found for the legacy resource entry.

## Next

- Continue non-map PIHC2 migration for remaining empty families, starting with buildings or other missing common-definition families.
- Decide whether shadowed copy-root warnings should stay as expected migration evidence or be filtered once each family is considered fully native.
