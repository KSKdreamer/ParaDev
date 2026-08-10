---
id: workflow-architect
title: Architect workflow
enabled: true
audience: architect
keywords: [architecture plan, architecture review, periodic architecture review, agile design, design smells, dependency review, module design, refactor plan, goals roadmap, api standard table, docs cleanup, organize docs, short-term goals, mid-term goals, long-term goals, implementation plan, design doc]
description: Use when organizing docs, designing or reviewing architecture, drafting refactor plans, updating goals, or producing step-by-step execution plans without implementing code.
---

# Architect Workflow

## When to use

Use this surface when the deliverable is **design and documentation**, not code. Typical triggers:

- Organize, deduplicate, or retire stale docs before a major effort.
- Design a new module or extension boundary before anyone writes implementation code.
- Review architecture health periodically or before a major release, refactor, provider/backend expansion, or repeated defect pattern.
- Draft a multi-slice refactor plan with registry seams, migration steps, and verification gates.
- Update short-, mid-, or long-term goals to match current code and roadmap reality.
- Produce an API standard table or cross-module interface contract for review.
- Write a step-by-step execution plan that an average engineer or agent can follow without rediscovering architecture in chat.

**Do not use** this workflow when the primary ask is:

- Implementing or fixing code → [../tasks/code.md](../tasks/code.md).
- Explaining existing behavior to a newcomer → [../tasks/code-explain.md](../tasks/code-explain.md).
- Syncing English docs to match already-shipped behavior → [../tasks/doc-sync.md](../tasks/doc-sync.md).
- Tracking GitHub/Linear status or orchestrating agents → [../tasks/manager.md](../tasks/manager.md).
- Resolving rule tradeoffs while coding a large change → [developer.md](developer.md) (implementation route).

The architect workflow may **read** any module or feature as evidence, but it must not anchor on one file or ticket. Start from repo mental model, goals, status, cross-cutting constraints, and current change pressure, then narrow to affected surfaces.

## Design philosophy gate

Every architect artifact must align with the Heaven Style principles in `SKILL.md`. Before proposing structure, run this gate:

| Principle | Architect check |
|-----------|-----------------|
| Minimal mental model | Can an average reader reconstruct the design from one page? |
| Registries over branches | Does the plan extend through registration APIs, not central `if` chains? |
| Shared infrastructure first | Are utilities/config routed through `heavenbase.utils` and `CM_HVNB`? |
| Break and fix, no shims | Does the plan update all call sites in-place without permanent v1/v2 APIs? |
| Compact, explicit Python | Do proposed APIs favor guard clauses, canonical OOP verbs, `raise_mismatch`? |
| Docs are part of the code | Will architecture pages, goals, and examples stay verifiable against source? |

Load rule files when the design touches their surface:

- Public API shape: `model`, `oop`, `name`, `types`
- Extension seams: `extension`, `compat`
- Docs and goals: `docs`
- Storage/query behavior: `sql`, `error`

For HeavenBase-lineage repos, read `docs/resources/architecture/mental-model.md` (or the project equivalent) before proposing cross-module interfaces.

## Agile architecture gate

Architecture is a continuous design activity, not a one-time document phase. Use agile principles to keep design tied to working software and real feedback:

| Agile principle | Architect check |
|-----------------|-----------------|
| Requirements change | Is the design aimed at the next verified change pressure rather than speculative future variants? |
| Working software | Are shipped behavior, tests, examples, and issue acceptance criteria treated as stronger evidence than stale diagrams? |
| Technical excellence | Do tests, CI, and refactoring capacity make the proposed change safe to execute? |
| Simple design | Does the design solve the current problem without needless patterns, layers, flags, or parallel APIs? |
| Continuous design | Does each slice include a feedback point where design can be revised from implementation evidence? |
| Collaboration | Are user, issue, roadmap, or maintainer concerns named instead of hidden behind generic architecture claims? |
| Useful documentation | Do diagrams and tables clarify decisions without becoming a substitute for code truth? |

Use SOLID, package principles, and patterns as diagnostic tools, not slogans:

- SRP and Common Closure: group responsibilities by reason to change.
- OCP and Heaven-style registries: extend behavior through registration APIs instead of reopening stable planners.
- LSP and ISP: keep public contracts substitutable and clients dependent only on methods they use.
- DIP, Stable Dependencies, and Stable Abstractions: high-level policy depends on abstractions; low-level details depend inward.
- ADP, REP, and Common Reuse: avoid dependency cycles, release reused units coherently, and avoid forcing consumers to depend on unrelated classes.

## Smell and dependency review

Run this review for new designs, refactor plans, and periodic architecture checks:

| Smell | Architect check |
|-------|-----------------|
| Rigidity | Does a small change force unrelated edits across layers? |
| Fragility | Do changes break unexpected behavior with no obvious dependency path? |
| Immobility | Are useful concepts too coupled to framework, storage, CLI, or provider details to reuse? |
| Viscosity | Is the easy change path the wrong architectural path? |
| Needless complexity | Are abstractions solving imagined requirements instead of current evidence? |
| Needless repetition | Is one rule, schema, default, or route duplicated across surfaces? |
| Opacity | Can an average maintainer reconstruct the system from names, docs, and tests? |

Also check package and dependency direction:

- Core business rules and high-level policies must not depend on databases, provider SDKs, UI/CLI adapters, generated artifacts, or external APIs.
- Volatile details depend on stable abstractions; stable modules expose abstractions when many callers depend on them.
- Dependency cycles are architecture findings. Break them in a slice plan or document an explicit waiver.
- Modules that change together belong together; modules reused together need coherent docs, tests, and release boundaries.

## Discovery workflow

Gather evidence before writing. Prefer live connectors; fall back to local git and docs.

### 1. Repo and environment

1. Read `AGENTS.md`, `docs/README.md`, and the docs authority map.
2. Note package version, default branch, release policy, and command wrappers from `pyproject.toml` and `AGENTS.md`.
3. Skim `src/<package>/` top-level layout and `__init__.py` public exports — map layers, not every file.

### 2. Docs inventory

1. List `docs/goals/`, `docs/resources/`, `docs/progress/`, architecture notes, generated artifacts, and sibling docs repos linked from `AGENTS.md`.
2. Mark each doc: **current**, **stale**, **planned-not-shipped**, **duplicate**, or **orphan**.
3. Identify the canonical English source for each user-facing claim (`README.en.md`, Mintlify root, mental-model page, etc.).

### 3. Codebase signals (breadth-first)

1. Read mental-model and extension-layout docs when present.
2. Scan registry/extension entry points: `register_*`, `extensions/`, `backends/`, `handlers/`, public facade modules.
3. Sample tests and examples that encode intended behavior; treat them as contracts.
4. Note compatibility re-exports, TODO markers, and duplicated planners — these often drive refactor plans.

### 4. Status and issues

1. Use Linear when available: active milestones, `In Progress` / `In Review` issues, blockers, rolling status comments, linked design threads.
2. Use GitHub/`gh` when available: open PRs, failing checks, review threads, recent merges on the default branch.
3. Read the latest `docs/progress/YYYY-MM-DD/README.md` when progress notes exist.
4. On auth or project-pressure failures, use [../failures/auth-secrets.md](../failures/auth-secrets.md) and [../failures/linear-pressure.md](../failures/linear-pressure.md).

### 5. Synthesis

Produce a short **current-state brief** (half page max):

- What the system is for, in one sentence.
- Layer map or module boundaries (table or diagram).
- Top mismatches between docs, goals, Linear claims, and code.
- Constraints and non-goals already recorded.
- Open questions that block a design decision.

Do not start detailed design until mismatches are listed. If scope is ambiguous, ask one focused question before proceeding.

## Periodic architecture review

Use a periodic review when the project has a cadence, reaches a release boundary, accumulates repeated defects, expands a provider/backend family, or shows architecture drift in docs, tests, or implementation.

1. **Scope** - name the package, module family, feature slice, release train, or whole-repo boundary under review.
2. **Comparison point** - cite the last review, last release, baseline branch, roadmap item, or current state if no previous review exists.
3. **Evidence** - inspect architecture docs, current goals, latest progress, public exports, dependency entry points, registry seams, tests, examples, open issues, and recent PRs/commits when available.
4. **Change pressure** - list what actually changed: user requests, new backends/providers, schema/storage behavior, defects, onboarding pain, or repeated code-review findings.
5. **Smell matrix** - score rigidity, fragility, immobility, viscosity, needless complexity, needless repetition, and opacity with concrete file/doc/test evidence.
6. **Dependency matrix** - identify inward dependencies, cycles, unstable dependencies, detail leakage into policy, and extension seams that require central edits.
7. **Fitness checks** - name the tests, examples, CI checks, docs checks, or probes that prove the architecture remains changeable.
8. **Actions** - classify recommendations as **now**, **next**, **defer**, or **waive**. Avoid broad rewrites unless the evidence shows repeated change cost.
9. **Next trigger** - record the next review trigger or cadence only when the project actually uses one.

Deliverable: an **architecture review** with scope, evidence, findings, prioritized actions, verification expectations, and docs/issue updates. Store durable reviews under a project-approved path such as `docs/reports/reviews/`, `docs/resources/architecture/`, `docs/progress/YYYY-MM-DD/`, or the owning issue when a tracker is the source of truth.

## Doc organization and cleanup

When the task includes docs hygiene:

1. **Consolidate** — one canonical page per topic; merge duplicates; link out instead of copying prose.
2. **Retire** — move superseded pages to a dated progress note or delete with a one-line redirect in the docs menu; do not leave contradictory architecture pages.
3. **Relabel** — separate *shipped*, *in progress*, and *planned* sections; never describe planned behavior as current.
4. **Anchor** — ensure `docs/README.md` lists goals, resources, progress, and the mental-model entry.
5. **Defer translation** — route Chinese MDX work to [../tasks/doc-trans.md](../tasks/doc-trans.md); architect output stays English unless the user requests translation.

Deliverable: a **docs change list** with file path, action (`keep`, `merge`, `rewrite`, `retire`, `create`), owner slice, and verification (grep, link check, Mintlify validate when applicable).

## Module design output

For a new module or extension, produce a design doc with this structure:

### Required sections

1. **Problem and success criteria** — user-visible outcome and measurable done state.
2. **Non-goals** — explicit exclusions to prevent scope creep.
3. **Layer placement** — which architectural layer owns the module; what it may import; what must not import it.
4. **Public surface** — classes, functions, CLI commands, registry hooks; prefer `heavenbase as hb` in examples.
5. **API standard table** — see template below.
6. **Data and control flow** — read/write paths, registry interactions, config keys via `CM_HVNB`.
7. **Extension seam** — which `register_*` API owns new behavior; no central routing edits.
8. **Migration / break-and-fix** — rename map, call-site sweep strategy, forbidden shims.
9. **Tests and examples** — behavior contracts agents must implement.
10. **Docs touch list** — mental-model, reference pages, goals, progress note, Mintlify pages.
11. **Slices** — ordered implementation slices with acceptance criteria and verification commands.
12. **Risks and waivers** — anything that needs explicit human approval.

Add an **Agile feedback gates** section before handoff: tests, demos, review checkpoints, or issue acceptance checks that let the design adapt after each implementation slice.

### API standard table template

Use one row per public symbol. Keep names aligned with [../rules/code/oop.md](../rules/code/oop.md) and [../rules/code/name.md](../rules/code/name.md).

| Symbol | Kind | Layer | Inputs | Returns | Raises | Registry seam | Doc page | Test anchor |
|--------|------|-------|--------|---------|--------|---------------|----------|-------------|
| `register_foo` | function | extensions | `name: str`, `builder: Callable` | `None` | `ValueError` on duplicate | `ext.register_foo` | `reference/foo.md` | `tests/test_foo.py::test_register` |

Add columns only when they reduce ambiguity for implementers. Do not duplicate full signatures if a single module file will be the source of truth — the table is the contract checklist.

## Refactor plan output

For cross-module refactors, produce a plan doc with:

1. **Trigger** — mismatch, tech debt, or goal that forces the change.
2. **Invariant checklist** — mental-model rules that must still hold after the refactor.
3. **Before / after map** — modules, public imports, registry ownership.
4. **Slice breakdown** — each slice is independently reviewable and verifiable:

```markdown
### Slice N: <short title>

**Goal:** one sentence.

**Touch:** paths/modules (bullet list).

**Steps:**
1. Concrete action an agent or human can execute.
2. ...

**Acceptance criteria:**
- [ ] Observable outcome.

**Verification:**
- `rtk bash scripts/test.bash <target>`
- `rtk bash scripts/flake.bash --ci --paths <paths>`

**Docs:** files to update in the same slice or explicitly deferred.

**Non-goals:** what this slice must not do.
```

5. **Break-and-fix sweep** — ordered delete/rename steps; no parallel old/new APIs unless waived.
6. **Rollback posture** — git revert boundaries per slice, not big-bang undeployable plans.

Hand implementation slices to [../tasks/code.md](../tasks/code.md) and rule-heavy execution to [developer.md](developer.md).

## Goals update workflow

Align `docs/goals/` (or project equivalent) with evidence from discovery.

### Short term (weeks)

- Bullet items tied to **current train** work; each item links to a Linear issue or names an owner slice.
- Mark completed items with date; move finished narrative to progress notes when it clutters the horizon view.
- Prefer coherence and doc/code alignment before new features.

### Mid term (1–3 months)

- Routing depth, persistence gaps, docs-site milestones, template/skill alignment — themes, not ticket dumps.
- Each theme states dependency on short-term items when order matters.

### Long term (3+ months)

- Train candidates (`0.2` etc.), architectural bets, explicit **non-goals** that prevent over-engineering.

### Standing non-goals

- Keep a short permanent list (no second planner, no central routing branches, no permanent shims) when the repo follows HeavenBase lineage.

Deliverable: a **goals diff** — proposed edits to `roadmap.md`, `current.md`, or `docs/goals/README.md` with rationale per bullet.

## Step-by-step execution plan

The final architect artifact for major work is an **execution plan** readable by average engineers and average-intelligence LLM agents. Requirements:

1. **Numbered steps** — each step is one clear action; no compound steps hiding multiple file edits.
2. ** Preconditions** — branch, issue link, env sync (`rtk bash scripts/sync-env.bash`), docs read list.
3. **File paths** — absolute or repo-root-relative paths for every edit target.
4. **Code shape hints** — registry call, class skeleton, or config key — not full implementations unless the step is trivial.
5. **Verification after every slice** — exact `rtk` + wrapper commands from `AGENTS.md`.
6. **Stop conditions** — when to pause for human review (public API change, schema migration, waiver).
7. **Handoff routes** — which task playbook continues after the plan (`code`, `code-review`, `doc-sync`, `manager`).

Store durable plans under a project-approved path:

- `docs/plans/<YYYY-MM-DD>-<topic>.md` for active multi-slice execution plans in repos that maintain plan artifacts.
- `docs/resources/architecture/<topic>.md` for architecture designs.
- `docs/goals/` updates for horizon changes.
- `docs/progress/YYYY-MM-DD/<topic>.md` for time-bound execution plans tied to a milestone.
- Linear issue description or a single rolling design comment when the plan is issue-owned.

Do not bury the only copy in chat history.

## Linear and GitHub alignment

When the design ties to tracked work:

1. Create or update a Linear issue with acceptance criteria copied from the plan summary.
2. Link related issues; avoid duplicating milestones already tracked.
3. For continuous design issues, edit **one rolling status comment** with plan version, open questions, and slice progress — do not spam routine updates.
4. If the plan gates a PR series, note suggested branch naming and review order in the issue.
5. Do not set issues to `Done` unless the user explicitly authorizes it.

## Quality bar before handoff

An architect deliverable is ready when:

- [ ] Current-state brief matches code and docs evidence cited.
- [ ] Design philosophy gate passed or waivers explicit.
- [ ] Agile architecture gate and smell/dependency review passed or waivers explicit.
- [ ] API standard table covers every new public symbol.
- [ ] Slices are small enough for one PR or one focused agent session each.
- [ ] Every slice has verification commands, not vague "run tests".
- [ ] Docs change list names canonical sources and stale pages to fix.
- [ ] Goals edits distinguish shipped vs planned behavior.
- [ ] Execution plan steps are executable without architectural guesswork.
- [ ] Non-goals and risks are stated.

## Report format

End architect runs with:

1. **Scope** — what was in/out of bounds.
2. **Evidence** — docs, commits, issues, connectors used.
3. **Artifacts produced** — paths or issue links.
4. **Recommended next step** — usually `code` slice 1, `doc-sync`, or human review.
5. **Open questions** — blockers only.

Also include an agile review summary: change pressure, smell/dependency findings, and feedback gates.

## Related surfaces

- Implementation: [../tasks/code.md](../tasks/code.md)
- Architecture design/review task: [../tasks/arch-design.md](../tasks/arch-design.md)
- Full-rule coding/refactor route: [developer.md](developer.md)
- Explanation for newcomers: [../tasks/code-explain.md](../tasks/code-explain.md)
- Docs sync after shipping: [../tasks/doc-sync.md](../tasks/doc-sync.md)
- Status orchestration: [../tasks/manager.md](../tasks/manager.md)
- Skill maintenance: [editor.md](editor.md)
