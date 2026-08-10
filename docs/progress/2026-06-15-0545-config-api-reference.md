# 2026-06-15 05:45 CST - Config API reference

## Scope

- Added a generated `paradev.config` API table for `DEFAULT_CONFIG`, `BOOTSTRAP_CONFIG`, `CM_PARADEV`, and config-reference helpers.
- Added the `config-api` CLI/catalog reference surface and regenerated config, API catalog, and CLI API Markdown references.
- Updated architecture, SDK manual, developer manual, and CLI tests so the config facade is tracked as a stable public SDK boundary.

## Review Notes

- `paradev.config.__all__` is now explicit, so wildcard imports expose only the intended config facade instead of implementation imports such as `os` or `ConfigManager`.
- This slice stays outside PIHC3 migration files and does not touch `node_modules`.

## Verification

- Planned targeted checks: Python compile, config/catalog/CLI API tests, heaven-style scan on touched Python files, path-limited flake, and staged diff checks.
