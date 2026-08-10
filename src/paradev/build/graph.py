"""Build graph inspection payloads."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from paradev._api_table import append_index_entry

from .manifest import artifact_collection_ids, artifact_module_ids, manifest_rows
from .records import BuildResult

GRAPH_SCHEMA = "paradev.build.graph.v1"


def build_graph(
    result: BuildResult,
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
    family: str | None = None,
    slot: str | None = None,
    source_path: str | None = None,
    artifact_path: str | None = None,
    artifact_targets: Sequence[tuple[str, str]] = (),
    artifact_type: str | None = None,
    target_root: str | None = None,
    edge_kind: str | None = None,
) -> dict[str, object]:
    """Return a source, artifact, and dependency graph for one build result.

    Args:
        result: Dry or emitted build result.
        module_id: Optional module source filter.
        collection_id: Optional collection source filter.
        family: Optional module or collection family filter.
        slot: Optional source slot filter.
        source_path: Optional source file path filter.
        artifact_path: Optional artifact path filter.
        artifact_targets: Optional exact `(artifact_path, target_root)` filters.
        artifact_type: Optional artifact type filter, such as `pdx`.
        target_root: Optional artifact target root filter, such as `output`.
        edge_kind: Optional edge kind filter, such as `emits` or `requires`.

    Returns:
        JSON-safe graph payload with deterministic node and edge ordering.
    """

    source_map = manifest_rows(result, "source-map.json")
    dependencies = manifest_rows(result, "dependencies.json")
    module_families = {f"module:{module.module_id}": module.family for module in result.modules}
    nodes: dict[str, dict[str, object]] = {}
    edges: list[dict[str, object]] = []

    if edge_kind in (None, "emits"):
        _add_emit_edges(
            nodes,
            edges,
            source_map,
            module_id=module_id,
            collection_id=collection_id,
            family=family,
            slot=slot,
            source_path=source_path,
            artifact_path=artifact_path,
            artifact_targets=artifact_targets,
            artifact_type=artifact_type,
            target_root=target_root,
        )
    if not any((collection_id, slot, source_path, artifact_path, artifact_targets, artifact_type, target_root)):
        _add_dependency_edges(nodes, edges, dependencies, module_families=module_families, module_id=module_id, family=family, edge_kind=edge_kind)

    node_rows = sorted(nodes.values(), key=lambda row: (str(row["type"]), str(row["id"])))
    edge_rows = sorted(edges, key=_edge_sort_key)
    payload: dict[str, object] = {
        "schema": GRAPH_SCHEMA,
        "project_id": result.project_id,
        "nodes": node_rows,
        "edges": edge_rows,
        "summary": _graph_summary(node_rows, edge_rows),
        "index": _graph_index(node_rows, edge_rows),
    }
    if result.profile:
        payload["profile"] = result.profile
    return payload


def _add_emit_edges(
    nodes: dict[str, dict[str, object]],
    edges: list[dict[str, object]],
    rows: object,
    *,
    module_id: str | None,
    collection_id: str | None,
    family: str | None,
    slot: str | None,
    source_path: str | None,
    artifact_path: str | None,
    artifact_targets: Sequence[tuple[str, str]],
    artifact_type: str | None,
    target_root: str | None,
) -> None:
    artifact_target_set = set(artifact_targets)
    include_artifact_only = bool(artifact_target_set or artifact_path or artifact_type or target_root) and not any(
        (module_id, collection_id, family, slot, source_path)
    )
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, Mapping):
            continue
        row_artifact_path = row.get("artifact_path")
        row_target_root = row.get("target_root")
        if artifact_target_set and (row_artifact_path, row_target_root) not in artifact_target_set:
            continue
        if artifact_path and row.get("artifact_path") != artifact_path:
            continue
        if artifact_type and row.get("type") != artifact_type:
            continue
        if target_root and row.get("target_root") != target_root:
            continue
        artifact_id = _artifact_id(row)
        sources = _matched_sources(
            row,
            module_id=module_id,
            collection_id=collection_id,
            family=family,
            slot=slot,
            source_path=source_path,
        )
        if not sources:
            if include_artifact_only:
                _add_node(nodes, _artifact_node(row, artifact_id))
            continue
        _add_node(nodes, _artifact_node(row, artifact_id))
        for source in sources:
            source_id = _source_id(source)
            _add_node(nodes, _source_node(source, source_id))
            edges.append(
                {
                    "source": source_id,
                    "target": artifact_id,
                    "kind": "emits",
                    "artifact_type": str(row["type"]),
                    "target_root": str(row["target_root"]),
                }
            )


def _add_dependency_edges(
    nodes: dict[str, dict[str, object]],
    edges: list[dict[str, object]],
    rows: object,
    *,
    module_families: Mapping[str, str],
    module_id: str | None,
    family: str | None,
    edge_kind: str | None,
) -> None:
    wanted_source = _module_node_id(module_id) if module_id else None
    for row in rows if isinstance(rows, list) else ():
        if not isinstance(row, Mapping):
            continue
        source_id = row.get("source")
        target = row.get("target")
        kind = row.get("kind")
        if not isinstance(source_id, str) or not isinstance(target, str) or not isinstance(kind, str):
            continue
        if edge_kind and kind != edge_kind:
            continue
        if wanted_source and source_id != wanted_source:
            continue
        if family and module_families.get(source_id) != family:
            continue
        nodes[source_id] = _module_node(source_id, module_families.get(source_id))
        target_id = _dependency_target_id(target)
        if target_id.startswith("module:"):
            nodes[target_id] = _module_node(target_id, module_families.get(target_id))
        else:
            nodes[target_id] = _reference_node(target, target_id)
        edges.append({"source": source_id, "target": target_id, "kind": kind})


def _source_map_sources(row: Mapping[object, object]) -> list[dict[str, object]]:
    sources = row.get("sources")
    if not isinstance(sources, list):
        return []
    return [dict(source) for source in sources if isinstance(source, Mapping)]


def _matched_sources(
    row: Mapping[object, object],
    *,
    module_id: str | None,
    collection_id: str | None,
    family: str | None,
    slot: str | None,
    source_path: str | None,
) -> list[dict[str, object]]:
    sources = _source_map_sources(row)
    if collection_id and not any((module_id, family, slot, source_path)) and collection_id in artifact_collection_ids(row):
        return sources
    return [
        source
        for source in sources
        if _source_matches(source, module_id=module_id, collection_id=collection_id, family=family, slot=slot, source_path=source_path)
    ]


def _source_matches(
    source: Mapping[str, object],
    *,
    module_id: str | None,
    collection_id: str | None,
    family: str | None,
    slot: str | None,
    source_path: str | None,
) -> bool:
    if source_path and source.get("path") != source_path:
        return False
    if module_id and source.get("module_id") != module_id:
        return False
    if collection_id and source.get("collection_id") != collection_id:
        return False
    if family and source.get("family") != family:
        return False
    if slot and source.get("slot") != slot:
        return False
    return True


def _artifact_id(row: Mapping[object, object]) -> str:
    return f"artifact:{row['target_root']}:{row['artifact_path']}"


def _artifact_node(row: Mapping[object, object], node_id: str) -> dict[str, object]:
    path = str(row["artifact_path"])
    target_root = str(row["target_root"])
    node: dict[str, object] = {
        "id": node_id,
        "type": "artifact",
        "group": f"artifact:{target_root}",
        "label": path,
        "display_label": _path_name(path),
        "display_detail": _display_detail(target_root, _parent_path(path)),
        "display_path": path,
        "path": path,
        "artifact_type": str(row["type"]),
        "target_root": target_root,
        "owner": str(row["owner"]),
    }
    module_ids = artifact_module_ids(row)
    collection_ids = artifact_collection_ids(row)
    if module_ids:
        node["module_ids"] = list(module_ids)
    if collection_ids:
        node["collection_ids"] = list(collection_ids)
    return node


def _add_node(nodes: dict[str, dict[str, object]], node: dict[str, object]) -> None:
    node_id = str(node["id"])
    existing = nodes.get(node_id)
    if existing is None:
        nodes[node_id] = node
        return
    if existing.get("type") == "artifact" and node.get("type") == "artifact":
        nodes[node_id] = _merge_artifact_nodes(existing, node)


def _merge_artifact_nodes(existing: dict[str, object], node: dict[str, object]) -> dict[str, object]:
    merged = dict(existing)
    for key in ("module_ids", "collection_ids"):
        values = _node_values(existing, key) | _node_values(node, key)
        if values:
            merged[key] = sorted(values)
    owners = _node_values(existing, "owners") | _node_values(node, "owners")
    for row in (existing, node):
        owner = row.get("owner")
        if isinstance(owner, str) and owner:
            owners.add(owner)
    if len(owners) > 1:
        merged["owners"] = sorted(owners)
    return merged


def _node_values(node: Mapping[str, object], key: str) -> set[str]:
    values = node.get(key)
    if not isinstance(values, list):
        return set()
    return {value for value in values if isinstance(value, str) and value}


def _source_id(source: Mapping[str, object]) -> str:
    return f"source:{source['path']}"


def _source_node(source: Mapping[str, object], node_id: str) -> dict[str, object]:
    path = str(source["path"])
    family = _node_text(source.get("family"))
    display_detail = _source_display_detail(source)
    node: dict[str, object] = {
        "id": node_id,
        "type": "source",
        "group": _node_group("source", family),
        "label": Path(path).name,
        "display_label": Path(path).name,
        "display_detail": display_detail,
        "display_path": _source_display_path(source, path),
        "path": path,
    }
    for key in ("module_id", "collection_id", "family", "slot"):
        value = source.get(key)
        if isinstance(value, str):
            node[key] = value
    return node


def _module_node_id(module_id: str) -> str:
    return module_id if module_id.startswith("module:") else f"module:{module_id}"


def _module_node(node_id: str, family: str | None = None) -> dict[str, object]:
    module_id = node_id.removeprefix("module:")
    node: dict[str, object] = {
        "id": node_id,
        "type": "module",
        "group": _node_group("module", family),
        "label": module_id,
        "display_label": _path_name(module_id),
        "display_detail": family or "module",
        "display_path": module_id,
        "module_id": module_id,
    }
    if family:
        node["family"] = family
    return node


def _dependency_target_id(target: str) -> str:
    return target if target.startswith("module:") else f"reference:{target}"


def _reference_node(target: str, node_id: str) -> dict[str, object]:
    target_kind, display_label = _reference_display(target)
    node: dict[str, object] = {
        "id": node_id,
        "type": "reference",
        "group": _node_group("reference", target_kind),
        "label": target,
        "display_label": display_label,
        "display_detail": target_kind or "reference",
        "display_path": target,
        "target": target,
    }
    if target_kind:
        node["target_kind"] = target_kind
    return node


def _edge_sort_key(edge: Mapping[str, object]) -> tuple[str, str, str, str, str]:
    return (
        str(edge.get("kind") or ""),
        str(edge.get("source") or ""),
        str(edge.get("target") or ""),
        str(edge.get("artifact_type") or ""),
        str(edge.get("target_root") or ""),
    )


def _graph_summary(nodes: list[dict[str, object]], edges: list[dict[str, object]]) -> dict[str, object]:
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes_by_type": _count_by(nodes, "type"),
        "nodes_by_group": _count_by(nodes, "group"),
        "edges_by_kind": _count_by(edges, "kind"),
    }


def _graph_index(nodes: list[dict[str, object]], edges: list[dict[str, object]]) -> dict[str, object]:
    return {"nodes_by_type": _index_by(nodes, "type"), "nodes_by_group": _index_by(nodes, "group"), "edges_by_kind": _index_by(edges, "kind")}


def _node_group(kind: str, qualifier: str | None) -> str:
    if qualifier:
        return f"{kind}:{qualifier}"
    return kind


def _node_text(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _path_name(path: str) -> str:
    return Path(path).name or path


def _parent_path(path: str) -> str | None:
    parent = Path(path).parent
    if str(parent) == ".":
        return None
    return str(parent)


def _display_detail(root: str, qualifier: str | None) -> str:
    if qualifier:
        return f"{root} / {qualifier}"
    return root


def _source_display_detail(source: Mapping[str, object]) -> str:
    owner = _node_text(source.get("module_id")) or _node_text(source.get("collection_id"))
    slot = _node_text(source.get("slot"))
    if owner and slot:
        return f"{owner} / {slot}"
    return owner or slot or "source"


def _source_display_path(source: Mapping[str, object], path: str) -> str:
    module_id = _node_text(source.get("module_id"))
    if module_id:
        prefix = ("modules", *module_id.split("/"))
        return _path_suffix(path, prefix) or "/".join((*prefix, _path_name(path)))

    collection_id = _node_text(source.get("collection_id"))
    if collection_id:
        family = _node_text(source.get("family"))
        prefix = ("collections", *(family.split("/") if family else ()), *collection_id.split("/"))
        return _path_suffix(path, prefix) or "/".join((*prefix, _path_name(path)))

    return _path_name(path)


def _path_suffix(path: str, prefix: Sequence[str]) -> str | None:
    parts = Path(path).parts
    prefix_tuple = tuple(prefix)
    if not prefix_tuple:
        return None
    for index in range(0, len(parts) - len(prefix_tuple) + 1):
        if tuple(parts[index : index + len(prefix_tuple)]) == prefix_tuple:
            return "/".join(parts[index:])
    return None


def _reference_display(target: str) -> tuple[str | None, str]:
    target_kind, separator, target_id = target.partition(":")
    if separator and target_kind and target_id:
        return target_kind, target_id
    return None, target


def _count_by(rows: list[dict[str, object]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = row.get(key)
        if isinstance(value, str):
            counts[value] = counts.get(value, 0) + 1
    return {value: counts[value] for value in sorted(counts)}


def _index_by(rows: list[dict[str, object]], key: str) -> dict[str, list[int]]:
    index: dict[str, list[int]] = {}
    for row_index, row in enumerate(rows):
        value = row.get(key)
        if isinstance(value, str):
            append_index_entry(index, value, row_index)
    return {value: index[value] for value in sorted(index)}


__all__ = ["GRAPH_SCHEMA", "build_graph"]
