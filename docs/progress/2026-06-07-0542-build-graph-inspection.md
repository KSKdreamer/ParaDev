# Build Graph Inspection Progress

Date: 2026-06-07 05:42 CST

Linear: unavailable; no Linear connector was exposed by tool discovery and `linear` is not on PATH.

## Done

- Added a build-layer `build_graph(...)` helper that composes source-map rows and dependency rows into deterministic graph nodes and edges.
- Added `Project.build_graph(...)` for SDK callers.
- Added `paradev build-graph <path> --json` with source, artifact, and edge-kind filters.
- Documented the graph inspection workflow as the bridge from persisted PDX/build catalog work into generic compilation graph work.

## Verification

- Red check: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_graph_returns_source_artifact_and_dependency_edges_without_writing tests/test_project.py::test_project_cli_filters_build_graph_json -q` failed because `Project.build_graph` and `build-graph` were missing.
- Focused green: `rtk bash scripts/test.bash tests/test_project.py::test_project_build_graph_returns_source_artifact_and_dependency_edges_without_writing tests/test_project.py::test_project_cli_filters_build_graph_json -q`
- Related: `rtk bash scripts/test.bash tests/test_project.py tests/test_build_manifest.py tests/test_build_records.py tests/test_cli.py tests/test_architecture.py -q`
- CLI smoke: `rtk uv run paradev build-graph demos/assets/projects/minimal --module focus/GER_sample --kind requires --json`
- Full suite: `rtk bash scripts/test.bash`
- Lint: `rtk bash scripts/flake.bash --ci`
- Heaven scan: `rtk uv run python .claude/skills/heaven-style/scripts/scan.py src/paradev/build/graph.py src/paradev/build/__init__.py src/paradev/sdk/project.py src/paradev/cli.py tests/test_project.py`

## Review

- The graph view reuses the existing dry-build source-map and dependency manifests instead of introducing a second planner.
- `build-graph --kind requires` shows dependency edges without unrelated source/artifact nodes, keeping filtered output small for users.
- The SDK/CLI surfaces do not write `.paradev/build` files.
- Unrelated desktop and README work remains outside this slice and should stay unstaged.

## Risks Or Blockers

- The graph currently exposes source-to-artifact and dependency edges. Collection ownership and richer typed catalog-table views can follow after the generic compilation graph is more stable.
- Linear status could not be updated from this environment.

## Next

- Feed the build graph into the HeavenBase catalog layer so persisted catalog inspection can show graph nodes and edges.
- Use the graph payload to drive the next generic module compilation diagnostics and explainability slice.
