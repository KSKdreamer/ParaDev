"""Build explanation payloads."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from .graph import build_graph
from .manifest import artifact_collection_ids, manifest_payloads
from .records import BuildResult, Collection, Module

EXPLAIN_SCHEMA = "paradev.build.explain.v1"


def build_explain(
    result: BuildResult,
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
    source_path: str | None = None,
    artifact_path: str | None = None,
    diagnostic_code: str | None = None,
    target_root: str | None = None,
) -> dict[str, object]:
    """Explain one module, collection, source file, artifact, or diagnostic's dry-build context.

    Args:
        result: Dry or emitted build result.
        module_id: Module id, with or without the `module:` prefix. Mutually
            exclusive with other targets.
        collection_id: Collection id, with or without the `collection:` prefix.
            Mutually exclusive with other targets.
        source_path: Source file path as represented in the source-map manifest.
            Mutually exclusive with other targets.
        artifact_path: Artifact path under its target root. Mutually exclusive with other targets.
        diagnostic_code: Diagnostic code to explain. Mutually exclusive with other targets.
        target_root: Optional artifact target root filter, such as `output`.

    Returns:
        JSON-safe explanation payload with related sources, artifacts,
        dependencies, diagnostics, and graph subset.

    Raises:
        ValueError: If the requested target is invalid or not part of the build
            result.
    """

    module_id = _target_text("--module", module_id)
    collection_id = _target_text("--collection", collection_id)
    source_path = _target_text("--source", source_path)
    artifact_path = _target_text("--artifact", artifact_path)
    diagnostic_code = _target_text("--diagnostic-code", diagnostic_code)
    _validate_target(
        module_id=module_id,
        collection_id=collection_id,
        source_path=source_path,
        artifact_path=artifact_path,
        diagnostic_code=diagnostic_code,
        target_root=target_root,
    )
    if diagnostic_code:
        return _build_diagnostic_explain(result, diagnostic_code=diagnostic_code)
    if source_path:
        return _build_source_explain(result, source_path=source_path)
    if artifact_path:
        return _build_artifact_explain(result, artifact_path=artifact_path, target_root=target_root)
    if collection_id:
        return _build_collection_explain(result, collection_id=collection_id)
    return _build_module_explain(result, module_id=str(module_id))


def _build_module_explain(result: BuildResult, *, module_id: str) -> dict[str, object]:
    module = _module(result, module_id)
    target = _target(module)
    manifests = manifest_payloads(result)
    source_map = _source_map_rows(manifests["source-map.json"].get("source_map"), module.module_id)
    dependencies = _dependency_rows(manifests["dependencies.json"].get("dependencies"), target["id"])
    diagnostics = _diagnostic_rows(manifests["diagnostics.json"].get("diagnostics"), module.module_id)
    sources = _sources(source_map, module.module_id)
    graph = build_graph(result, module_id=module.module_id)
    return _payload(
        result,
        target=target,
        sources=sources,
        artifacts=source_map,
        dependencies=dependencies,
        diagnostics=diagnostics,
        graph=graph,
    )


def _build_collection_explain(result: BuildResult, *, collection_id: str) -> dict[str, object]:
    collection = _collection(result, collection_id)
    target = _collection_target(collection)
    manifests = manifest_payloads(result)
    source_map = _collection_source_map_rows(manifests["source-map.json"].get("source_map"), collection.collection_id)
    sources = _artifact_source_rows(source_map)
    dependencies = _collection_dependency_rows(manifests["dependencies.json"].get("dependencies"), collection.module_ids)
    diagnostics = _collection_diagnostic_rows(manifests["diagnostics.json"].get("diagnostics"), collection)
    graph = build_graph(result, collection_id=collection.collection_id)
    return _payload(
        result,
        target=target,
        sources=sources,
        artifacts=source_map,
        dependencies=dependencies,
        diagnostics=diagnostics,
        graph=graph,
    )


def _build_artifact_explain(result: BuildResult, *, artifact_path: str, target_root: str | None) -> dict[str, object]:
    manifests = manifest_payloads(result)
    source_map = _artifact_source_map_rows(manifests["source-map.json"].get("source_map"), artifact_path=artifact_path, target_root=target_root)
    if not source_map:
        raise ValueError(f"Unknown build artifact: {artifact_path}")
    if len(source_map) > 1:
        raise ValueError(f"Ambiguous build artifact: {artifact_path}; pass --target-root.")
    artifact = source_map[0]
    target = _artifact_target(artifact)
    sources = _artifact_sources(artifact)
    dependencies: list[dict[str, object]] = []
    diagnostics = _artifact_diagnostic_rows(manifests["diagnostics.json"].get("diagnostics"), artifact=artifact, sources=sources)
    graph = build_graph(result, artifact_path=str(artifact["artifact_path"]), target_root=str(artifact["target_root"]))
    return _payload(
        result,
        target=target,
        sources=sources,
        artifacts=source_map,
        dependencies=dependencies,
        diagnostics=diagnostics,
        graph=graph,
    )


def _build_source_explain(result: BuildResult, *, source_path: str) -> dict[str, object]:
    manifests = manifest_payloads(result)
    source_map = _source_source_map_rows(manifests["source-map.json"].get("source_map"), source_path=source_path)
    if not source_map:
        raise ValueError(f"Unknown build source: {source_path}")
    sources = _source_sources(source_map, source_path)
    target = _source_target(sources[0])
    dependencies: list[dict[str, object]] = []
    diagnostics = _source_diagnostic_rows(manifests["diagnostics.json"].get("diagnostics"), source_path=source_path)
    graph = build_graph(result, source_path=source_path)
    return _payload(
        result,
        target=target,
        sources=sources,
        artifacts=source_map,
        dependencies=dependencies,
        diagnostics=diagnostics,
        graph=graph,
    )


def _build_diagnostic_explain(result: BuildResult, *, diagnostic_code: str) -> dict[str, object]:
    manifests = manifest_payloads(result)
    diagnostics = _diagnostic_code_rows(manifests["diagnostics.json"].get("diagnostics"), diagnostic_code)
    if not diagnostics:
        raise ValueError(f"Unknown build diagnostic code: {diagnostic_code}")
    sources = _diagnostic_sources(diagnostics)
    artifacts = _diagnostic_artifacts(manifests["source-map.json"].get("source_map"), diagnostics)
    dependencies: list[dict[str, object]] = []
    graph = _diagnostic_graph(result, sources=sources, artifacts=artifacts)
    return _payload(
        result,
        target=_diagnostic_target(diagnostic_code),
        sources=sources,
        artifacts=artifacts,
        dependencies=dependencies,
        diagnostics=diagnostics,
        graph=graph,
    )


def _payload(
    result: BuildResult,
    *,
    target: dict[str, object],
    sources: list[dict[str, object]],
    artifacts: list[dict[str, object]],
    dependencies: list[dict[str, object]],
    diagnostics: list[dict[str, object]],
    graph: Mapping[str, object],
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": EXPLAIN_SCHEMA,
        "project_id": result.project_id,
        "target": target,
        "summary": _summary(sources=sources, source_map=artifacts, dependencies=dependencies, diagnostics=diagnostics, graph=graph),
        "sources": sources,
        "artifacts": artifacts,
        "dependencies": dependencies,
        "diagnostics": diagnostics,
        "graph": graph,
    }
    if result.profile:
        payload["profile"] = result.profile
    return payload


def _target_text(flag: str, value: str | None) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        raise ValueError(f"{flag} must be non-empty.")
    return text


def _validate_target(
    *,
    module_id: str | None,
    collection_id: str | None,
    source_path: str | None,
    artifact_path: str | None,
    diagnostic_code: str | None,
    target_root: str | None,
) -> None:
    targets = [value for value in (module_id, collection_id, source_path, artifact_path, diagnostic_code) if value]
    if len(targets) > 1:
        raise ValueError("Pass only one build explanation target: --module, --collection, --source, --artifact, or --diagnostic-code.")
    if not targets:
        raise ValueError("Pass a build explanation target with --module, --collection, --source, --artifact, or --diagnostic-code.")
    if (module_id or collection_id or source_path or diagnostic_code) and target_root:
        raise ValueError("--target-root is only valid with --artifact.")


def _module(result: BuildResult, value: str) -> Module:
    module_id = value.removeprefix("module:")
    for module in result.modules:
        if module.module_id == module_id:
            return module
    raise ValueError(f"Unknown build module: {module_id}")


def _collection(result: BuildResult, value: str) -> Collection:
    collection_id = value.removeprefix("collection:")
    for collection in result.collections:
        if collection.collection_id == collection_id:
            return collection
    raise ValueError(f"Unknown build collection: {collection_id}")


def _target(module: Module) -> dict[str, object]:
    return {"id": f"module:{module.module_id}", "type": "module", "module_id": module.module_id, "family": module.family}


def _collection_target(collection: Collection) -> dict[str, object]:
    target: dict[str, object] = {
        "id": f"collection:{collection.collection_id}",
        "type": "collection",
        "collection_id": collection.collection_id,
        "family": collection.family,
        "module_ids": list(collection.module_ids),
    }
    if collection.source_slots:
        target["source_slots"] = {key: [str(path).replace("\\", "/") for path in collection.source_slots[key]] for key in sorted(collection.source_slots)}
    return target


def _artifact_target(row: Mapping[object, object]) -> dict[str, object]:
    artifact_path = str(row["artifact_path"])
    target_root = str(row["target_root"])
    return {
        "id": f"artifact:{target_root}:{artifact_path}",
        "type": "artifact",
        "artifact_path": artifact_path,
        "artifact_type": str(row["type"]),
        "target_root": target_root,
        "owner": str(row["owner"]),
    }


def _source_target(source: Mapping[object, object]) -> dict[str, object]:
    path = str(source["path"])
    target: dict[str, object] = {
        "id": f"source:{path}",
        "type": "source",
        "label": Path(path).name,
        "path": path,
    }
    for key in ("module_id", "collection_id", "family", "slot"):
        value = source.get(key)
        if isinstance(value, str):
            target[key] = value
    return target


def _diagnostic_target(code: str) -> dict[str, object]:
    return {"id": f"diagnostic:{code}", "type": "diagnostic", "code": code}


def _source_map_rows(rows: object, module_id: str) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, Mapping):
            continue
        if _row_has_module_source(row, module_id):
            filtered.append(dict(row))
    return filtered


def _source_source_map_rows(rows: object, *, source_path: str) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, Mapping):
            continue
        if _row_has_source_path(row, source_path):
            filtered.append(dict(row))
    return filtered


def _artifact_source_map_rows(rows: object, *, artifact_path: str, target_root: str | None) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, Mapping):
            continue
        if row.get("artifact_path") != artifact_path:
            continue
        if target_root and row.get("target_root") != target_root:
            continue
        filtered.append(dict(row))
    return filtered


def _collection_source_map_rows(rows: object, collection_id: str) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if isinstance(row, Mapping) and collection_id in artifact_collection_ids(row):
            filtered.append(dict(row))
    return filtered


def _dependency_rows(rows: object, source_id: object) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if isinstance(row, Mapping) and row.get("source") == source_id:
            filtered.append(dict(row))
    return filtered


def _collection_dependency_rows(rows: object, module_ids: tuple[str, ...]) -> list[dict[str, object]]:
    wanted_sources = {f"module:{module_id}" for module_id in module_ids}
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if isinstance(row, Mapping) and row.get("source") in wanted_sources:
            filtered.append(dict(row))
    return filtered


def _diagnostic_rows(rows: object, module_id: str) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, Mapping):
            continue
        if row.get("module_id") == module_id or _source_value(row, "module_id") == module_id:
            filtered.append(dict(row))
    return filtered


def _collection_diagnostic_rows(rows: object, collection: Collection) -> list[dict[str, object]]:
    module_ids = set(collection.module_ids)
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, Mapping):
            continue
        if (
            row.get("collection_id") == collection.collection_id
            or _source_value(row, "collection_id") == collection.collection_id
            or row.get("module_id") in module_ids
            or _source_value(row, "module_id") in module_ids
        ):
            filtered.append(dict(row))
    return filtered


def _source_diagnostic_rows(rows: object, *, source_path: str) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, Mapping):
            continue
        if row.get("source_path") == source_path or _source_value(row, "path") == source_path:
            filtered.append(dict(row))
    return filtered


def _artifact_diagnostic_rows(
    rows: object,
    *,
    artifact: Mapping[object, object],
    sources: list[dict[str, object]],
) -> list[dict[str, object]]:
    source_paths = {str(source["path"]) for source in sources if isinstance(source.get("path"), str)}
    artifact_path = str(artifact["artifact_path"])
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, Mapping):
            continue
        if row.get("artifact_path") == artifact_path or _source_value(row, "path") in source_paths:
            filtered.append(dict(row))
    return filtered


def _diagnostic_code_rows(rows: object, code: str) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if isinstance(row, Mapping) and row.get("code") == code:
            filtered.append(dict(row))
    return filtered


def _diagnostic_sources(diagnostics: list[dict[str, object]]) -> list[dict[str, object]]:
    sources: dict[tuple[str, str, str, str, str], dict[str, object]] = {}
    for diagnostic in diagnostics:
        source = diagnostic.get("source")
        if isinstance(source, Mapping):
            source_row = dict(source)
            sources[_source_key(source_row)] = source_row
    return [sources[key] for key in sorted(sources)]


def _diagnostic_artifacts(rows: object, diagnostics: list[dict[str, object]]) -> list[dict[str, object]]:
    artifact_targets = tuple(
        (str(row["artifact_path"]), str(row["target_root"]) if isinstance(row.get("target_root"), str) else None)
        for row in diagnostics
        if isinstance(row.get("artifact_path"), str)
    )
    if not artifact_targets:
        return []
    artifacts: list[dict[str, object]] = []
    for row in rows if isinstance(rows, list) else ():
        if isinstance(row, Mapping) and any(
            row.get("artifact_path") == artifact_path and (target_root is None or row.get("target_root") == target_root)
            for artifact_path, target_root in artifact_targets
        ):
            artifacts.append(dict(row))
    return artifacts


def _diagnostic_graph(
    result: BuildResult,
    *,
    sources: list[dict[str, object]],
    artifacts: list[dict[str, object]],
) -> dict[str, object]:
    artifact_targets = _artifact_targets(artifacts)
    if artifact_targets:
        return build_graph(result, artifact_targets=artifact_targets)
    if len(sources) == 1:
        return build_graph(result, source_path=str(sources[0]["path"]))
    return build_graph(result, source_path="diagnostic:<unanchored>")


def _artifact_targets(artifacts: list[dict[str, object]]) -> tuple[tuple[str, str], ...]:
    targets = {
        (str(artifact["artifact_path"]), str(artifact["target_root"]))
        for artifact in artifacts
        if isinstance(artifact.get("artifact_path"), str) and isinstance(artifact.get("target_root"), str)
    }
    return tuple(sorted(targets))


def _sources(source_map: list[dict[str, object]], module_id: str) -> list[dict[str, object]]:
    sources: dict[str, dict[str, object]] = {}
    for row in source_map:
        row_sources = row.get("sources")
        for source in row_sources if isinstance(row_sources, list) else ():
            if isinstance(source, Mapping) and source.get("module_id") == module_id:
                sources[str(source["path"])] = dict(source)
    return [sources[path] for path in sorted(sources)]


def _source_sources(source_map: list[dict[str, object]], source_path: str) -> list[dict[str, object]]:
    sources: dict[tuple[str, str, str, str, str], dict[str, object]] = {}
    for row in source_map:
        row_sources = row.get("sources")
        for source in row_sources if isinstance(row_sources, list) else ():
            if isinstance(source, Mapping) and source.get("path") == source_path:
                source_row = dict(source)
                sources[_source_key(source_row)] = source_row
    return [sources[key] for key in sorted(sources)]


def _artifact_sources(artifact: Mapping[object, object]) -> list[dict[str, object]]:
    sources: dict[str, dict[str, object]] = {}
    row_sources = artifact.get("sources")
    for source in row_sources if isinstance(row_sources, list) else ():
        if isinstance(source, Mapping) and isinstance(source.get("path"), str):
            sources[str(source["path"])] = dict(source)
    return [sources[path] for path in sorted(sources)]


def _artifact_source_rows(source_map: list[dict[str, object]]) -> list[dict[str, object]]:
    sources: dict[tuple[str, str, str, str, str], dict[str, object]] = {}
    for row in source_map:
        row_sources = row.get("sources")
        for source in row_sources if isinstance(row_sources, list) else ():
            if isinstance(source, Mapping):
                source_row = dict(source)
                sources[_source_key(source_row)] = source_row
    return [sources[key] for key in sorted(sources)]


def _source_key(source: Mapping[object, object]) -> tuple[str, str, str, str, str]:
    return (
        str(source.get("path") or ""),
        str(source.get("module_id") or ""),
        str(source.get("collection_id") or ""),
        str(source.get("family") or ""),
        str(source.get("slot") or ""),
    )


def _row_has_module_source(row: Mapping[object, object], module_id: str) -> bool:
    sources = row.get("sources")
    for source in sources if isinstance(sources, list) else ():
        if isinstance(source, Mapping) and source.get("module_id") == module_id:
            return True
    return False


def _row_has_source_path(row: Mapping[object, object], source_path: str) -> bool:
    sources = row.get("sources")
    for source in sources if isinstance(sources, list) else ():
        if isinstance(source, Mapping) and source.get("path") == source_path:
            return True
    return False


def _source_value(row: Mapping[object, object], key: str) -> object:
    source = row.get("source")
    return source.get(key) if isinstance(source, Mapping) else None


def _summary(
    *,
    sources: list[dict[str, object]],
    source_map: list[dict[str, object]],
    dependencies: list[dict[str, object]],
    diagnostics: list[dict[str, object]],
    graph: Mapping[str, object],
) -> dict[str, object]:
    graph_summary = graph.get("summary") if isinstance(graph.get("summary"), Mapping) else {}
    return {
        "source_count": len(sources),
        "artifact_count": len(source_map),
        "dependency_count": len(dependencies),
        "diagnostic_count": len(diagnostics),
        "graph_node_count": int(graph_summary.get("node_count") or 0),
        "graph_edge_count": int(graph_summary.get("edge_count") or 0),
        "blocked": any(row.get("severity") == "error" for row in diagnostics),
    }


__all__ = ["EXPLAIN_SCHEMA", "build_explain"]
