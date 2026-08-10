# PIHC3 Trait Overlay Cleanup

Date: 2026-06-08

## Scope

Used the byte-exact trait parity review to narrow the PIHC_dev copy overlay for native country-leader trait outputs.

## Result

- Added copy-root excludes in `projects/PIHC3/paradev.yaml`:
  - `common/country_leader/TRAIT_*.txt`
  - `localisation/english/TRAIT_*_l_english.yml`
  - `localisation/simp_chinese/TRAIT_*_l_simp_chinese.yml`
- Preserved unrelated copy-only files such as `common/country_leader/00_traits.txt`.
- Reduced `copy_root.shadowed_artifact` diagnostics from 1,581 to 1,164.
- Remaining shadow diagnostics are idea-owned.
- Native trait output still exists in `build/mod`.

## Verification

```bash
rtk uv run paradev build projects/PIHC3 --emit-manifests --json
rtk uv run paradev diagnostics projects/PIHC3 --code copy_root.shadowed_artifact --json
rtk uv run python projects/PIHC3/scripts/review_trait_shadow_parity.py --summary-only --fail-on-diff
```

Observed results:

- PIHC3 build: `module_count: 529`, `artifact_count: 26976`, `diagnostic_count: 1164`, `error_count: 0`, `blocked: false`.
- Shadow diagnostics: 1,164 total, all idea-owned.
- Trait parity review: 139 traits, 417 artifacts, `status_counts: {"exact": 417}`.
- `projects/PIHC3/build/mod/common/country_leader/TRAIT_ARCHAEOLOGIST.txt` exists after the cleanup.

## Next Step

Repeat the same review-first cleanup flow for native idea shadows. The idea side has more artifacts and includes icons/sprite assumptions, so it should get a dedicated parity review before changing copy-root excludes.
