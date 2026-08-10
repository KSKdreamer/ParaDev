# PIHC3 Idea Metadata Extraction

Status: completed slice

## Scope

- Updated `projects/PIHC3/scripts/import_pihc2_ideas_current.py` so native idea modules expose merged idea-body data in `meta.yaml` settings.
- Regenerated all 390 `src/modules/idea/IDEA_<TAG>` modules.
- Kept the built-in HOI4 `idea` family on shared `def`, `loc`, and `icon` slots; no family-specific compiler code was added.

## Details

- Idea metadata now records `idea_keys`, category, picture, removal cost, modifiers, cancel/allowed/visible/available blocks, default `allowed_civil_war`, designer flags, traits, targeted modifiers, and AI weights where present.
- The importer factors the merged HOI4DEV-style idea body once and uses it for both `def.txt` generation and metadata extraction, preserving normalized PDX parity while improving GUI browsing data.
- Direct import loading now adds the script directory to `sys.path`, so the importer contract can be exercised by focused tests.

## Verification

- Red: `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_idea_importer_extracts_compiled_idea_metadata_contract -q` first failed on missing script-local helper import, then failed on missing `idea_keys`.
- Green: `rtk uv run pytest tests/test_pihc3_migration_contracts.py::test_pihc3_idea_importer_extracts_compiled_idea_metadata_contract -q` passed.
- Focused suite: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k 'idea_importer or idea_family or idea_component or idea_asset_component'` passed with 6 tests and 147 deselected.
- Regeneration: `rtk uv run python projects/PIHC3/scripts/import_pihc2_ideas_current.py --clean` imported 390 idea modules.
- Build: `rtk uv run paradev build projects/PIHC3 --emit-artifacts --emit-manifests --json > /tmp/pihc3-idea-metadata-build.json` exited 0 and reported 16,581 modules, 62 collections, 37,370 artifacts, 713 diagnostics, 0 errors, `blocked: false`.

## Remaining

- Source-image-to-DDS icon regeneration remains future work; compiled idea assets are still preserved by `idea_asset_component`.
- Nested idea-category law aggregation and level ordering are handled by `idea_category`, but still need a dedicated parity review.
