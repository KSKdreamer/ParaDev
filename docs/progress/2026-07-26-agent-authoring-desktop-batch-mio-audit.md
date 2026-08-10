# Agent Authoring, Desktop Batch Creation, And MIO Audit

Date: 2026-07-26 SGT

## Summary

- Added a first-class, stdout-safe `paradev mcp serve` entrypoint for
  plan-first project authoring. Its four runtime tools expose templates,
  authoring paths, authoring plans, and guarded multi-module creation.
- Added a repository-local ParaDev authoring skill with a PIHC3 five-idea
  example. A real MCP dry plan produced five creates and fifteen source files
  without writing a demo module.
- Added a transactional desktop batch-creation dialog backed by the same SDK
  plan, exact plan hash, schema, and recovery contract as the CLI, REST, and
  MCP surfaces.
- Fixed two local HeavenBase integration defects: wrapped typed `Args`
  descriptions now parse correctly, and explicit Toolkit JSON schemas now
  survive FastMCP export.
- Audited PIHC3 Military Industrial Organization data and compilation. The
  current compatibility family compiles, and the next native family and tree
  projection slice is documented.

This checkpoint completes the MCP/skill, polished batch GUI, and MIO
investigation items from
`2026-07-26-transactional-authoring-pihc3-bop.md`. The larger continuous
ParaDev/PIHC3 modularization and publication-hardening objective remains active.

## First-Class Agent Authoring

`paradev mcp serve` starts a silent stdio MCP server with these runtime tools:

- `project_templates`
- `project_authoring_path`
- `project_authoring_plan`
- `project_create_modules`

The creation tool remains plan-first and force-free. An apply must repeat the
reviewed request with `write=true` and the exact state-sensitive `plan_hash`.
Its published schema preserves the one-of family/template selector, closed
nested objects, non-empty identifiers, and the SDK-owned 256-row batch limit.

ParaDev currently pins published `heavenbase==0.1.2.1`. ParaDev therefore owns
a narrow `create_authoring_mcp_server()` compatibility adapter that constructs
FastMCP `FunctionTool` objects directly while retaining HeavenBase execution
and serialization hooks. The equivalent general fix is also implemented and
tested in the local HeavenBase checkout for its next patch release.

The reusable skill lives at `.agents/skills/paradev-authoring/`. It teaches an
agent to discover an authoring-ready template, preview a complete batch, show
diagnostics and file paths, obtain approval, and apply the unchanged plan.

The real PIHC3 demonstration requested five ideas named A through E with
civilian-industry modifiers of 2%, 5%, 8%, 12%, and 16%. A live MCP preview
returned:

| Result | Value |
| --- | --- |
| Planned module creates | 5 |
| Planned source files | 15 |
| Files per module | `meta.yaml`, `def.txt`, `main.loc` |
| Writes performed | 0 |

No `paradev_qa_*` or demonstration module directories remain in PIHC3.

## Desktop Batch Authoring

The module editor now offers a generic batch-create dialog for every
authoring-ready template. It supports typed template fields, per-row template
selection, multiple source roots, up to 256 rows, and Unicode-normalized,
case-insensitive duplicate protection.

The interaction is transactional:

1. Preview renders the complete SDK plan and freezes its exact hash.
2. Any request edit invalidates that preview.
3. Apply locks the in-flight request and sends the unchanged request and hash.
4. The service boundary validates the response schema, selector, project root,
   family, object id, files, state, and recovery-path containment.
5. Successful or blocked outcomes are explicit; contradictory transport
   states fail closed.

Retained rollback transactions are surfaced in both the workspace banner and
the dialog with safe Open and Dismiss actions. The modal traps focus, restores
focus to its launcher, supports Escape, and has complete English and Chinese
copy.

Browser QA used the real PIHC3 project rather than a fixture. The same five-row
request previewed five creates and fifteen files with plan hash
`fffdf5488278a6d5149f998c631dff65281b1c5a21c0e51ea5a61d3fef0c4488`.
Apply was intentionally not pressed. The dialog was checked in light, dark,
and Anthropic themes, at the normal desktop viewport and at 720 by 800 pixels.
Escape from the first object-id input closed the dialog and restored focus to
Batch create.

## HeavenBase Compatibility Fixes

The local HeavenBase checkout now:

- keeps the active parameter key while appending wrapped, typed Google-style
  `Args` descriptions; and
- builds FastMCP `FunctionTool` instances with each Toolkit tool's explicit
  input schema, preserving nested JSON Schema constraints while retaining
  inferred structured output behavior.

ParaDev's public MCP argument summaries remain physically single-line as a
compatibility measure for the published 0.1.2.1 parser. They can be relaxed
after a fixed HeavenBase patch is published and pinned.

## PIHC3 Compilation And MIO Audit

The final strict, write-free PIHC3 plan passed:

| Check | Result |
| --- | --- |
| Modules | 18,032 |
| Collections | 78 |
| Planned artifacts | 37,558 |
| Diagnostics | 0 |
| Errors | 0 |
| Blocked | false |

The previously verified full publication remains 37,559 final artifacts with
zero diagnostics. The extra final artifact is the project-wide postprocessed
output created during emission.

The existing `military_industrial_organization_component` compatibility family
contains seven modules and compiles in a strict targeted build to 69 artifacts
with zero diagnostics. The corpus includes organization, trait, policy, weight,
and support data, but the current project diagram projection is focus-specific
and only exposes MIO metadata summaries.

The recommended next implementation slice is:

- native `military_industrial_organization`,
  `military_industrial_organization_policy`, weight, and support families;
- about 72 organization/policy modules with co-located PDX and localization;
- a family-owned tree projection rather than focus-specific expansion;
- PDX AST round-trip coverage for trait links; and
- derived summaries in hidden cache data rather than user-maintained
  `meta.yaml`.

That slice is documented in
`projects/PIHC3/docs/migration/46-military-industrial-organizations.md`; it was
audited but not implemented in this checkpoint.

## Verification

| Gate | Result |
| --- | --- |
| ParaDev complete fast suite | 1,636 passed; 2 expected skips |
| Local HeavenBase complete fast suite | 828 passed; 1 expected skip; 10 warnings |
| Desktop Vitest | 1,159 passed across 64 files |
| Desktop production build | passed; existing large-chunk advisory only |
| Tauri formatting and `cargo check` | passed |
| Tauri Rust tests | 64 passed across 3 suites |
| Strict real PIHC3 dry plan | 18,032 modules; 78 collections; 37,558 artifacts; 0 diagnostics |
| Authoring skill validator | passed |
| README synchronization | both generated targets current |
| Black and Flake8 | passed in ParaDev and HeavenBase |
| Heaven-style production scans | passed for changed ParaDev and HeavenBase integration files |
| Repository diff whitespace checks | passed before this note; rerun at final handoff |

The broad ParaDev test file scan still reports established direct `pathlib`
and `json` test-harness imports. Changed production integration files have no
banned imports, and no unrelated test-harness rewrite was folded into this
checkpoint.

## Repository State

No files were staged, committed, or pushed.

Several required additions are still untracked, including the authoring skill,
batch dialog and tests, publication helpers, and MCP/adversarial tests. PIHC3's
deleted balance-of-power component assets and their untracked co-located
replacements form one logical migration and must be staged together if a
commit is later requested.

The untracked `projects/PIHC3/assets/loadingscreens/` directory is about 168 MB
and was not created, modified, deleted, or staged by this checkpoint. Its
Git/LFS policy needs explicit review before publication. Unrelated pre-existing
HeavenBase changes in serialization tests and helpers were also preserved.

## Remaining Work

- Publish the local HeavenBase docstring and FastMCP schema fixes as a patch,
  then bump ParaDev's dependency from 0.1.2.1. Until then, keep ParaDev's
  compatibility adapter.
- Persist per-tool schema overrides in serialized HeavenBase Toolkit manifests.
  Ephemeral ParaDev MCP construction is exact, so this is not a current runtime
  blocker.
- Add a compatibility lane for the next FastMCP major release. The declared
  dependency is `>=3.0` without an upper bound; this checkpoint verified 3.4.1
  and 3.4.2.
- Continue consolidating user-facing `*_component` and
  `*_asset_component` families into single-source module folders, with a full
  strict compile after each family.
- Implement the documented native MIO families and family-owned tree
  projection after selecting the desired source-folder contract.
- Continue publication hardening: portable fail-closed behavior, transactional
  stale-output removal, retained-transaction inspection/recovery commands, and
  narrower protection against non-cooperating external writers.
