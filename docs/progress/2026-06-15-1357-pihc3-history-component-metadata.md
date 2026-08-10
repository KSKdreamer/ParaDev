# PIHC3 History Component Metadata

Slice: enrich compiled general-history support components while keeping the family path-preserving and generic.

Changes:

- Added generic source-shape metadata to `projects/PIHC3/scripts/migrate_pihc2_history_components.py`.
- Kept `history_component` on the existing shared PDX slot instead of splitting departments, advisors, corps commanders, and scientists into separate component families.
- Regenerated 30 modules under `projects/PIHC3/src/modules/history_component/`.
- Updated history migration, design, and legacy inventory docs.

Metadata now records component id, source slot/counts, general-history domain, history role, history phase, country tag where applicable, byte/line/nonempty-line counts, top-level block keys/samples, root assignment keys/samples/counts, root assignment key counts, and direct field-key counts inside top-level blocks.

Representative checks cover:

- `HISTORY_COMPONENT_GENERAL_00_PIHC_DEPARTMENTS`: phase `00`, role `departments`, one `every_possible_country` block, and seven direct `generate_character` entries.
- `HISTORY_COMPONENT_GENERAL_01_PIHC_C01_CORP_COMMANDERS`: phase `01`, role `corp_commanders`, country tag `C01`, 10 C01 blocks, and 10 direct `random_list` fields.
- `HISTORY_COMPONENT_GENERAL_01_PIHC_C01_SCIENTISTS`: phase `01`, role `scientists`, country tag `C01`, two C01 blocks, and two direct `random_list` fields.

Verification:

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k history_component` -> 3 passed, 203 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_history_components.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_history_components.py --clean` -> 30 modules regenerated.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` -> 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build artifact ownership check found all 30 reviewed `history/general/*.txt` outputs owned by `module:history_component/...`.

Remaining work:

- Structured general-history setup authoring remains future work only if GUI editing needs it.
- Country history remains owned by `country_component`, unit/OOB history by `division`, and map/state history remains skipped for now.
