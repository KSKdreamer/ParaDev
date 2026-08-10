# Collection Asset Constraint Progress

Date: 2026-06-07 11:26

Linear: TAL-294. Read/write attempts still returned
`UNAUTHORIZED; Session expired. Please re-authenticate.`

## Done

- Extended generic collection-owning families so collection descriptor copy
  slots are validated against declared `asset_constraints`.
- Kept module and collection asset diagnostics on the same helper path while
  preserving module-owned `module_id` diagnostics and adding collection-owned
  `collection_id` diagnostics.
- Covered manifest-declared `collection_source` families so descriptor assets
  block SDK/CLI builds and resolve through diagnostic source inspection.
- Updated build-flow docs to state that asset constraints apply to module and
  collection descriptor copy sources.

## Verification

- Red first: focused tests failed because collection descriptor copy slots did
  not produce asset constraint diagnostics.
- Focused collection asset tests: `2 passed`.
- Related simple family, project build, project, and build manifest tests:
  `185 passed`.
- `rtk git diff --check`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- Heaven-style scan on changed Python paths: passed.
- Full suite: `280 passed`.

## Risks Or Blockers

- Linear OAuth/session is expired, so TAL-294 could not be updated from this
  loop.

## Next

- Continue generic module compilation hardening, with the next slice focused on
  the smallest user-visible compiler behavior that still lacks registry-backed
  tests.
