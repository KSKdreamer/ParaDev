# 2026-06-15 10:59 Build graph index helper

## Scope

- Reused the shared typed index append helper in `src/paradev/build/graph.py` for the build graph `value -> row indexes` map.
- Kept the public `paradev.build.graph.v1` payload and build graph filters unchanged.
- Avoided dirty PIHC3 migration paths and desktop files owned by parallel workers.

## Verification

- `rtk uv run python - <<'PY' ...` compared build graph payloads against `HEAD` for default, module, edge-kind, family, and artifact filters.
- `rtk bash scripts/test.bash tests/test_project.py::test_project_build_graph_returns_source_artifact_and_dependency_edges_without_writing tests/test_project.py::test_project_cli_filters_build_graph_json -q`
- `rtk uv run python -m py_compile src/paradev/build/graph.py`
- `rtk uv run python .agents/skills/heaven-style/scripts/scan.py src/paradev/build/graph.py`
- `rtk bash scripts/flake.bash --ci --paths src/paradev/build/graph.py`
- `rtk git diff --check -- src/paradev/build/graph.py docs/progress/2026-06-15-1059-build-graph-index-helper.md`

## Notes

- Full-suite tests remain deferred to reduce CPU usage while other workers are active.
