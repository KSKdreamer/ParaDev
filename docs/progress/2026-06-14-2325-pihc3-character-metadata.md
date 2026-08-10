# PIHC3 Character Metadata Extraction

Status: completed slice

## Scope

- Updated `projects/PIHC3/scripts/migrate_pihc2_characters.py` so native character modules expose compiled character-body data in `meta.yaml` settings.
- Regenerated all 250 `src/modules/character/CHARACTER_<TAG>` modules.
- Kept the built-in simple `character` family on shared `def`, `loc`, and `portrait` slots; no family-specific compiler code was added.

## Details

- Character metadata now records `character_keys`, `character_roles`, `name`, portrait references, gender, country-leader/advisor/commander blocks, traits, ideology, advisor cost/removal settings, and empty role trait lists where present.
- The importer parses compiled PIHC_dev character PDX once per run and uses it for metadata while preserving the compiled source text in `def.txt`.
- Direct import loading now adds the script directory to `sys.path`, so the importer contract can be exercised by focused tests.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'character_importer or character_family or portrait_component or portrait_asset_component or leader_trait_component'` first failed on missing script-local helper import.
- Green: the same focused suite passed with 8 tests and 149 deselected after metadata extraction was implemented.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/migrate_pihc2_characters.py --clean` imported 250 character modules.
- Build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-character-metadata-build.json` exited 0 and reported 16,581 modules, 62 collections, 37,404 artifacts, 713 diagnostics, 0 errors, `blocked: false`.

## Remaining

- Role-specific authoring templates for advisors, country leaders, corps commanders, field marshals, navy leaders, and scientists remain future work.
- Portrait DDS regeneration, animation strip generation, and editable random-character pool reconstruction remain future slices.
