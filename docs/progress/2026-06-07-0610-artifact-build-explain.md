# Artifact Build Explain Progress

Date: 2026-06-07 06:10 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Extended `paradev.build.explain.v1` so one payload can explain either a module or a planned artifact.
- Added artifact target support to `Project.build_explain(...)` and `paradev build-explain --artifact ... --target-root ... --json`.
- Added an artifact path filter to the shared build graph helper so artifact explanations reuse the same source-to-artifact graph model.
- Documented the artifact-first workflow for answering "what produced this artifact?"

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_returns_artifact_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_artifact_json -q` failed because `Project.build_explain(...)` did not accept `artifact_path` and the CLI did not expose `--artifact`.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_explain_returns_module_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_json tests/test_project.py::test_project_build_explain_returns_artifact_context_without_writing tests/test_project.py::test_project_cli_build_explain_outputs_artifact_json -q`
- CLI smoke: `rtk uv run paradev build-explain demos/assets/projects/minimal --artifact common/national_focus/GER_main.txt --target-root output --json`
- Related: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py tests/test_build_records.py tests/test_cli.py tests/test_architecture.py -q`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/explain.py src/paradev/build/graph.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`
- Diff hygiene: `rtk git diff --check`

## Review

- Artifact explanations are composed from source-map, diagnostics, and build graph payloads; there is still one traceability model.
- Artifact diagnostics are source-path scoped, so unrelated module diagnostics do not appear on every artifact from that module.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- Artifact explanations currently include emits edges only; incoming module/reference relationships remain available through module explanations and can be added to artifact payloads when a concrete UI/MCP question needs them.
- Linear status could not be updated from this environment.

## Next

- Add source-file-first explanation so users can ask what a specific authored file contributes to the build.
- Continue pushing generic compiler diagnostics toward source slots rather than raw path guessing.
