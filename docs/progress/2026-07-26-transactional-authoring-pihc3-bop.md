# Transactional Authoring And PIHC3 Balance-Of-Power Consolidation

Date: 2026-07-26 SGT

## Summary

- Kept ParaDev compatible with local HeavenBase 0.1.2.1 and reduced the real
  PIHC3 dry-plan time by adding the safe C-backed YAML loader path upstream.
- Hardened full, cached, and targeted publication with project locks,
  descriptor-anchored roots, ownership ledgers, and no-churn cached writes.
- Consolidated PIHC3's eight balance-of-power records so definition,
  localization, graphics, and interface assets live in one
  `balance_of_power` module folder. The separate
  `balance_of_power_asset_component` family and its migration-only tooling are
  gone.
- Added guarded multi-module creation across the Python SDK, CLI, REST,
  desktop bridge, generated frontend contract, and a real HeavenBase MCP
  toolkit. A five-idea request with 2%, 5%, 8%, 12%, and 16% civilian-industry
  modifiers now plans and applies through one reviewed transaction.
- Simplified the PIHC3 starter idea template to title-only `meta.yaml`,
  object-id-matched pictures, a numeric `cic` input, optional modifier PDX, and
  lower-case `_desc` localization.

## Transactional Module Creation

`Project.create_modules(...)` is plan-first. Each request selects exactly one
family or template, supplies an object id and values, and targets one configured
source root. Apply requires the exact state-sensitive `plan_hash`; there is no
force mode.

The plan hash includes ordered requests, rendered byte digests, statuses,
diagnostics, filesystem identities, and source/project locations. A stale hash,
duplicate target, partial or divergent existing module, or concurrent target
blocks the batch. An explicit fresh plan whose modules already match is an
idempotent no-op.

The writer stages every file before publishing any module. Descriptor-anchored
no-follow operations, create-only hard links, inode-aware rollback quarantine,
and retained recovery transactions prevent a concurrent owner from being
overwritten or deleted. Catalog projections run only after the complete source
commit succeeds.

The same `paradev.sdk.module_batch.v1` payload is available through:

- `Project.create_modules(...)`;
- `paradev module-batch-create`;
- `POST /projects/modules/create-batch`;
- frontend operation `module.create_batch`, including the Python desktop
  helper, Tauri command, and TypeScript `createModules(...)` service;
- MCP tool `project_create_modules` from
  `create_authoring_mcp_toolkit()`.

The MCP Toolkit, Tool, and serializer all use ParaDev's isolated HeavenBase
resolver and config authority. A real FastMCP client schema lookup and tool call
are covered by tests.

## PIHC3 Compile Results

The consolidated balance-of-power corpus and the simplified idea template pass
strict compilation against the real PIHC3 tree:

| Check | Result |
| --- | --- |
| Strict dry plan | 18,032 modules; 78 collections; 37,558 artifacts; 0 diagnostics; not blocked |
| Full artifact publication | 18,032 modules; 78 collections; 37,559 final artifacts; 0 diagnostics |
| Cached rebuild | ownership ledger and artifact mtimes unchanged |
| Targeted partial rebuild | six C01 outputs restored exactly; unrelated C02 hash and mtime unchanged |
| Five new idea fixture | 5 modules; 12 artifacts; 0 diagnostics |

The one-artifact difference between the full final output and the dry plan is
the project-wide postprocessed artifact created during emission.

## Performance

- Replaced quadratic publication membership checks with indexed planning.
  Real full PIHC3 publication fell from an observed eight-minute stall to about
  one minute and fifty-two seconds.
- Avoided cached building-icon and project postprocess rewrites when bytes did
  not change.
- Replaced repeated global module sorting with a heap-based merge.
- Added safe YAML C-loader selection in local HeavenBase. The same strict
  PIHC3 dry plan improved from about 52.6 seconds to about 32.9 seconds in the
  isolated comparison.

## Verification

| Gate | Result |
| --- | --- |
| ParaDev complete fast suite | 1,633 passed; 2 expected skips |
| Module scaffold and batch concurrency gate | 42 passed |
| CLI/MCP focused gate | 14 passed, including a real FastMCP client call |
| REST/desktop bridge | 98 passed |
| Architecture and generated-contract gate | 91 passed |
| Desktop Vitest | 1,137 passed |
| Desktop production build | passed |
| Tauri Rust library | 64 passed |
| PIHC3 basic idea template contract | passed |
| Local HeavenBase utility regressions | 24 passed; 1 environment-dependent skip |
| Black, Flake8, Heaven-style scan, and diff checks | passed; scanner reports only established utility-import exceptions |

## Remaining Work

- Package the authoring MCP toolkit behind a first-class stdio/server command
  and add a reusable agent skill so users do not need custom embedding code.
- Surface multi-module creation as a polished GUI workflow with editable
  previews, saved requests, and recovery guidance.
- Continue folding the remaining hidden `*_component` and
  `*_asset_component` migration families into author-facing module folders,
  one compile-verified family at a time.
- Add automatic inspection/recovery commands for retained module transactions.
  Filesystem exception and concurrency safety are covered; a portable
  multi-directory, single-syscall crash commit is not available.
- Finish the remaining publication hardening: fail-closed Windows parity,
  transactional stale-output removal, and narrower protection against
  non-cooperating external writers.
- Investigate Military Industrial Organization tree authoring after the core
  module cleanup and batch GUI are stable.
