# PDX Array Selectors Progress

Date: 2026-06-07 09:01 CST

Linear: unavailable; tool discovery exposed no Linear connector and `rtk which linear` returned no executable.

## Done

- Scanned the local HOI4 install for real array selector syntax after the unquoted-path parser slice.
- Found `^` selectors in script values and keys, including `FROM.warlord_subjects^num`, `SWE.SWE_states_to_transfers^0`, `operation_types_scores^i`, and `args^0?0.1`.
- Preserved identifier-tail `^` selectors as single PDX scalar identifiers when followed by an identifier or digit.
- Covered both scalar values and `var:` keys such as `var:SWE.SWE_states_to_transfers^0`.
- Documented array selector parse fidelity in the build workflow guide.

## Verification

- Red check: `rtk uv run pytest tests/test_pdx_token.py::test_tokenizer_keeps_array_selector_values_together tests/test_pdx_roundtrip.py::test_array_selector_values_round_trip_as_one_scalar -q` failed because `^` split into bare entries.
- Focused green: the same command passed 2 tests.
- PDX suite: `rtk uv run pytest tests/test_pdx_token.py tests/test_pdx_roundtrip.py -q` passed 26 tests.
- Related CLI/loader suite: `rtk bash scripts/test.bash tests/test_pdx_token.py tests/test_pdx_roundtrip.py tests/test_build_loaders.py tests/test_cli.py -q` passed 41 tests.
- Fallback-token probe: comparing the previous `HEAD` tokenizer to the working tree on the deterministic 1,200-file common/events/history/interface sample reduced sampled `^` fallback tokens from 4 to 0.
- HOI4 sample probe: `rtk uv run python - <<'PY' ... scan first 1200 common/events/history/interface PDX candidates ... PY` reported the same 2 unclosed-block files seen before this slice and no new parser errors: `common/doctrines/subdoctrines/sea/navy_submarine_doctrines.txt` and `common/ideas/SOV.txt`.
- Full suite: `rtk bash scripts/test.bash` passed with 254 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/pdx/token.py tests/test_pdx_token.py tests/test_pdx_roundtrip.py`

## Review

- This stays inside the tokenizer boundary; `^` selectors remain raw PDX scalar text rather than becoming typed array references.
- The rule only extends an identifier tail when `^` is followed by an identifier character or digit, which avoids absorbing a stray operator-like caret at token boundaries.
- The parser still treats the two local HOI4 unclosed-block files as structured diagnostics rather than special-casing malformed game content.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.
- The next parser-fidelity gap from the deterministic sample is not yet chosen; remaining fallback characters include `.`, `+`, `|`, and `,`, and some may be benign punctuation rather than scalar syntax.

## Next

- Inspect remaining fallback tokens against real game files, then either preserve another confirmed scalar form or return to generic module compilation behavior.
