# PIHC3 Country Component Metadata

Slice: enrich compiled country support components while keeping the family path-preserving and generic.

Changes:

- Added generic source-shape metadata to `projects/PIHC3/scripts/migrate_pihc2_country_components.py`.
- Kept `country_component` on the existing shared PDX slot instead of splitting tag registration, aliases, dynamic country definitions, colors, and history into separate component families.
- Regenerated 147 modules under `projects/PIHC3/src/modules/country_component/`.
- Updated country migration, design, and legacy inventory docs.

Metadata now records component id, source slot/counts, country component domain, country tag where applicable, byte/line/nonempty-line counts, top-level block keys/samples, root assignment keys/samples/counts, root assignment key counts, and direct field-key counts inside top-level blocks.

Representative checks cover:

- `COUNTRY_COMPONENT_COUNTRY_TAGS_00_COUNTRIES`: 67 country-tag assignments from `C00` through `C66`.
- `COUNTRY_COMPONENT_COUNTRY_TAG_ALIASES_TAG_ALIASES`: 24 alias blocks with `original_tag` and `has_country_flag`.
- `COUNTRY_COMPONENT_COUNTRIES_COLORS`: 67 color blocks with `color` and `color_ui`.
- `COUNTRY_COMPONENT_COUNTRIES_D01`: dynamic country definition body for tag `D01`.
- `COUNTRY_COMPONENT_COUNTRIES_C01`: C01 country history with 102 root assignments and 30 top-level blocks.

Verification:

- `rtk uv run pytest -q tests/test_pihc3_migration_contracts.py -k country_component` -> 3 passed, 202 deselected.
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py projects/PIHC3/scripts/migrate_pihc2_country_components.py tests/test_pihc3_migration_contracts.py` -> OK.
- `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_country_components.py --clean` -> 147 modules regenerated.
- `rtk proxy uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json` -> 16,581 modules, 62 collections, 37,480 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Build artifact ownership check found all 147 reviewed country support outputs owned by `module:country_component/...`.

Remaining work:

- Higher-level editable country setup reconstruction remains future work.
- Portrait/leader setup review, map ownership review, AI setup, OOB wiring, and cosmetic-tag flag source review remain future work.
