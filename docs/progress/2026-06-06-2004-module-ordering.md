# Module Ordering Progress

Date: 2026-06-06 20:04 CST

Linear: TAL-293

## Done

- Added deterministic module ordering from resolvable module `after` dependencies.
- Applied ordered modules before family artifact emission in `plan_build(...)`.
- Added blocking cycle diagnostics for module `after` dependency cycles.
- Documented the current ordering scope in the build-flow workflow.

## Verification

- `rtk uv run pytest tests/test_build_records.py tests/test_build_manifest.py -q`
- `rtk bash scripts/test.bash`
- `rtk bash scripts/flake.bash --ci`
- `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/records.py src/paradev/build/plan.py tests/test_build_records.py tests/test_build_manifest.py`

## Risks Or Blockers

- Live Linear sync is still pending because no Linear MCP tool or `linear` CLI is available in this session.
- Ordering currently resolves module-local aliases only; unresolved targets remain graph data rather than diagnostics.
- Existing local desktop and README edits remain outside this build graph slice.

## Next

- Add missing-target validation for `requires` and `after` edges using project-local symbols and later game reference indexes.
