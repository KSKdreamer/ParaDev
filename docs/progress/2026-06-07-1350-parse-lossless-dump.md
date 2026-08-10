# 2026-06-07 13:50 - Parse Lossless Dump

## Scope

- Added `paradev parse --dump --json` so CLI callers can request the lossless `PDXBlock.dump()` payload alongside the existing lossy `data` projection.
- Kept the default `paradev.pdx.parse.v1` payload unchanged unless `--dump` is passed.
- Added CLI regression coverage that reloads the dump through `PDXBlock.load(...)` and verifies comments, duplicate entries, and file-extension metadata survive.
- Updated the build workflow docs to explain when scripts should request the lossless dump.

## Verification

- Red: `rtk uv run pytest tests/test_cli.py::test_parse_can_include_lossless_dump_json` failed because `--dump` was not a supported parse option.
- Green: `rtk uv run pytest tests/test_cli.py::test_parse_can_include_lossless_dump_json` passed.
- Related: `rtk uv run pytest tests/test_cli.py tests/test_pdx_token.py tests/test_pdx_roundtrip.py` passed with 32 tests.
- Diff hygiene: `rtk git diff --check` passed.
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/cli.py tests/test_cli.py` passed with `OK: 2 file(s) - no banned imports`.
- Flake: `rtk bash scripts/flake.bash --ci` passed with 46 files unchanged.
- Full tests: `rtk bash scripts/test.bash` passed with 306 tests.

## Review Notes

- The `dump` field is additive and emitted only for successful parses that pass `--dump`.
- The existing `data` projection remains the lightweight default for scripts that do not need comments, duplicate entries, or scalar annotations.
- Linear sync to TAL-291 was attempted, but the API session is expired and returned `UNAUTHORIZED`; local progress continues until the session is refreshed.
