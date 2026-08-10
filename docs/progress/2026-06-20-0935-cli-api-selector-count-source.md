# CLI API Selector Count Source

- Refreshed the focused CLI/REST/MCP selector regression suite after the API catalog `--reference-group` projection raised the CLI API table to 193 rows.
- Replaced duplicated `192` literals with checks against `get_cli_api_table()` so the REST `/cli-api` response and aggregate API catalog row count are verified against the SDK-owned table source.
- Kept the slice test-only because the generated references and runtime selector behavior already reflected the current API catalog contract.
