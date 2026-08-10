# HeavenBase 0.1.2.0 Local Migration

Date: 2026-07-18 14:33 SGT

## Summary

- Upgraded the existing HeavenBase migration branch from `0.1.1.6` to local and remote master `0.1.2.0` at exact commit `7f4efc47fc794b52a58496b88cec2402289a1175`.
- Verified that the branch's Context Registry migration, Extension API, LLM engine, and canonical file-URI changes cover every ParaDev API break found against HeavenBase 0.1.2.0.
- Made the temporary editable-source workflow target ParaDev's own `.venv` and remain active across the repository's test, lint, environment-check, native-web, and Tauri launch wrappers.
- Removed 16 SQLite portability warnings by renaming the internal dynamic HOI4 entity field from `desc` to `description`; the public `Catalog.desc` projection and query payload remain unchanged.
- Preserved the user's existing dirty ParaDev and PIHC3 checkouts by extending the clean `codex/heavenbase-0116-migration` worktree and draft PR.

## Dependency Contract

- `requirements.txt` declares `heavenbase==0.1.2.0`.
- uv resolves HeavenBase from the exact upstream Git revision because 0.1.2.0 is not yet published on PyPI.
- `uv.lock` records version 0.1.2.0, the upstream repository, and the exact commit SHA.
- Local HeavenBase source testing uses:

  ```bash
  rtk env HEAVENBASE_SOURCE=/Users/magolor/Projects/HeavenBase/HeavenBase \
    bash scripts/sync-env.bash --heavenbase-source
  ```

- A source-override marker is written inside `.venv`. Repository wrappers set uv's no-sync mode while the recorded source remains valid. Running plain `scripts/sync-env.bash` removes the marker and restores the pinned Git revision.
- The first implementation accidentally installed the override into the active `conda main` environment. That environment was restored to its prior published HeavenBase 0.1.1.5 package; `conda dev` remains the local-source 0.1.2.0 environment.

## Data And API Safety

- Legacy `hb_config_layers` rows migrate lazily and idempotently into the Context v1 Registry.
- Existing Context scopes are never overwritten, the legacy table remains available as forensic evidence, and a durable migration marker prevents deleted scopes from being resurrected.
- Scope versions, tombstones, timestamps, values, and latest generation are preserved.
- Failed validation or writes do not leave a partial migrated scope.
- Catalog smoke/write/query behavior remains stable under HeavenBase 0.1.2.0.
- The internal HOI4 `description` field derives the same bounded public `catalog.desc` text and retains the complete original payload in `data`.

## Verification

| Gate | Result |
| --- | --- |
| Exact pinned Git import | HeavenBase 0.1.2.0 at commit `7f4efc47` |
| Final pinned environment/config/warning regression | 21 passed |
| Editable local-source import before and after wrappers | HeavenBase 0.1.2.0 from `/Users/magolor/Projects/HeavenBase/HeavenBase/src` |
| Environment override behavioral tests | 5 passed |
| Local-source config/catalog/LLM/OpenAPI focused suite | 19 passed, 16 warnings |
| Independent `conda dev` focused suite | 26 passed |
| Reserved SQLite name regression and catalog behavior | 3 passed; warnings reduced from 16 to 0 |
| Repository-wide Python fast gate | 1,263 passed, 3 warnings in 5m31s |
| Desktop Vitest gate | 780 passed across 52 files |
| REST service contract slice | 41 passed |
| Black and Flake8 | 139 files unchanged; passed |
| Bash syntax | `_env`, sync, test, flake, and run wrappers passed |
| Environment and lock drift | passed |
| Python sdist and wheel build | passed |
| Diff whitespace check | passed |

The full `tests/test_hb.py` suite is intentionally slow; its migration-critical smoke and relative-SQLite-write nodes passed independently, and all non-slow HB tests are included in the repository-wide fast result.

## Open Release Blockers

1. The built Python wheel declares unpublished `heavenbase==0.1.2.0`. `[tool.uv.sources]` is a uv workspace rule and is not included as a pip resolution source in wheel metadata. Publishing HeavenBase 0.1.2.0 or adopting an exact PEP 508 Git dependency is required before the Python release workflow can install the built wheel.
2. The Tauri binary still derives the ParaDev repository root from Rust's compile-time `CARGO_MANIFEST_DIR` and launches `uv run python` from that checkout. The bundle contains no Python backend or runtime resources. An installed app would therefore depend on the builder's source tree and cannot yet be called portable.
3. The repository-embedded Heaven Style skill remains 0.1.1.5. The installed 0.1.2.0 skill comes from an uncommitted Blueprint source tree, and its current mirror script merges without deleting moved files or recursively excluding junk. Skill mirroring is deferred until that canonical source and replacement workflow are stabilized.

## Next

- Commit and push this reviewed 0.1.2.0 migration checkpoint, update PR #3, and merge it after remote checks.
- Replace the Tauri checkout-dependent backend with a bundled sidecar/runtime contract and add an installed-app smoke test.
- Validate PIHC3 using the migrated runtime, then land the already-audited dirty PIHC3 changes as separate commits rather than one combined change.
- Start the 766-focus vertical migration described in the companion PIHC3 entity parity audit.
