# Collection Build Explain Progress

Date: 2026-06-07 11:19

Linear: TAL-294. Read and write attempts still returned
`UNAUTHORIZED; Session expired. Please re-authenticate.`

## Done

- Added `build-explain` collection targets to the SDK and CLI.
- Collection explanations now include collection-owned artifacts, descriptor
  source slots, contributing descriptor and member-module sources, member
  dependency rows, related diagnostics, and a graph subset.
- Updated build graph collection filtering so collection-owned artifacts include
  all contributing source edges, not only descriptor-owned source rows.
- Updated build-flow docs for `--collection` explain targets.

## Verification

- Red first: focused SDK/CLI tests failed because `Project.build_explain(...)`
  did not accept `collection_id` and `paradev build-explain` had no
  `--collection` option.
- Focused explain tests: `13 passed`.
- Related project/build manifest tests: `173 passed`.
- `rtk git diff --check`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- Heaven-style scan on changed Python paths: passed.
- Full suite: `278 passed`.

## Risks Or Blockers

- Linear OAuth/session is expired, so TAL-294 could not be updated from this
  loop.

## Next

- Continue generic compiler inspection and first-slot compiler hardening, then
  move toward the next module compilation slice.
