# PIHC3 Unit Component Metadata

Slice: enrich compiled unit/equipment support modules while keeping the family path-preserving and generic.

Changes:

- Added generic PDX-file metadata extraction to `projects/PIHC3/scripts/migrate_pihc2_unit_components.py`.
- Kept `unit_component` on the existing shared `pdx` slot plus generic localization output.
- Updated the stale family contract to assert the current generic loc slot.
- Regenerated 25 modules under `projects/PIHC3/src/modules/unit_component/`.
- Updated the unit component migration note, equipment note, design overview, and legacy inventory.

Metadata now records component id, unit domain, source slot counts, byte/line/nonempty-line counts, top-level wrapper keys, record counts, block/scalar record counts, full record names, first/last record samples, direct field-key counts, localization language counts, unique localization key counts, localization languages, and localization keys.

Representative checks cover:

- `UNIT_COMPONENT_UNITS_AIR`: `unit_definitions`, one `sub_units` wrapper, 38 block records, 603 source lines, and 5 unique localized unit keys.
- `UNIT_COMPONENT_UNITS_EQUIPMENT_CONVOYS`: `equipment_support`, one `equipments` wrapper, two block records, direct equipment field counts, and three unique localization keys.
- `UNIT_COMPONENT_UNITS_UNIT_MODIFIERS_UNIT_MODIFIERS`: `unit_modifiers`, one `sub_unit_modifiers` wrapper, 53 scalar records, and 53 unique localization keys.

Verification:

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k unit_component` -> 3 passed, 208 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_unit_components.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_unit_components.py --clean` -> 25 modules regenerated.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` -> 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build artifact ownership check found all 25 reviewed unit/equipment support PDX outputs owned by `module:unit_component/...`.

Remaining work:

- Editable sub-unit records remain future work only if GUI authoring needs them.
- Editable convoy/train/ship-hull support records remain future work.
- Unit-modifier balancing review remains future work.
