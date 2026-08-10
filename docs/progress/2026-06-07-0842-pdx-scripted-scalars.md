# PDX Scripted Scalars Progress

Date: 2026-06-07 08:42 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Scanned the local HOI4 install for parser gaps in `common`, `events`, `history/countries`, and `interface` script files.
- Preserved bracketed scripted scalar values such as `[GetHitlerHandshakeEventPicture]` and `[?temp_var_PRC_military_factories]` as single parser values.
- Preserved fallback default scalar values such as `global.days_add_support?1337` as single parser values.
- Added structured `pdx.unterminated_bracket_value` diagnostics for unclosed bracketed values.
- Documented the scripted scalar behavior and bracket diagnostic in the build workflow guide.

## Verification

- Red check: `rtk uv run pytest tests/test_pdx_token.py::test_tokenizer_keeps_scripted_scalar_values_together tests/test_pdx_roundtrip.py::test_scripted_scalar_values_round_trip_as_one_scalar -q` failed because bracketed values and `?` defaults split into extra bare entries.
- Focused green: `rtk uv run pytest tests/test_pdx_token.py::test_tokenizer_keeps_scripted_scalar_values_together tests/test_pdx_roundtrip.py::test_scripted_scalar_values_round_trip_as_one_scalar -q`
- PDX suite: `rtk uv run pytest tests/test_pdx_token.py tests/test_pdx_roundtrip.py -q` passed 22 tests.
- Related CLI/loader suite: `rtk bash scripts/test.bash tests/test_pdx_token.py tests/test_pdx_roundtrip.py tests/test_build_loaders.py tests/test_cli.py -q` passed 37 tests.
- Parser smoke: `rtk uv run python - <<'PY' ... PDXBlock.from_str(...) ... PY` preserved bracketed scripted values and fallback defaults in `to_dict()` and `to_str()`.
- Diagnostic smoke: `rtk uv run python - <<'PY' ... PDXBlock.from_str('picture = [GetHitlerHandshakeEventPicture') ... PY` returned `pdx.unterminated_bracket_value`.
- HOI4 sample probe: `rtk uv run python - <<'PY' ... scan first 1200 common/events/history/interface PDX candidates ... PY` reported the same 2 unclosed-block files seen before this slice and no new parser errors.
- Full suite: `rtk bash scripts/test.bash` passed with 250 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/pdx/token.py tests/test_pdx_token.py tests/test_pdx_roundtrip.py`
- Diff hygiene: `rtk git diff --check -- src/paradev/pdx/token.py tests/test_pdx_token.py tests/test_pdx_roundtrip.py docs/workflows/build-flow.md docs/progress/2026-06-07-0842-pdx-scripted-scalars.md`

## Review

- The parser still exposes scripted expressions as plain scalar identifiers; no new public scalar type or SDK surface was added.
- The tokenizer owns the fidelity fix, so CLI parse, source-slot loaders, and future LSP diagnostics use the same token stream.
- The two remaining sampled HOI4 parse failures have raw comment-stripped brace balance one, so they are tracked as corpus evidence rather than a parser regression from this slice.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Linear status could not be updated from this environment.
- This preserves scripted scalar text but does not semantically validate bracket expressions, fallback defaults, or HOI4 dynamic values.

## Next

- Continue parser hardening from real HOI4 samples, then move back toward generic module compilation behavior when parser scalar fidelity is less lossy.
