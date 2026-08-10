# HeavenBase 0.1.2.1 And PIHC3 Clean Compile

Date: 2026-07-25 01:31 SGT

## Summary

- Upgraded ParaDev's unpublished HeavenBase dependency from 0.1.2.0 to local
  HeavenBase 0.1.2.1 at exact `dev-refactor` commit
  `5399682f3c6925b068391c5261018aa4f27d4a9d`.
- Ported ParaDev's config and Catalog integration to the refactored Context,
  workspace, extension, execution, and LLM authority contracts.
- Preserved the editable local-source workflow and made PIHC3's compile wrapper
  honor the recorded HeavenBase override instead of allowing `uv run` to
  replace it with the locked Git package.
- Completed a real PIHC3 `--clean` artifact build from scratch. The compact
  summary reports 18,175 modules, 78 collections, 37,555 artifacts, zero
  diagnostics, zero errors, and `blocked: false`.
- Preserved the existing dirty PIHC3 entity-compiler work and the older dirty
  ParaDev checkout. ParaDev compatibility work was isolated in the clean
  `codex/pihc3-portable-template-fixture` worktree.

## HeavenBase 0.1.2.1 Compatibility

- `heavenbase.Database` is now used from the package facade.
- `RowOp` is imported from `heavenbase.execution`.
- ParaDev's config Context reuses HeavenBase's validated packaged bootstrap and
  overrides only the ParaDev control database identity and file location. This
  retains the required SQLite override, dialect, and bootstrap tags.
- Temporary service workspaces now use the public
  `HeavenBase(..., detached=True)` lifecycle through one ParaDev-owned helper.
- The HOI4 extension uses `Extension.register()`, mapping-valued tags, and
  import-addressable generated Entity classes. Catalog writes resolve the
  canonical Entity classes owned by each workspace after extension replay.
- ParaDev's pytest bootstrap follows HeavenBase's 0.1.2.1 Context reset and
  config-authority contract.
- The offline LLM route regression uses the owning `DEFAULT_CONTEXT` rather
  than an unbound config-only authority.

## PIHC3 Compile Contract

- Project-local entity plugins import `system.entity_compiler` and
  `system.entity_records` through the project root placed on `sys.path`.
  Relative imports are not valid for ParaDev's standalone file-loaded plugin
  modules.
- `compile.bash` enables ParaDev's recorded local HeavenBase override after uv
  resolution. The call is guarded so the wrapper's isolated shell tests remain
  compatible with their minimal `_env.bash` fixture.
- The verified clean build used the current PIHC3 GUI-smoke manifest and wrote
  its configured output to `build/gui-smoke-mod`.
- Generated output measured approximately 1.3 GB, with approximately 251 MB of
  `.paradev` build metadata.

## Verification

| Gate | Result |
| --- | --- |
| Local HeavenBase source sync | 0.1.2.1 editable checkout at exact `5399682f3c` commit |
| PIHC3 clean artifact compile | passed |
| PIHC3 compact build summary | 18,175 modules; 78 collections; 37,555 artifacts; 0 diagnostics; 0 errors |
| PIHC3 compile-wrapper and entity-family regressions | 21 passed |
| ParaDev config and project regressions | 289 passed |
| ParaDev complete fast gate | 1,539 passed, 1 expected skip, 2 warnings |
| Black and Flake8 | 162 files unchanged; passed |
| Environment and generated-lock drift | passed |
| Python sdist and wheel build | passed |

The Heaven Style scanner still reports the repository's existing direct
`json`, `os`, `pathlib`, and `subprocess` imports in older touched files. This
migration adds no new scanner violation.

## Remaining PIHC3 Test Drift

The complete `PIHC3-GUI-Smoke/scripts/tests` collection initially produced 212
passes and six failures. The three compile-wrapper failures were caused by the
new override hook and are fixed. The remaining three exact-corpus assertions
predate this checkpoint's changes: the dirty PIHC3 worktree already contains
`legacy/entities.json` plus expanded assignment provenance in
`HOI4DEV_ENTITIES/meta.yaml`, while those older tests still require the
previous 182-file manifest and metadata key set. They do not block compilation,
and the authoritative clean build is green, but the corpus assertions should
be updated or the in-progress entity data should be finalized together.

## Next

- Review and commit the ParaDev 0.1.2.1 compatibility checkpoint separately
  from the existing PIHC3 entity-compiler work.
- Reconcile the three PIHC3 exact-corpus tests with the intended
  `legacy/entities.json` and assignment-provenance contract.
- Exercise the packaged GUI against the same 0.1.2.1 worktree after the PIHC3
  corpus contract is finalized.
