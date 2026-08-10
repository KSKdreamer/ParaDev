# 2026-06-07 03:21 CST - Project-Local Family Declarations

## Done

- Added first-pass `paradev.yaml` project-local family declarations for generic `simple_source` families.
- Let declared families extend the selected profile registry for `Project.families()`, `Project.build()`, and registry-backed discovery when callers do not pass an explicit registry.
- Added contextual manifest validation for unsupported declarative family kinds.
- Documented the declarative family shape in the build-flow guide with a `superevent` example.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_simple_family tests/test_project.py::test_project_manifest_rejects_unsupported_family_kind -q` failed because manifest-declared families were ignored and unsupported kinds were not validated.
- Focused green: `rtk bash scripts/test.bash tests/test_project_build.py::test_project_build_uses_manifest_declared_simple_family tests/test_project.py::test_project_manifest_rejects_unsupported_family_kind -q` passed 2 tests.
- Related suite: `rtk bash scripts/test.bash tests/test_project.py tests/test_project_build.py tests/test_build_records.py tests/test_build_manifest.py -q` passed 98 tests.
- Full suite: `rtk bash scripts/test.bash` passed 171 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/extensions.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_project.py tests/test_project_build.py`
- SDK smoke: `rtk uv run python - <<'PY' ...` loaded a temporary project with a manifest-declared `superevent` family and planned `events/superevents/FALL_OF_PARIS.txt`.
- Whitespace: `rtk git diff --check -- src/paradev/build/extensions.py src/paradev/build/__init__.py src/paradev/sdk/project.py tests/test_project.py tests/test_project_build.py docs/workflows/build-flow.md docs/progress/2026-06-07-0321-project-local-family-declarations.md`

## Review

- Reviewed the intentional diff for build extension helpers, SDK project registry wiring, tests, and build-flow docs; no blocking findings.

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- Declarative project-local families currently support `simple_source` only. Routed and collection declarations remain future registry-extension work.
- Explicit SDK `registry=` arguments remain authoritative and do not merge `paradev.yaml` family declarations.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Extend the project-local family path toward routed and collection families, or add a Python plugin loading contract once the narrow declarative path is stable.
