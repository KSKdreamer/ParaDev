# PDX Dotted Variables Progress

Date: 2026-06-07 08:33 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Grounded the parser slice in the local HOI4 install, which uses dotted dynamic variable references such as `attacker_state_vs_@FROM.FROM` in event files.
- Fixed token-start dynamic variable parsing so `@FROM.FROM` stays one scalar value instead of splitting into `@FROM`, `.`, and `FROM` entries.
- Kept embedded references such as `distance_to@ROOT.capital` on the existing identifier path.
- Documented dynamic variable parse fidelity in the build workflow guide.

## Verification

- Red check: `rtk uv run pytest tests/test_pdx_token.py::test_tokenizer_keeps_dotted_variable_references_together tests/test_pdx_roundtrip.py::test_dotted_variable_values_round_trip_as_one_scalar -q` failed because `@FROM.FROM` split into multiple tokens and entries.
- Focused green: `rtk uv run pytest tests/test_pdx_token.py::test_tokenizer_keeps_dotted_variable_references_together tests/test_pdx_roundtrip.py::test_dotted_variable_values_round_trip_as_one_scalar -q`
- PDX suite: `rtk uv run pytest tests/test_pdx_token.py tests/test_pdx_roundtrip.py -q` passed 19 tests.
- Related CLI/loader suite: `rtk bash scripts/test.bash tests/test_pdx_token.py tests/test_pdx_roundtrip.py tests/test_build_loaders.py tests/test_cli.py -q` passed 34 tests.
- Parser smoke: `rtk uv run python - <<'PY' ... PDXBlock.from_str('clear_variable = attacker_state_vs_@FROM.FROM\nvalue = @FROM.FROM') ... PY`
- Full suite: `rtk bash scripts/test.bash` passed with 247 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/pdx/token.py tests/test_pdx_token.py tests/test_pdx_roundtrip.py`
- Diff hygiene: `rtk git diff --check -- src/paradev/pdx/token.py tests/test_pdx_token.py tests/test_pdx_roundtrip.py docs/workflows/build-flow.md`

## Review

- The tokenizer now reuses the same symbol-tail rule for normal identifiers and token-start variables, keeping dotted and scoped dynamic references consistent.
- The parser output still exposes the same `paradev.pdx.parse.v1` lossy projection; only scalar fidelity changed.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.
- This is lexical/round-trip fidelity, not full semantic validation of HOI4 dynamic variable expressions.

## Next

- Continue parser hardening against real HOI4 syntax samples before moving to broader generic compilation behavior.
