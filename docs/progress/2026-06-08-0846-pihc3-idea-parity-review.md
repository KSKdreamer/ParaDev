# PIHC3 Idea Parity Review

Date: 2026-06-08

## Scope

Added a PIHC3-local byte-level parity review for native idea artifacts that still shadow the PIHC_dev copy overlay.

## Result

- Added `projects/PIHC3/scripts/review_idea_shadow_parity.py`.
- The script reads `.paradev/build/source-map.json` so it reviews the actual native idea artifacts emitted by the compiler.
- Current real-project result: 390 ideas and 1,166 generated idea artifacts reviewed.
- Byte-level parity is not sufficient for cleanup yet: 1,164 artifacts differ and 2 generated English localization artifacts do not have PIHC_dev copy-root counterparts.

Current summary:

```json
{
  "artifact_count": 1166,
  "bucket_status_counts": {
    "common/ideas:different": 390,
    "localisation/english:different": 388,
    "localisation/english:missing_copy": 2,
    "localisation/simp_chinese:different": 386
  },
  "idea_count": 390,
  "schema": "pihc3.idea_shadow_parity.v1",
  "status_counts": {
    "different": 1164,
    "missing_copy": 2
  }
}
```

## Evidence

Representative differences are formatting-level: native PDX uses tab indentation while PIHC_dev uses spaces, and native localization omits the PIHC_dev BOM/tab style.

Generated English localization artifacts without copy-root counterparts:

- `localisation/english/IDEA_C01_ANGRY_BEST_PONY_l_english.yml`
- `localisation/english/IDEA_C01_ANGRY_CRY_l_english.yml`

## Next Step

Add normalized PDX/localization parity before changing idea copy-root excludes. The normalized review should distinguish formatting-only differences from real semantic/content drift.

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
- Flake: 4 Python files unchanged after formatting.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26976`, `diagnostic_count: 1164`, `error_count: 0`, `blocked: false`.
- Trait parity: 139 traits, 417 artifacts, `status_counts: {"exact": 417}`.
- Idea parity: 390 ideas, 1,166 artifacts, `status_counts: {"different": 1164, "missing_copy": 2}`.
