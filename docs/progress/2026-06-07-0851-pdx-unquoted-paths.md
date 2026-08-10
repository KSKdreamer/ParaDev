# PDX Unquoted Paths Progress

Date: 2026-06-07 08:51 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Scanned the local HOI4 install for tokenizer fallback characters after scripted scalar parsing.
- Found that real `.gfx` files use unquoted asset paths such as `texturefile = gfx/interface/equipmentdesigner/tanks/designer/generic/generic_light_AAB.dds`.
- Preserved unquoted path-like scalar values with `/` separators as single parser values, including doubled separators such as `gfx//leaders//Africa//Portrait_Africa_Generic_2.dds`.
- Documented unquoted asset path parse fidelity in the build workflow guide.

## Verification

- Red check: `rtk uv run pytest tests/test_pdx_token.py::test_tokenizer_keeps_unquoted_path_values_together tests/test_pdx_roundtrip.py::test_unquoted_path_values_round_trip_as_one_scalar -q` failed because `/` split into bare entries.
- Focused green: `rtk uv run pytest tests/test_pdx_token.py::test_tokenizer_keeps_unquoted_path_values_together tests/test_pdx_roundtrip.py::test_unquoted_path_values_round_trip_as_one_scalar -q`
- PDX suite: `rtk uv run pytest tests/test_pdx_token.py tests/test_pdx_roundtrip.py -q` passed 24 tests.
- Related CLI/loader suite: `rtk bash scripts/test.bash tests/test_pdx_token.py tests/test_pdx_roundtrip.py tests/test_build_loaders.py tests/test_cli.py -q` passed 39 tests.
- Parser smoke: `rtk uv run python - <<'PY' ... PDXBlock.from_str(...) ... PY` preserved normal and doubled unquoted asset paths in `to_dict()` and `to_str()`.
- Fallback-token probe: `rtk uv run python - <<'PY' ... count single-character fallback identifiers ... PY` reduced sampled `/` fallback tokens from 7,954 to 0 in the deterministic 1,200-file common/events/history/interface sample.
- HOI4 sample probe: `rtk uv run python - <<'PY' ... scan first 1200 common/events/history/interface PDX candidates ... PY` reported the same 2 unclosed-block files seen before this slice and no new parser errors: `common/doctrines/subdoctrines/sea/navy_submarine_doctrines.txt` and `common/ideas/SOV.txt`.
- Full suite: `rtk bash scripts/test.bash` passed with 252 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/pdx/token.py tests/test_pdx_token.py tests/test_pdx_roundtrip.py`
- Diff hygiene: `rtk git diff --check -- src/paradev/pdx/token.py tests/test_pdx_token.py tests/test_pdx_roundtrip.py docs/workflows/build-flow.md docs/progress/2026-06-07-0851-pdx-unquoted-paths.md`

## Review

- This remains a lexical fidelity fix: path strings are preserved as plain scalar identifiers, not validated against the filesystem.
- The tokenizer owns the change so parse CLI, source-slot loaders, and future editor diagnostics share the same behavior.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.
- Array selectors using `^` remain the next obvious real HOI4 scalar-fidelity gap.

## Next

- Preserve array-selector scalar values such as `global.monroe_countries_in_support^num` and `SOV_military_offensive_states^0` before returning to generic module compilation behavior.
