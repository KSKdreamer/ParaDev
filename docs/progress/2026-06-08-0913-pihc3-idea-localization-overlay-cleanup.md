# PIHC3 Idea Localization Overlay Cleanup

Date: 2026-06-08

## Scope

Finished the review-first cleanup flow for native idea localization artifacts.

## Result

- Fixed `projects/PIHC3/scripts/review_idea_shadow_parity.py` to normalize multiline localization strings.
- Added global shared-key compatibility so repeated `SUCCESS`/`FAILURE` keys are compatible when the same key/text exists elsewhere in native generated localization.
- Added copy-root excludes in `projects/PIHC3/paradev.yaml`:
  - `localisation/english/IDEA_*_l_english.yml`
  - `localisation/simp_chinese/IDEA_*_l_simp_chinese.yml`
- Reduced `copy_root.shadowed_artifact` diagnostics from 774 to 0.

Current idea parity summary:

```json
{
  "parity_status_counts": {
    "compatible_extra_empty_desc": 256,
    "compatible_shared_loc_elsewhere": 6,
    "equivalent": 902,
    "missing_copy": 2
  }
}
```

Current build summary:

```json
{
  "artifact_count": 26892,
  "blocked": false,
  "diagnostic_count": 0,
  "error_count": 0,
  "module_count": 529
}
```

## Notes

- The two `missing_copy` rows are native-only English localization outputs:
  - `localisation/english/IDEA_C01_ANGRY_BEST_PONY_l_english.yml`
  - `localisation/english/IDEA_C01_ANGRY_CRY_l_english.yml`
- Idea localization is parity-compatible, not byte-identical.
- The copy overlay no longer shadows native idea or trait artifacts.

## Next Step

Move to the next PIHC2 domain or add the next project-local authoring template. The idea and country-leader trait domains now have native modules, project-local SDK templates, parity review tools, and no copy-root shadow queue.

## Verification

```bash
rtk bash scripts/test.bash tests/test_sdk_examples.py -q
rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py projects/PIHC3/scripts/migrate_pihc2_traits.py projects/PIHC3/scripts/review_trait_shadow_parity.py projects/PIHC3/scripts/review_idea_shadow_parity.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py projects/PIHC3/scripts/migrate_pihc2_traits.py projects/PIHC3/scripts/review_trait_shadow_parity.py projects/PIHC3/scripts/review_idea_shadow_parity.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json
rtk uv run python projects/PIHC3/scripts/review_trait_shadow_parity.py --summary-only --fail-on-diff
rtk uv run python projects/PIHC3/scripts/review_idea_shadow_parity.py --summary-only
```

Observed results:

- `tests/test_sdk_examples.py`: 9 passed.
- Flake: 4 Python files unchanged.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26892`, `diagnostic_count: 0`, `error_count: 0`, `blocked: false`.
- Copy-root shadows: 0.
- Trait parity: 139 traits, 417 artifacts, `status_counts: {"exact": 417}`.
- Idea parity: `parity_status_counts: {"compatible_extra_empty_desc": 256, "compatible_shared_loc_elsewhere": 6, "equivalent": 902, "missing_copy": 2}`.
- Sample generated idea PDX, idea localization, native-only English localization, and trait PDX files all exist in `build/mod`.
