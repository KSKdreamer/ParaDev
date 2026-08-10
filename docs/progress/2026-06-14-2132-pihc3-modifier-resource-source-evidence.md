# 2026-06-14 21:32 CST - PIHC3 Modifier Resource Source Evidence

## Done

- Verified the current PIHC3 build already contains native `building`, `equipment`, and `modifier` modules, so the missing-GUI-data symptom is not caused by absent module families.
- Extended `modifier` import to preserve explicit PIHC2 `resources/modifiers/<TAG>` source folders as module-local legacy evidence.
- Copied `default.png`, `info.json`, and `locs.txt` from the seven available modifier resource folders into matching `MODIFIER_<TAG>` modules under `legacy/modifiers/<TAG>/`.
- Recorded those source paths in matching module `meta.yaml` settings and `legacy/source.yaml`.
- Left emitted game artifacts unchanged: compiled `common/modifiers/*.txt`, `gfx/interface/modifiers/MODIFIER_*.dds`, and `interface/modifiers/MODIFIER_*.gfx` still use the existing native modifier slots.
- Updated modifier migration docs and the legacy inventory to describe the non-emitted resource evidence.

## Verification

- Red check first: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'modifier_importer or modifier_family'` failed because `ModifierSource` lacked `legacy_source_paths`.
- `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'modifier_importer or modifier_family'`
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_modifiers.py --clean`
- Byte-checked `MODIFIER_EVERFREE_FOREST` `default.png`, `info.json`, and `locs.txt` against the PIHC2 source folder.
- `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-modifier-resource-source-build.json`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_modifiers.py tests/test_pihc3_migration_contracts.py`
- `rtk git diff --check`

The build reports 16,579 modules across 62 collections, 37,098 artifacts, 713 diagnostics, 0 errors, and `blocked: false`. The manifest still emits `MODIFIER_EVERFREE_FOREST` PDX/DDS/GFX artifacts from the `modifier` family, and 0 `legacy/modifiers/...` files are emitted as artifacts.

## Risk

- This preserves explicit PIHC2 modifier source folders for audit and future reconstruction; it does not reconstruct dynamic modifier or aggregate opinion modifier authoring from decision/focus/event scripts.
- BOP modifier localization remains intentionally owned by balance-of-power modules to avoid duplicate display rows.
- The module/artifact counts reflect the current dirty workspace build, including parallel work outside this slice.

## Next

- Continue data-family parity work for equipment/building/modifier GUI surfaces, or add source-evidence preservation to equipment records where PIHC2 source folders still carry unpreserved source images and JSON.
