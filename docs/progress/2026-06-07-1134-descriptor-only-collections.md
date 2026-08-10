# Descriptor-Only Collections Progress

Date: 2026-06-07 11:34

Linear: TAL-294. Read/write attempts still returned
`UNAUTHORIZED; Session expired. Please re-authenticate.`

## Done

- Made generic collection-source families emit descriptor-owned PDX,
  localization, and copy artifacts even when a collection has no member modules.
- Covered direct `plan_build(...)` behavior and manifest-backed
  `Project.build(...)` discovery for descriptor-only collections.
- Verified descriptor-only collection outputs stay visible through artifact,
  asset, source-map, and summary payloads.
- Updated build-flow docs so users know they can scaffold collections before
  adding modules.

## Verification

- Red first: focused tests failed because descriptor-only collections produced
  no artifacts.
- Focused descriptor-only collection tests: `2 passed`.
- Related simple family, project build, project, and build manifest tests:
  `187 passed`.
- `rtk git diff --check`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- Heaven-style scan on changed Python paths: passed.
- Full suite: `282 passed`.

## Risks Or Blockers

- Linear OAuth/session is expired, so TAL-294 could not be updated from this
  loop.

## Next

- Continue hardening generic module compilation from the user-visible inspection
  surface, especially places where descriptor scaffolds and member modules
  should behave consistently.
