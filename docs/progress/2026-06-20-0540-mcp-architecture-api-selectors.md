# MCP Architecture API Selectors

- Added the read-only `architecture_api` MCP contract row for `get_architecture_api_selection(...)`.
- Added the matching `architecture_api` row to the architecture API table so SDK, CLI, REST, MCP, and docs describe the same selector path.
- Regenerated the architecture and MCP API references from their table helpers.
- Kept aggregate API catalog regeneration for a clean staged worktree because the local tree contains unrelated PIHC3/desktop changes that affect generated row counts.
- Verification stayed targeted to MCP/architecture selector tests and selected CLI/architecture contracts.
