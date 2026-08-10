# 2026-06-15 0603 CST - GUI API Reference

## Scope

- Added a generated `paradev.gui` facade API table for the installed `paradev-gui` launcher parser and entry point.
- Exposed explicit `paradev.gui.__all__` exports for the launcher helpers, schema constant, TypedDict rows, table helper, and Markdown renderer.
- Registered `gui-api` in the API catalog and CLI API table so SDK, CLI, desktop, and docs coverage audits can find the GUI launcher boundary.
- Regenerated the GUI, API catalog, and CLI generated reference docs.

## Boundaries

- Runtime GUI behavior is unchanged: the launcher still parses arguments, prints the placeholder endpoint message, and returns `0`.
- This slice avoids PIHC3 migration files, desktop frontend changes, and `node_modules/`.
- Verification is intentionally focused on the new GUI facade, generated catalog, CLI API table, and path-limited style checks.
