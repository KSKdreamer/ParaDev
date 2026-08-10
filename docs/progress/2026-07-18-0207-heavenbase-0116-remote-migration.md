# HeavenBase 0.1.1.6 Remote Migration

Date: 2026-07-18 02:07 SGT

## Summary

- Migrated ParaDev's remote-HeavenBase stage from the legacy integration to HeavenBase `0.1.1.6` at exact upstream commit `5fff322e093fe91bc76fbe7e7ca5379b1281733e`.
- Added a lossless, idempotent migration from the legacy `hb_config_layers` table to the HeavenBase Context v1 Registry contract.
- Replaced removed HeavenBase extension and LLM materialization APIs with their current `Extension` and `LLMEngine.apply(...)` equivalents.
- Kept initialization lazy: importing `paradev.config` neither creates a fresh database nor opens or mutates an existing one; migration begins on first config access.
- Synchronized stale generated API-contract assertions that predated this worktree.

## Remote Dependency Contract

- `requirements.txt` identifies the required release as `heavenbase==0.1.1.6`.
- uv resolves HeavenBase from the exact `origin/master` Git commit because PyPI currently publishes only through `0.1.1.5`.
- `uv.lock` records version `0.1.1.6`, the upstream repository, and the exact commit SHA.
- `scripts/sync-env.bash --check --no-heavenbase` confirms the environment and lockfile are synchronized.

## Configuration Data Safety

- The migration validates every legacy row before writing any migrated scope.
- Scope versions, tombstones, timestamps, values, and the latest legacy generation are preserved in the new Registry representation.
- The original `hb_config_layers` table remains untouched as a forensic source.
- Existing Context v1 scopes take precedence and are never overwritten.
- A separate durable migration marker prevents a deliberately deleted scope from being resurrected on restart.
- Compare-and-swap conflicts retry without replacing unrelated concurrent Registry changes.
- Failed or malformed migrations close the Context and leave the new Registry scope empty.

## Verification

- Configuration migration regression suite: `15 passed`.
- Configuration, desktop selection, and CLI contract suite: `244 passed` with 16 upstream/runtime warnings.
- HeavenBase integration suite: `23 passed` with 224 warnings in 10m59s.
- Focused API-reference and architecture contract checks: `10 passed`.
- Focused extension and database-URI regressions: `2 passed`.
- Repository-wide fast suite: `1257 passed` with 306 warnings in 5m41s after the final lazy-startup fix.
- Repository-wide Ruff and formatting gate: passed; all 138 Python files were unchanged by the formatter.
- Environment/lock drift check: passed.

## Findings And Risks

- Non-uv installation and packaging remain blocked until HeavenBase `0.1.1.6` is published to PyPI or ParaDev adopts an explicit Git requirement for those paths.
- The Heaven Style scanner reports baseline standard-library utility usage in large pre-existing desktop, adapter, and test modules. New configuration migration modules and the changed HOI4 adapter are clean; unrelated refactoring is deferred.
- The local-source stage is intentionally next. The local HeavenBase checkout reports `0.1.2.0`, contains unrelated local changes, and is behind its remote development branch, so it must be exercised as an explicit editable source without mutating that checkout.
- GUI audit found release blockers outside this migration slice: the Tauri bundle depends on a compile-time checkout path, first-run project creation is missing, and no packaging/end-to-end CI path exists yet.
- Entity audit found that focus and technology editing can update metadata or legacy drafts without guaranteeing canonical definition output, source-slot selection is ambiguous, and 134 aggregate legacy records need an explicit PIHC2-to-PIHC3 reconstruction path.

## Next

- Review the final publication diff, then commit, push, and merge this major remote-migration branch through a pull request.
- Exercise ParaDev against the existing local HeavenBase source checkout with a stable no-resync workflow.
- Start the GUI packaging/first-run block, followed by systematic PIHC3 entity parity and editor validation.
