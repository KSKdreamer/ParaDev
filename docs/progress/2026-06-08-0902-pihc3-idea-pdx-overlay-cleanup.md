# PIHC3 Idea PDX Overlay Cleanup

Date: 2026-06-08

## Scope

Used normalized idea parity evidence to narrow the PIHC_dev copy overlay for native idea PDX output while leaving idea localization in the overlay.

## Result

- Added `parity_status` to `projects/PIHC3/scripts/review_idea_shadow_parity.py`.
- `compatible_extra_empty_desc` marks localization artifacts where the only drift is a native empty `_desc` key required by current ParaDev idea localization checks.
- Added `common/ideas/IDEA_*.txt` to `projects/PIHC3/paradev.yaml` copy-root excludes.
- Reduced `copy_root.shadowed_artifact` diagnostics from 1,164 to 774.
- Remaining shadow diagnostics are idea-localization only.

Current idea parity summary:

```json
{
  "parity_status_counts": {
    "compatible_extra_empty_desc": 252,
    "different": 111,
    "equivalent": 801,
    "missing_copy": 2
  }
}
```

Current build summary:

```json
{
  "artifact_count": 26970,
  "blocked": false,
  "diagnostic_count": 774,
  "error_count": 0,
  "module_count": 529
}
```

## Remaining Localization Drift

- 252 localization artifacts are compatible-only drift from native empty `_desc` additions.
- 111 localization artifacts still have real key drift.
- 2 generated English localization artifacts still have no PIHC_dev copy-root counterpart.

The remaining 111 real key drifts are:

- 107 artifacts with missing native keys only;
- 4 artifacts with both native-only empty `_desc` additions and missing native keys.

## Next Step

Fix or explicitly accept the remaining localization key drift before narrowing idea localization copy-root excludes.

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
- PIHC3 build: `module_count: 529`, `artifact_count: 26970`, `diagnostic_count: 774`, `error_count: 0`, `blocked: false`.
- Copy-root shadows: 774 total, all idea-localization owned.
- Shadow buckets: 388 English localization files and 386 Simplified Chinese localization files.
- Trait parity: 139 traits, 417 artifacts, `status_counts: {"exact": 417}`.
- Idea parity: `parity_status_counts: {"compatible_extra_empty_desc": 252, "different": 111, "equivalent": 801, "missing_copy": 2}`.
