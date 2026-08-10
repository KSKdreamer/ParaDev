# Descriptor Loc Copy Progress

Date: 2026-06-07 11:41

Linear: TAL-294. Read/write attempts still returned
`UNAUTHORIZED; Session expired. Please re-authenticate.`

## Done

- Made descriptor localization and copy artifacts emit independently from
  descriptor or member PDX entries.
- Added direct generic-family coverage for localization-only and copy-only
  descriptor collections.
- Added manifest-backed project coverage proving localization, asset, and
  source-map inspection still resolve collection-owned sources.
- Updated build-flow docs to state descriptor localization/copy outputs do not
  require a descriptor PDX source.

## Verification

- Red first: focused tests failed because collections with only descriptor
  localization/copy slots produced no artifacts.
- Focused descriptor loc/copy tests: `2 passed`.
- Related simple family, project build, project, and build manifest tests:
  `189 passed`.
- `rtk git diff --check`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- Heaven-style scan on changed Python paths: passed.
- Full suite: `284 passed`.

## Risks Or Blockers

- Linear OAuth/session is expired, so TAL-294 could not be updated from this
  loop.

## Next

- Continue hardening collection and module compiler behavior where partial
  authoring should still produce inspectable SDK/CLI output.
