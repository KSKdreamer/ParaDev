# PIHC3 Trait Parity Review

Date: 2026-06-08

## Scope

Added a PIHC3-local review script for native country-leader trait artifacts that shadow the PIHC_dev copy overlay.

## Result

- Added `projects/PIHC3/scripts/review_trait_shadow_parity.py`.
- The script discovers native `TRAIT_*` modules and compares their generated output under `build/mod` with PIHC_dev copy-root files.
- It checks each trait's country-leader PDX file, English localization, and Simplified Chinese localization.
- Current real-project result: 139 traits, 417 artifacts, all 417 byte-exact.

## Verification

```bash
rtk bash scripts/test.bash tests/test_sdk_examples.py::test_pihc3_trait_shadow_parity_review_summarizes_artifact_statuses -q
rtk bash scripts/test.bash tests/test_sdk_examples.py -q
rtk bash scripts/flake.bash --ci --paths tests/test_sdk_examples.py projects/PIHC3/scripts/migrate_pihc2_traits.py projects/PIHC3/scripts/review_trait_shadow_parity.py
rtk uv run python .claude/skills/heaven-style/scripts/scan.py tests/test_sdk_examples.py projects/PIHC3/scripts/migrate_pihc2_traits.py projects/PIHC3/scripts/review_trait_shadow_parity.py
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run python projects/PIHC3/scripts/review_trait_shadow_parity.py --summary-only --fail-on-diff
```

Observed results:

- `tests/test_sdk_examples.py`: 8 passed.
- Flake: 3 Python files unchanged after formatting.
- Heaven-style scan: OK, no banned imports.
- PIHC3 build: `module_count: 529`, `artifact_count: 26976`, `diagnostic_count: 1581`, `error_count: 0`, `blocked: false`.
- Trait parity review:

```json
{
  "artifact_count": 417,
  "schema": "pihc3.trait_shadow_parity.v1",
  "status_counts": {
    "exact": 417
  },
  "trait_count": 139
}
```

## Next Step

Use the exact trait parity evidence to narrow the PIHC_dev copy overlay for `common/country_leader/TRAIT_*.txt`, `localisation/english/TRAIT_*_l_english.yml`, and `localisation/simp_chinese/TRAIT_*_l_simp_chinese.yml`, while preserving unrelated copy-only files such as `common/country_leader/00_traits.txt`.
