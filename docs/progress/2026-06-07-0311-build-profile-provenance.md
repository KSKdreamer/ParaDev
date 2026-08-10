# 2026-06-07 03:11 CST - Build Profile Provenance

## Done

- Added optional build `profile` provenance to `BuildResult`.
- Threaded the resolved `Project.build(...)` profile into dry-run results, CLI build JSON, and emitted manifest payloads.
- Added `plan_build(..., profile=...)` support for SDK callers that build through a custom registry.
- Documented profile provenance in the build-flow guide.

## Verification

- Red first: `rtk bash scripts/test.bash tests/test_build_records.py::test_build_result_records_selected_profile_when_supplied tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project_build.py::test_project_build_returns_dry_run_result_without_writing_by_default tests/test_project_build.py::test_project_build_can_emit_manifest_files_when_requested tests/test_project.py::test_demo_project_build_cli_outputs_profile_artifacts -q` failed because `BuildResult.plan`, `plan_build`, build JSON, and manifest payloads did not expose `profile`.
- Focused green: `rtk bash scripts/test.bash tests/test_build_records.py::test_build_result_records_selected_profile_when_supplied tests/test_build_manifest.py::test_manifest_payloads_and_writes_include_source_map_and_summary tests/test_project_build.py::test_project_build_returns_dry_run_result_without_writing_by_default tests/test_project_build.py::test_project_build_can_emit_manifest_files_when_requested tests/test_project.py::test_demo_project_build_cli_outputs_profile_artifacts -q` passed 5 tests.
- Related suite: `rtk bash scripts/test.bash tests/test_build_records.py tests/test_build_manifest.py tests/test_project_build.py tests/test_project.py -q` passed 96 tests.
- Full suite: `rtk bash scripts/test.bash` passed 169 tests.
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven-style scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/records.py src/paradev/build/plan.py src/paradev/build/manifest.py src/paradev/sdk/project.py tests/test_build_records.py tests/test_build_manifest.py tests/test_project_build.py tests/test_project.py`
- CLI smoke: `rtk uv run paradev build demos/assets/projects/minimal --json`
- Whitespace: `rtk git diff --check -- src/paradev/build/records.py src/paradev/build/plan.py src/paradev/build/manifest.py src/paradev/sdk/project.py tests/test_build_records.py tests/test_build_manifest.py tests/test_project_build.py tests/test_project.py docs/workflows/build-flow.md docs/progress/2026-06-07-0311-build-profile-provenance.md`

## Review

- Reviewed the intentional diff for build records, planner, manifests, SDK project build, tests, and build-flow docs; no blocking findings.

## Linear

- `rtk command -v linear` exits with status 1.
- Tool discovery for Linear issue management exposed Codex automation and GitHub tools only; no Linear connector is available in this session.

## Risks

- This slice records the selected profile id; it does not snapshot the full registry contents. Family contracts remain available through `Project.families(...)`.
- Existing unrelated desktop, README, and script changes remain intentionally untouched.

## Next

- Continue toward project-local extension proof and profile/registry introspection that lets custom module compilers participate without core routing changes.
