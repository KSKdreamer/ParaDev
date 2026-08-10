# API Catalog Reference Group Selector

- Added `reference_group` to the shared API catalog selector so SDK, CLI, REST, and MCP callers can fetch one reader-oriented reference-group row without using raw table internals.
- Regenerated the affected API reference pages for API catalog, CLI, REST, MCP, and surfaces after the selector and return-type contract changed.
- Refreshed focused CLI API table assertions to the current selector-helper command model, including the new `paradev api-catalog --reference-group` projection.
- Verification target is the API catalog, REST, MCP, surfaces, and CLI API table slice rather than the full suite to avoid contending with concurrent PIHC3 migration work.
