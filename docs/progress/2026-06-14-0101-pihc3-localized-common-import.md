# 2026-06-14 01:01 +0800 - PIHC3 Localized Common Import

## Summary

Extended the compiled PIHC_dev common-source importer to cover small localized common families that can use the shared `simple_source` module path.

## Changes

- Imported 34 more native modules, bringing the compiled common-source importer to 357 modules across 18 families.
- Added native modules for autonomous states, buildings, continuous focuses, faction templates, game rules, operations, operation phases, operation tokens, operative codenames, resistance activities, resources, unit medals, and wargoals.
- Preserved compiled PIHC_dev PDX in each module `def.txt`.
- Wrote compiled English/Simplified Chinese localization rows for localized common families where the source references loc keys; left operation phases PDX-only for this pass because their localization rows collide with autonomy output paths.
- Added copy-root excludes for the newly native common output paths.
- Updated PIHC3 migration design and family notes from starter-only status to starter-plus-importer status.

## Verification

- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_common_sources.py --clean`
- `rtk git diff --check -- <changed PIHC3 migration files and this note>`
- `rtk rg -n "[[:blank:]]$" <changed PIHC3 migration files and this note>`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_common_sources.py`
  - OK: 1 file, no banned imports
- `rtk bash scripts/flake.bash --ci`
- `rtk bash scripts/test.bash`
  - 554 passed in 175.74s
- `rtk uv run paradev summary projects/PIHC3 --json`
  - modules: 2,841
  - collections: 62
  - artifacts: 25,995
  - diagnostics: 4,183
  - errors: 0
  - blocked: false
- `Project.load(Path("projects/PIHC3")).build(emit_artifacts=True, emit_manifests=True)`
  - dry_run: false
  - modules: 2,841
  - collections: 62
  - artifacts: 25,995
  - diagnostics: 4,183
  - errors: 0
  - blocked: false
- Native ownership spot checks confirmed one native owner for:
  - `common/buildings/00_buildings.txt`
  - `common/resources/00_resources.txt`
  - `common/autonomous_states/pihc_dominion.txt`
  - `common/game_rules/pihc_game_rules.txt`
  - `common/operations/00_operations.txt`
  - `common/operation_phases/lar_collaboration_government.txt`
  - `common/operation_tokens/00_OperationTokens.txt`
  - `common/units/codenames_operatives/generic_opertive_codenames.txt`
  - `common/unit_medals/00_default.txt`
  - `common/wargoals/00_invasion.txt`

## Risks Or Blockers

- Operation-phase localization needs a follow-up pass after resolving the source localization path collision.
- Full faction goals/rules/upgrades, inventory items, superevents, state lore, entities, states, and map data remain future native migration slices.

## Next

- Continue turning scaffold-only or copy-only families into native modules through shared slots first.
- Add family-specific parity validators where legacy generators emitted generated assets, scripted localisation, GUI fragments, or multi-file aggregates.
