---
id: manager
task_kind: manager
status: active
enabled: true
order: 50
keywords: [project manager, status report, track tasks, triage linear, triage github, orchestrate agents, project status]
triggers: [manager, project status, what's ongoing, stale tasks, next steps, orchestrate, track Linear, track GitHub]
description: Use when tracking GitHub/Linear status, stale work, recent activity, next steps, or multi-agent coordination.
related_rules: [overview, review, docs, test]
---

# Manager Task

## Goal

Maintain an operational view of the GitHub repo and Linear workspace, then propose or coordinate the next useful work. Default project scope is HeavenBase unless the user names another repo, Linear project, team, label, milestone, or issue set.

## Sources

1. Read repo `AGENTS.md`, current branch, `git status`, recent commits, open PRs, CI/check status, issues, and project docs/status files.
2. Use GitHub tools or `gh` when available for PRs, branches, issues, checks, reviews, and recent activity.
3. Use Linear tools when available for issues, projects, cycles, labels, status, comments, stale work, blockers, and ownership.
4. If a connector/MCP auth fails repeatedly, use [../failures/auth-secrets.md](../failures/auth-secrets.md) and fall back to direct API paths when possible.
5. If Linear issue creation is blocked by project pressure, or a continuous issue has accumulated too many routine comments, use [../failures/linear-pressure.md](../failures/linear-pressure.md).
6. Never expose secrets, tokens, or private auth details in status reports.

## Status Analysis

Classify work into:

- Ongoing: active branches, in-progress Linear issues, open PRs, recent commits, active review threads, or running plans.
- Recent: tasks completed or materially changed in the selected lookback window.
- Stale: no recent activity, blocked status, failing checks, old review comments, unclear owner, missing acceptance criteria, or docs/test sync gaps.
- Risk: issues with ambiguous scope, hidden dependencies, stale docs, unverified fixes, auth/env blockers, or too-large PRs.
- Next steps: concrete actions with owner, target artifact, verification, and suggested task route.

## Orchestration Authority

- The manager may create or update Linear issues, comments, labels, links, and status when that follows from discovered facts.
- For continuous Linear issues, the manager should maintain one rolling status comment and edit it for routine progress, verification, and next steps. Do not pile up new comments unless the update is a distinct decision, blocker, handoff, or explicitly requested separate note.
- The manager may move Linear issues up to `In Review` when implementation evidence and review readiness are clear.
- The manager must not set Linear issues to `Done` unless the user explicitly instructs it or explicitly grants that authority for the current run.
- The manager may spawn or propose subagents when available. Use narrow prompts and clear task routes such as `code -> code-review -> doc-sync -> doc-trans -> code-explain`.
- The manager should monitor spawned work by collecting artifacts, verification output, review findings, docs updates, and Linear/GitHub status changes before reporting completion.

## Workflow

1. Resolve scope: project, repo, Linear team/project/cycle, GitHub branch/PR/issue set, and lookback window.
2. Gather current GitHub and Linear state. Prefer live connector data; use local git and docs as supporting evidence.
3. Cross-check code/docs/Linear claims for mismatch.
4. Identify ongoing, recent, stale, blocked, and risky items.
5. Propose next steps in priority order. Include which task playbook should execute each step.
6. Make authorized status/comment updates only when evidence is clear. State every update made.
7. If orchestrating agents, launch or propose the smallest useful chain, then monitor until each handoff has an artifact or explicit blocker.

## Report Format

Use concise sections:

- Scope and data sources.
- Ongoing work.
- Recent changes.
- Stale or blocked work.
- Risks and mismatches.
- Recommended next steps.
- Linear/GitHub updates made, including whether an existing rolling Linear comment was edited or a separate comment was intentionally added.
- Agent workflow started or proposed.
