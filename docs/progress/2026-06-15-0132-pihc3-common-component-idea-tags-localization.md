# 2026-06-15 01:32 PIHC3 common component idea-tags localization

## Scope

Continued the non-map PIHC2 to PIHC3 migration by expanding `common_component` localization ownership for compiled idea-tag support. This keeps `common/idea_tags/00_idea.txt` in the shared path-preserving common-component family and avoids adding a dedicated module type for one wrapper record.

## Changes

- Added path-gated localization extraction for `common/idea_tags/*.txt`.
- Extraction now reads `idea_categories = { ... }` and owns top-level `IDEA_TAG_*` wrapper rows.
- Native `idea_category` modules continue to own referenced `IDEA_CATEGORY_ERA_*` slot rows.
- Regenerated 48 common component modules.
- Generated `main.loc` for `COMMON_COMPONENT_IDEA_TAGS_00_IDEA`.
- Updated migration docs and the legacy inventory note.

## Evidence

- Red contract: `rtk uv run pytest tests/test_pihc3_migration_contracts.py -q -k "common_component_importer"` first failed with `KeyError: 'l_english'` for `common/idea_tags/00_idea.txt`.
- Green contract after the path-gated extractor change: `1 passed, 165 deselected in 293.80s`.
- Post-format focused contract: `1 passed, 165 deselected in 295.03s`.
- Regeneration: `Imported 48 PIHC2 common component modules into /Users/magolor/Utils/ParaDev-3/projects/PIHC3/src/modules/common_component`.
- Generated metadata: idea tags now have `loc_key_count: 2`.
- Dry build: `rtk uv run paradev build projects/PIHC3 --json > /tmp/pihc3-common-idea-tags-loc-dry-build.json`.
- Dry-build summary: 16,581 modules, 62 collections, 37,450 artifacts, 713 diagnostics, 0 errors, `blocked: false`.
- Dry-build diagnostics: 546 `copy_root.shadowed_artifact` warnings and 167 metadata warnings.
- Dry-build ownership: 48 `common_component` PDX artifacts and 240 `common_component` localization artifacts from 28 localized common-component modules.

## Follow-Up

- Continue common-component localization only where display keys are directly and safely derivable from compiled PDX.
- Keep map-adjacent terrain support out of this family until the skipped-map slice resumes.
