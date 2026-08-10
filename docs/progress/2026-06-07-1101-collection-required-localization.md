# Collection Required Localization Progress

Date: 2026-06-07 11:01

Linear: TAL-294. Read and write updates were attempted, but the Linear connector
returned `UNAUTHORIZED; Session expired. Please re-authenticate.`

## Done

- Added generic collection-source required localization validation for collection descriptor `.loc` sources.
- Allowed `{collection_id}` in `required_loc_keys` templates for declarative and Python-backed families.
- Updated docs and tests for collection diagnostics with resolved source context.

## Verification

- Red first: focused collection localization tests failed because `{collection_id}` was not yet accepted in `required_loc_keys`.
- Focused tests: `2 passed`.
- Related build tests: `187 passed`.
- Formatting and flake: passed.
- Heaven-style scan on changed Python paths: passed.
- Full suite: `272 passed`.

## Risks Or Blockers

- Linear OAuth/session is expired, so TAL-294 could not be updated from this loop.

## Next

- Continue collection-aware generic compiler rows and diagnostics, then proceed to the next generic module compilation slice.
