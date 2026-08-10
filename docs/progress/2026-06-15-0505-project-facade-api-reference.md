# Project Facade API Reference Progress

Date: 2026-06-15 05:05 CST

Linear: not updated

## Done

- Added a generated `paradev.project` facade API table for `Project`, `ProjectManifestError`, and project facade-reference helpers.
- Added CLI `project-facade-api` JSON/Markdown output and registered it in the aggregate API catalog and CLI command reference.
- Regenerated affected user-manual reference pages and linked the new page from the manual and architecture contracts.

## Verification

- Planned targeted checks: py_compile, focused architecture/CLI pytest, heaven-style scan, targeted flake, and `git diff --check`.

## Risks Or Blockers

- The worktree still has unrelated PIHC3, desktop, logo, skill, and `node_modules/` changes from other workers; this slice avoids staging them.

## Next

- Continue filling public facade/API-table gaps while preserving SDK-owned behavior and avoiding PIHC3 migration files.
