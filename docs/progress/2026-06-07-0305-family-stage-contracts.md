# 2026-06-07 03:05 CST - Family Stage Contracts

## Done

- Added explicit `stages` to the `paradev.build.families.v1` SDK and CLI payloads.
- Derived family stages from source-slot contracts and registered family methods, keeping the planner behavior unchanged.
- Covered simple, routed, collection-source, and collection-PDX family contracts in `Project.families(...)` tests.
- Documented the `stages` payload in the build-flow guide so SDK, GUI, MCP, and script clients do not infer compiler participation from Python methods.

## Verification

- Red first: `rtk uv run pytest tests/test_project.py -k families` failed because family payloads did not include `stages`.
- Focused green: `rtk uv run pytest tests/test_project.py -k families` passed 4 tests.
- Focused wrapper: `rtk bash scripts/test.bash tests/test_project.py -k families -q` passed 4 tests.
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py -q` passed 76 tests.
- Full suite: `rtk bash scripts/test.bash` passed 168 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/registry.py tests/test_project.py`
- CLI smoke: `rtk uv run paradev families demos/assets/projects/minimal --json`
- Whitespace: `rtk git diff --check -- src/paradev/build/registry.py tests/test_project.py docs/workflows/build-flow.md docs/progress/2026-06-07-0305-family-stage-contracts.md`

## Review

- Reviewed the intentional diff for `src/paradev/build/registry.py`, `tests/test_project.py`, and `docs/workflows/build-flow.md`; no blocking findings.

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- `stages` is a contract view, not a separate execution engine. It intentionally reports family-visible build participation and leaves project-level manifest/index stages out of the family rows.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue generic module compilation work by making family stage contracts useful in downstream SDK/CLI inspection and future extension-family authoring.
