# Collection Slot Inspection Progress

Date: 2026-06-07 11:11

Linear: TAL-294. Read and write attempts still returned
`UNAUTHORIZED; Session expired. Please re-authenticate.`

## Done

- Added descriptor `source_slots` to collection records when a collection is
  loaded from authored descriptor files.
- Added a collection manifest slot index and `Project.collections(source_slot=...)`
  filtering.
- Added `paradev collections --slot` for descriptor-slot filtering.
- Updated build-flow docs for collection descriptor source-slot inspection.

## Verification

- Red first: focused SDK and CLI collection-slot tests failed because
  `Project.collections(...)` did not accept `source_slot` and the CLI lacked
  `--slot`.
- Focused tests: `2 passed`.
- Related project/build manifest tests: `179 passed`.
- `rtk git diff --check`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- `rtk python .claude/skills/heaven-style/scripts/scan.py ...`: failed because
  that interpreter did not have `heavenbase`.
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py ...`: passed.
- Full suite: `274 passed`.

## Risks Or Blockers

- Linear OAuth/session is expired, so TAL-294 could not be updated from this
  loop.

## Next

- Continue making collection descriptors first-class in generic compiler
  inspection, then move into the next generic module compilation slice.
