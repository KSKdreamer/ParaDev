# 2026-06-16 11:03 PIHC3 decision native metadata

## Scope

Enrich the PIHC2 -> PIHC3 native decision import so the GUI can browse decision provenance, localization, source slots, field groups, and icon evidence without adding decision-specific compiler logic.

## Changes

- Added a focused red contract for a representative `AGRICULTURE_INDUSTRY` decision module covering decision id, compiled source presence, source slot counts, legacy resource evidence paths, info/localization counts, direct field groups, effect/AI metadata, and icon dimensions.
- Extended `projects/PIHC3/scripts/migrate_pihc2_decisions.py` to emit generic decision metadata from existing sources: `legacy/source.yaml`, `meta.yaml`, `main.loc`, `def.txt`, and lightweight copied icons.
- Regenerated all 62 decision category collections and 458 native decision modules with `--clean`.
- Updated the PIHC3 decision migration notes, design overview, and legacy inventory with the refreshed native decision coverage.

## Evidence

- Red contract: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k decision_importer_extracts_source_slot_localization_and_icon_metadata_contract` failed first with `KeyError: 'decision_id'`.
- Green contract: the same focused command passed with `1 passed, 227 deselected`.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_decisions.py --clean` imported 62 decision category collections and decision modules into `projects/PIHC3/src`.
- Metadata coverage: 458 decision modules, 37-54 metadata settings per module, 44.7 average settings, 456 localized modules, 403 source-icon modules, 451 effect-summary modules, 438 trigger-summary modules, 428 AI-weight-summary modules, and 1,317 legacy evidence paths.
- Focused regression: `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k decision_importer` passed with `2 passed, 226 deselected`.
- Formatting: `rtk uv run black --check projects/PIHC3/scripts/migrate_pihc2_decisions.py tests/test_pihc3_migration_contracts.py` passed.
- Heaven-style scan: `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_decisions.py tests/test_pihc3_migration_contracts.py` returned `OK: 2 file(s) - no banned imports`.
- Build: `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-decision-native-metadata-build.json` completed with 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, and `blocked: false`.
- Build ownership: native decision modules own 1,315 artifacts, including 403 `gfx/paradev/DECISION_*/icon.png` files and 912 localization YAML files. Decision category collections own 246 artifacts, including 60 merged decision-category PDX files, 62 category descriptors, and 124 localization YAML files.

## Follow-Up

Category-specific GUI editing, scripted GUI parity, deeper generated icon workflows, and richer collection-level category metadata remain future decision slices.
