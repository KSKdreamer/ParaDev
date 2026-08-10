# PIHC3 Idea Normalized Parity

Date: 2026-06-08

## Scope

Extended the PIHC3 idea parity reviewer with normalized comparison so byte-level formatting differences do not hide real content drift.

## Result

- `projects/PIHC3/scripts/review_idea_shadow_parity.py` now reports `normalized_status` per artifact.
- PDX normalization uses the ParaDev PDX parser and compares parsed block dictionaries.
- Localization normalization ignores UTF-8 BOM, indentation, language-header style, and escaped string syntax while preserving keys and text.
- Byte-level result remains unchanged: 1,164 different artifacts and 2 missing copy-root artifacts.
- Normalized result:
  - 801 equivalent artifacts;
  - 363 different artifacts;
  - 2 missing copy-root artifacts.

Current summary:

```json
{
  "bucket_normalized_status_counts": {
    "common/ideas:equivalent": 390,
    "localisation/english:different": 180,
    "localisation/english:equivalent": 208,
    "localisation/english:missing_copy": 2,
    "localisation/simp_chinese:different": 183,
    "localisation/simp_chinese:equivalent": 203
  },
  "normalized_status_counts": {
    "different": 363,
    "equivalent": 801,
    "missing_copy": 2
  }
}
```

## Evidence

- All 390 generated idea PDX files are normalized-equivalent to PIHC_dev.
- 411 generated idea localization files are normalized-equivalent to PIHC_dev.
- 252 localization artifacts differ only because native output adds an empty `_desc` key absent from PIHC_dev.
- The remaining 111 mixed localization cases include missing copy-root keys, such as `IDEA_ALL_DARK_MAGIC_PAYBACK_desc`.

## Next Step

Do not narrow idea copy-root excludes yet. First decide whether empty generated `_desc` keys should be treated as acceptable parity, then fix or explicitly accept the remaining localization key drift.

## Verification

```bash
rtk bash scripts/test.bash tests/test_sdk_examples.py -q
rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py projects/PIHC3/scripts/migrate_pihc2_traits.py projects/PIHC3/scripts/review_trait_shadow_parity.py projects/PIHC3/scripts/review_idea_shadow_parity.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py projects/PIHC3/scripts/migrate_pihc2_traits.py projects/PIHC3/scripts/review_trait_shadow_parity.py projects/PIHC3/scripts/review_idea_shadow_parity.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run python projects/PIHC3/scripts/review_trait_shadow_parity.py --summary-only --fail-on-diff
rtk uv run python projects/PIHC3/scripts/review_idea_shadow_parity.py --summary-only
```

Observed results:

- `tests/test_sdk_examples.py`: 9 passed.
- Flake: 4 Python files unchanged.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26976`, `diagnostic_count: 1164`, `error_count: 0`, `blocked: false`.
- Trait parity: 139 traits, 417 artifacts, `status_counts: {"exact": 417}`.
- Idea normalized parity: `status_counts: {"different": 1164, "missing_copy": 2}`, `normalized_status_counts: {"different": 363, "equivalent": 801, "missing_copy": 2}`.
