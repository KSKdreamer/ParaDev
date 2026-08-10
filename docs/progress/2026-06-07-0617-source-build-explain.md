# Source Build Explain Progress

Date: 2026-06-07 06:17 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Extended `paradev.build.explain.v1` with source-file targets alongside module and artifact targets.
- Added `Project.build_explain(source_path=...)`, resolving relative source paths from the project root.
- Added `paradev build-explain --source ... --json` for the source-first user workflow.
- Added source path filtering to the shared build graph helper so source explanations reuse the same emits graph model.
- Documented the source-first workflow for answering "what did this source file produce?"

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_returns_source_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_source_json -q` failed because `Project.build_explain(...)` did not accept `source_path` and the CLI did not expose `--source`.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_returns_module_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_json tests/test_project.py::test_project_build_explain_returns_artifact_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_artifact_json tests/test_project.py::test_project_build_explain_returns_source_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_source_json -q`
- CLI smoke: `rtk uv run paradev build-explain demos/assets/projects/minimal --source src/modules/focus/GER_sample/def.pdx --json`
- Related: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py tests/test_build_records.py tests/test_cli.py tests/test_architecture.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/explain.py src/paradev/build/graph.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- Source explanations remain manifest-backed: they compose source-map, diagnostics, and graph payloads instead of path-guessing artifacts.
- The CLI still has one explain command with one selected target: module, source, or artifact.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Source explanations currently focus on emitted artifacts and source-linked diagnostics; module-level dependency context remains in module explanations.
- Linear status could not be updated from this environment.

## Next

- Add validation tests for invalid or ambiguous explain targets so CLI/MCP clients receive predictable errors.
- Continue pushing generic compiler diagnostics toward source slots rather than raw path guessing.
