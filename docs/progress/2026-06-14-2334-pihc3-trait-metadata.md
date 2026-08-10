# PIHC3 Trait Metadata Extraction

Status: completed slice

## Scope

- Updated `projects/PIHC3/scripts/migrate_pihc2_traits.py` so native trait modules expose generated trait-body data in `meta.yaml` settings.
- Regenerated all 139 `src/modules/trait/TRAIT_<TAG>` modules.
- Kept the routed `trait` family on shared `def`, `loc`, and optional icon/copy slots; no family-specific compiler code was added.

## Details

- Trait metadata now records `trait_keys`, `random`, default `ai_will_do`, modifier fields such as stability/research/army factors, and custom tooltip keys where present.
- The importer factors the HOI4DEV-style generated trait body once and uses it for both `def.txt` generation and metadata extraction.
- Direct import loading now adds the script directory to `sys.path`, so the importer contract can be exercised by focused tests.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'trait_importer or trait_family or unit_leader_component or leader_trait_component'` first failed on missing script-local helper import.
- Green: the same focused suite passed with 6 tests and 153 deselected after metadata extraction was implemented.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_traits.py --clean` imported 139 trait modules.
- Build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-trait-metadata-build.json` exited 0 and reported 16,581 modules, 62 collections, 37,404 artifacts, 713 diagnostics, 0 errors, `blocked: false`.

## Remaining

- Unit-leader and scientist trait authoring remains future work; current PIHC2 `resources/traits` records intentionally stay `country_leader` subtype modules.
- Trait icon/image handling remains limited to shared optional source slots and legacy evidence.
