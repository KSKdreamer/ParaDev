# Collection Metadata Keys Progress

Date: 2026-06-07 11:48

Linear: TAL-294. Read/write attempts still returned
`UNAUTHORIZED; Session expired. Please re-authenticate.`

## Done

- Threaded family-owned `metadata_keys` through collection descriptor discovery.
- Collection descriptor `meta.yaml` and `collection.yaml` now accept the same
  project-local family metadata keys exposed in family inspection.
- Added manifest-backed coverage so descriptor metadata such as `scope` is
  preserved without a spurious `collection_metadata.unknown_key` warning.
- Updated build-flow docs for collection-owning family metadata contracts.

## Verification

- Red first: focused test failed because descriptor metadata key `scope`
  produced `collection_metadata.unknown_key`.
- Focused collection metadata-key test: `1 passed`.
- Related loader, module source, project build, project, and build manifest
  tests: `179 passed`.
- `rtk git diff --check`: passed.
- `rtk bash scripts/flake.bash --ci`: passed.
- Heaven-style scan on changed Python paths: passed.
- Full suite: `285 passed`.

## Risks Or Blockers

- Linear OAuth/session is expired, so TAL-294 could not be updated from this
  loop.

## Next

- Continue aligning collection descriptor behavior with module source behavior,
  especially any remaining registry-backed discovery contracts.
