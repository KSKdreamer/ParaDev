"""Source-backed Hearts of Iron IV doctrine diagram contracts.

Doctrine gameplay definitions remain in each module's canonical ``def.txt``.
ParaDev-owned visual layout and relationship state lives in the hidden
``.paradev/diagram.yaml`` file beside it.  This module operates only on exact
caller-provided snapshots; it does not discover projects or write files.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from heavenbase.utils import dumps_yaml, loads_yaml

from paradev.pdx import PDXBlock, PDXParseError, parse_pdx

from ._diagram_source import (
    is_finite_number,
    is_source_revision,
    is_utf8_text,
    stable_payload_hash,
    text_sha256,
)

DOCTRINE_DIAGRAM_STATE_SCHEMA = "paradev.hoi4.doctrine-diagram-state.v1"
DOCTRINE_DIAGRAM_PROJECTION_SCHEMA = "paradev.hoi4.doctrine-diagram-projection.v1"
DOCTRINE_DIAGRAM_PLAN_SCHEMA = "paradev.hoi4.doctrine-diagram-plan.v1"

__all__ = [
    "DOCTRINE_DIAGRAM_PLAN_SCHEMA",
    "DOCTRINE_DIAGRAM_PROJECTION_SCHEMA",
    "DOCTRINE_DIAGRAM_STATE_SCHEMA",
    "DoctrineEdgeIntent",
    "DoctrinePositionIntent",
    "DoctrineSource",
    "doctrine_diagram_projection",
    "plan_doctrine_diagram_edits",
]

_DIAGRAM_STATE_KEYS = frozenset(
    {
        "schema",
        "position",
        "paths",
        "mutually_exclusive",
    }
)
_EDGE_KINDS = frozenset({"mutually_exclusive", "path"})
_ERROR = "error"
_WARNING = "warning"


@dataclass(frozen=True, slots=True)
class DoctrineSource:
    """One reviewed doctrine module source bundle.

    Args:
        object_id: Stable logical module identifier used by ParaDev.
        module_id: Canonical ``doctrine/<object_id>`` module identifier.
        definition_path: Project-relative canonical ``def.txt`` path.
        definition_text: Complete UTF-8 doctrine definition text.
        diagram_path: Project-relative hidden diagram-state path.
        diagram_text: Complete UTF-8 diagram-state text, or ``None`` when a
            module has not been initialized for guarded diagram editing.
    """

    object_id: str
    module_id: str
    definition_path: str
    definition_text: str
    diagram_path: str
    diagram_text: str | None


@dataclass(frozen=True, slots=True)
class DoctrinePositionIntent:
    """Reviewed absolute position for one doctrine node.

    Args:
        doctrine_id: Logical doctrine module identifier.
        x: Desired finite horizontal coordinate.
        y: Desired finite vertical coordinate.
        source_revision: Exact hidden-state revision from the projection.
    """

    doctrine_id: str
    x: int | float
    y: int | float
    source_revision: str


@dataclass(frozen=True, slots=True)
class DoctrineEdgeIntent:
    """Reviewed desired presence of one doctrine relationship.

    ``path`` is directed from ``source_id`` to ``target_id``.
    ``mutually_exclusive`` is stored symmetrically in both endpoint states.

    Args:
        kind: ``path`` or ``mutually_exclusive``.
        source_id: Logical source doctrine identifier.
        target_id: Logical target doctrine identifier.
        present: Whether the relationship should exist after the edit.
        source_revision: Exact hidden-state revision of ``source_id``.
    """

    kind: str
    source_id: str
    target_id: str
    present: bool
    source_revision: str


@dataclass(frozen=True, slots=True)
class _TextDocument:
    path: str
    text: str
    sha256: str
    revision: str


@dataclass(frozen=True, slots=True)
class _DiagramState:
    position: tuple[int | float, int | float]
    paths: tuple[str, ...]
    mutually_exclusive: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _DoctrineRecord:
    object_id: str
    module_id: str
    compiled_id: str | None
    definition: _TextDocument
    diagram: _TextDocument | None
    state: _DiagramState | None


@dataclass(frozen=True, slots=True)
class _Diagnostic:
    code: str
    message: str
    severity: str = _ERROR
    doctrine_id: str | None = None
    source_path: str | None = None

    def to_dict(self) -> dict[str, object]:
        row: dict[str, object] = {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
        }
        if self.doctrine_id is not None:
            row["doctrine_id"] = self.doctrine_id
        if self.source_path is not None:
            row["source_path"] = self.source_path
        return row


@dataclass(frozen=True, slots=True)
class _DoctrineModel:
    records: tuple[_DoctrineRecord, ...]
    edges: tuple[dict[str, object], ...]
    diagnostics: tuple[_Diagnostic, ...]


def doctrine_diagram_projection(
    sources: Sequence[DoctrineSource | Mapping[str, object]],
) -> dict[str, object]:
    """Project exact doctrine module sources into one deterministic graph.

    Args:
        sources: Reviewed module snapshots. Mapping rows use the same fields
            as :class:`DoctrineSource`.

    Returns:
        JSON-safe nodes, path and mutual-exclusion edges, source revisions,
        diagnostics, and explicit editability.
    """

    model = _doctrine_model(sources)
    duplicate_ids = _duplicates(record.object_id for record in model.records)
    duplicate_compiled_ids = _duplicates(record.compiled_id for record in model.records if record.compiled_id is not None)
    nodes = [
        _node(
            record,
            duplicate=(record.object_id in duplicate_ids or record.compiled_id in duplicate_compiled_ids),
        )
        for record in sorted(
            model.records,
            key=lambda row: (row.object_id, row.definition.path),
        )
    ]
    diagnostics = _sorted_diagnostics(model.diagnostics)
    edge_counts = Counter(str(edge["kind"]) for edge in model.edges)
    editable_nodes = sum(row.get("editable") is True for row in nodes)
    return {
        "schema": DOCTRINE_DIAGRAM_PROJECTION_SCHEMA,
        "source_kind": "module_doctrine_definition_and_hidden_diagram_state",
        "editable": bool(editable_nodes) and not any(row.severity == _ERROR for row in diagnostics),
        "sources": [
            source
            for record in sorted(
                model.records,
                key=lambda row: (row.object_id, row.definition.path),
            )
            for source in _source_rows(record)
        ],
        "nodes": nodes,
        "edges": list(model.edges),
        "diagnostics": [row.to_dict() for row in diagnostics],
        "summary": {
            "source_count": sum(1 + (record.diagram is not None) for record in model.records),
            "definition_count": len(model.records),
            "diagram_state_count": sum(record.diagram is not None for record in model.records),
            "node_count": len(nodes),
            "editable_node_count": editable_nodes,
            "edge_count": len(model.edges),
            "edge_counts": {kind: edge_counts[kind] for kind in sorted(edge_counts)},
            "diagnostic_count": len(diagnostics),
        },
    }


def plan_doctrine_diagram_edits(
    sources: Sequence[DoctrineSource | Mapping[str, object]],
    *,
    position_intents: Sequence[DoctrinePositionIntent | Mapping[str, object]] = (),
    edge_intents: Sequence[DoctrineEdgeIntent | Mapping[str, object]] = (),
    pending_node_ids: Sequence[str] = (),
) -> dict[str, object]:
    """Plan exact hidden-state drafts for reviewed doctrine diagram edits.

    Planning is pure and deterministic. Every position and relationship
    request is revision guarded; an ambiguous, malformed, or stale request
    blocks the complete plan and returns no drafts.

    Args:
        sources: Current exact doctrine module snapshots.
        position_intents: Reviewed absolute node-position intents.
        edge_intents: Reviewed path or mutual-exclusion intents.
        pending_node_ids: New node ids installed by the enclosing transaction.
            A directed path may target one of these ids, but a mutual exclusion
            still requires two existing editable endpoint states.

    Returns:
        Stable-hash plan with complete hidden YAML drafts, or fail-closed
        diagnostics when no safe transaction can be formed.
    """

    model = _doctrine_model(sources)
    diagnostics = list(model.diagnostics)
    positions, position_diagnostics = _position_intents(position_intents)
    edges, edge_diagnostics = _edge_intents(edge_intents)
    pending_nodes, pending_diagnostics = _pending_node_ids(pending_node_ids)
    diagnostics.extend(position_diagnostics)
    diagnostics.extend(edge_diagnostics)
    diagnostics.extend(pending_diagnostics)

    records = _unique_records(model.records)
    for doctrine_id in sorted(pending_nodes & records.keys()):
        diagnostics.append(
            _Diagnostic(
                code="doctrine.plan.pending_node_exists",
                message=f"Pending doctrine {doctrine_id!r} already exists.",
                doctrine_id=doctrine_id,
            )
        )
    states = {doctrine_id: _mutable_state(record.state) for doctrine_id, record in records.items() if record.state is not None}
    changed_fields: dict[str, set[str]] = defaultdict(set)

    for intent in positions:
        record = records.get(intent.doctrine_id)
        if record is None or record.diagram is None or record.state is None:
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.plan.node_uneditable",
                    message=(f"Doctrine {intent.doctrine_id!r} has no unique " "initialized hidden diagram state."),
                    doctrine_id=intent.doctrine_id,
                )
            )
            continue
        if intent.source_revision != record.diagram.revision:
            diagnostics.append(_stale_revision(record, intent.source_revision))
            continue
        state = states[intent.doctrine_id]
        position = {"x": intent.x, "y": intent.y}
        if state["position"] != position:
            state["position"] = position
            changed_fields[intent.doctrine_id].add("position")

    existing_edges = {
        (
            str(edge["kind"]),
            str(edge["source"]),
            str(edge["target"]),
        )
        for edge in model.edges
    }
    for intent in edges:
        source = records.get(intent.source_id)
        target = records.get(intent.target_id)
        target_is_pending = intent.target_id in pending_nodes
        if source is None or source.diagram is None or source.state is None:
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.plan.edge_owner_uneditable",
                    message=(f"Doctrine relationship {intent.source_id!r} -> " f"{intent.target_id!r} has no unique editable source."),
                    doctrine_id=intent.source_id,
                )
            )
            continue
        if intent.source_revision != source.diagram.revision:
            diagnostics.append(_stale_revision(source, intent.source_revision))
            continue
        if target_is_pending and (intent.kind != "path" or not intent.present):
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.plan.pending_edge_unsupported",
                    message=(f"Pending doctrine {intent.target_id!r} may only be the " "present target of a directed path."),
                    doctrine_id=intent.target_id,
                )
            )
            continue
        if not target_is_pending and (target is None or target.diagram is None or target.state is None):
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.plan.edge_target_uneditable",
                    message=(f"Doctrine relationship {intent.source_id!r} -> " f"{intent.target_id!r} requires both endpoint states."),
                    doctrine_id=intent.target_id,
                )
            )
            continue

        edge_key = (
            intent.kind,
            *(sorted((intent.source_id, intent.target_id)) if intent.kind == "mutually_exclusive" else (intent.source_id, intent.target_id)),
        )
        if intent.present == (edge_key in existing_edges):
            continue
        if intent.kind == "path":
            _set_member(
                states[intent.source_id]["paths"],
                intent.target_id,
                intent.present,
            )
            changed_fields[intent.source_id].add("paths")
            continue
        _set_member(
            states[intent.source_id]["mutually_exclusive"],
            intent.target_id,
            intent.present,
        )
        _set_member(
            states[intent.target_id]["mutually_exclusive"],
            intent.source_id,
            intent.present,
        )
        changed_fields[intent.source_id].add("mutually_exclusive")
        changed_fields[intent.target_id].add("mutually_exclusive")

    diagnostics = list(_sorted_diagnostics(diagnostics))
    blocked = any(row.severity == _ERROR for row in diagnostics)
    drafts: list[dict[str, object]] = []
    replacements: list[dict[str, object]] = []
    if not blocked:
        for doctrine_id in sorted(changed_fields):
            record = records[doctrine_id]
            if record.diagram is None:
                raise AssertionError("Changed doctrine state has no exact source document.")
            text = _render_state(states[doctrine_id])
            if text == record.diagram.text:
                continue
            digest = text_sha256(text)
            drafts.append(
                {
                    "path": record.diagram.path,
                    "expected_source_revision": record.diagram.revision,
                    "expected_sha256": record.diagram.sha256,
                    "text": text,
                    "sha256": digest,
                    "source_revision": f"sha256:{digest}",
                }
            )
            replacements.append(
                {
                    "path": record.diagram.path,
                    "fields": sorted(changed_fields[doctrine_id]),
                }
            )

    if blocked:
        drafts = []
        replacements = []
    status = "blocked" if blocked else "planned" if drafts else "unchanged"
    intent_rows = {
        "positions": [
            {
                "doctrine_id": row.doctrine_id,
                "x": row.x,
                "y": row.y,
                "source_revision": row.source_revision,
            }
            for row in positions
        ],
        "edges": [
            {
                "kind": row.kind,
                "source_id": row.source_id,
                "target_id": row.target_id,
                "present": row.present,
                "source_revision": row.source_revision,
            }
            for row in edges
        ],
        "pending_node_ids": sorted(pending_nodes),
    }
    plan: dict[str, object] = {
        "schema": DOCTRINE_DIAGRAM_PLAN_SCHEMA,
        "projection_schema": DOCTRINE_DIAGRAM_PROJECTION_SCHEMA,
        "status": status,
        "write": False,
        "sources": [
            source
            for record in sorted(
                model.records,
                key=lambda row: (row.object_id, row.definition.path),
            )
            for source in _source_rows(record)
        ],
        "intents": intent_rows,
        "source_replacements": replacements,
        "drafts": drafts,
        "diagnostics": [row.to_dict() for row in diagnostics],
        "summary": {
            "position_intent_count": len(positions),
            "edge_intent_count": len(edges),
            "replacement_count": len(replacements),
            "draft_count": len(drafts),
            "diagnostic_count": len(diagnostics),
        },
    }
    plan["plan_hash"] = stable_payload_hash(plan)
    return plan


def _doctrine_model(
    sources: Sequence[DoctrineSource | Mapping[str, object]],
) -> _DoctrineModel:
    diagnostics: list[_Diagnostic] = []
    records: list[_DoctrineRecord] = []
    for index, value in enumerate(sources):
        source = _normalize_source(value, index, diagnostics)
        if source is None:
            continue
        definition = _text_document(
            source.definition_path,
            source.definition_text,
            label=f"Doctrine source record {index} definition",
            diagnostics=diagnostics,
        )
        if definition is None:
            continue
        compiled_id = _compiled_id(
            source.object_id,
            definition,
            diagnostics,
        )
        diagram: _TextDocument | None = None
        state: _DiagramState | None = None
        if source.diagram_text is None:
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.state.missing",
                    message=(f"Doctrine {source.object_id!r} has no hidden " ".paradev/diagram.yaml state and is view-only."),
                    severity=_WARNING,
                    doctrine_id=source.object_id,
                    source_path=source.diagram_path,
                )
            )
        else:
            diagram = _text_document(
                source.diagram_path,
                source.diagram_text,
                label=f"Doctrine source record {index} diagram state",
                diagnostics=diagnostics,
            )
            if diagram is not None:
                state = _diagram_state(
                    source.object_id,
                    diagram,
                    diagnostics,
                )
        records.append(
            _DoctrineRecord(
                object_id=source.object_id,
                module_id=source.module_id,
                compiled_id=compiled_id,
                definition=definition,
                diagram=diagram,
                state=state,
            )
        )

    for doctrine_id in sorted(_duplicates(record.object_id for record in records)):
        diagnostics.append(
            _Diagnostic(
                code="doctrine.node.duplicate_id",
                message=(f"Doctrine {doctrine_id!r} is declared by more than one " "reviewed module."),
                doctrine_id=doctrine_id,
            )
        )
    for compiled_id in sorted(_duplicates(record.compiled_id for record in records if record.compiled_id is not None)):
        diagnostics.append(
            _Diagnostic(
                code="doctrine.node.duplicate_compiled_id",
                message=(f"Compiled doctrine id {compiled_id!r} is declared by " "more than one reviewed module."),
            )
        )

    edges = _edges(records, diagnostics)
    return _DoctrineModel(
        records=tuple(records),
        edges=tuple(edges),
        diagnostics=_sorted_diagnostics(diagnostics),
    )


def _normalize_source(
    value: DoctrineSource | Mapping[str, object],
    index: int,
    diagnostics: list[_Diagnostic],
) -> DoctrineSource | None:
    if isinstance(value, DoctrineSource):
        source = value
    elif isinstance(value, Mapping):
        fields = {
            "object_id": value.get("object_id"),
            "module_id": value.get("module_id"),
            "definition_path": value.get("definition_path"),
            "definition_text": value.get("definition_text"),
            "diagram_path": value.get("diagram_path"),
            "diagram_text": value.get("diagram_text"),
        }
        if not all(
            isinstance(fields[key], str)
            for key in (
                "object_id",
                "module_id",
                "definition_path",
                "definition_text",
                "diagram_path",
            )
        ) or not (fields["diagram_text"] is None or isinstance(fields["diagram_text"], str)):
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.source.invalid_record",
                    message=(f"Doctrine source record {index} has invalid or " "missing identity, path, or text fields."),
                )
            )
            return None
        source = DoctrineSource(
            object_id=str(fields["object_id"]),
            module_id=str(fields["module_id"]),
            definition_path=str(fields["definition_path"]),
            definition_text=str(fields["definition_text"]),
            diagram_path=str(fields["diagram_path"]),
            diagram_text=(str(fields["diagram_text"]) if fields["diagram_text"] is not None else None),
        )
    else:
        diagnostics.append(
            _Diagnostic(
                code="doctrine.source.invalid_record",
                message=(f"Doctrine source record {index} is not a DoctrineSource " "or mapping."),
            )
        )
        return None

    strings = (
        source.object_id,
        source.module_id,
        source.definition_path,
        source.definition_text,
        source.diagram_path,
    )
    if any(not is_utf8_text(text) for text in strings):
        diagnostics.append(
            _Diagnostic(
                code="doctrine.source.invalid_utf8",
                message=(f"Doctrine source record {index} contains text that " "cannot be encoded as UTF-8."),
            )
        )
        return None
    if (
        not source.object_id.strip()
        or source.module_id != f"doctrine/{source.object_id}"
        or not source.definition_path.endswith("/def.txt")
        or not source.diagram_path.endswith("/.paradev/diagram.yaml")
    ):
        diagnostics.append(
            _Diagnostic(
                code="doctrine.source.invalid_identity",
                message=(f"Doctrine source record {index} must use one canonical " "module id, def.txt, and .paradev/diagram.yaml path."),
            )
        )
        return None
    return source


def _text_document(
    path: str,
    text: str,
    *,
    label: str,
    diagnostics: list[_Diagnostic],
) -> _TextDocument | None:
    if not path.strip() or not is_utf8_text(path) or not is_utf8_text(text):
        diagnostics.append(
            _Diagnostic(
                code="doctrine.source.invalid_text",
                message=f"{label} must contain non-empty UTF-8 path and text.",
            )
        )
        return None
    digest = text_sha256(text)
    return _TextDocument(
        path=path,
        text=text,
        sha256=digest,
        revision=f"sha256:{digest}",
    )


def _compiled_id(
    doctrine_id: str,
    document: _TextDocument,
    diagnostics: list[_Diagnostic],
) -> str | None:
    try:
        root = parse_pdx(document.text)
    except PDXParseError as error:
        detail = "; ".join(diagnostic.message for diagnostic in error.diagnostics)
        diagnostics.append(
            _Diagnostic(
                code="doctrine.definition.invalid_pdx",
                message=(f"Doctrine {doctrine_id!r} def.txt is invalid PDX: " f"{detail or 'unknown parser failure'}."),
                doctrine_id=doctrine_id,
                source_path=document.path,
            )
        )
        return None
    entries = [entry for entry in root.entries if entry.key_str and isinstance(entry.val, PDXBlock)]
    if len(entries) != 1:
        diagnostics.append(
            _Diagnostic(
                code="doctrine.definition.ambiguous_root",
                message=(f"Doctrine {doctrine_id!r} def.txt must contain exactly " "one top-level doctrine block."),
                doctrine_id=doctrine_id,
                source_path=document.path,
            )
        )
        return None
    return entries[0].key_str


def _diagram_state(
    doctrine_id: str,
    document: _TextDocument,
    diagnostics: list[_Diagnostic],
) -> _DiagramState | None:
    try:
        value = loads_yaml(document.text)
    except Exception:
        diagnostics.append(
            _Diagnostic(
                code="doctrine.state.invalid_yaml",
                message=(f"Doctrine {doctrine_id!r} hidden diagram state must be " "valid single-document YAML."),
                doctrine_id=doctrine_id,
                source_path=document.path,
            )
        )
        return None
    if not isinstance(value, Mapping):
        diagnostics.append(
            _Diagnostic(
                code="doctrine.state.invalid_mapping",
                message=(f"Doctrine {doctrine_id!r} hidden diagram state must be " "a YAML mapping."),
                doctrine_id=doctrine_id,
                source_path=document.path,
            )
        )
        return None
    unknown = sorted(str(key) for key in value if not isinstance(key, str) or key not in _DIAGRAM_STATE_KEYS)
    position = value.get("position")
    paths = _identifier_list(value.get("paths"))
    mutually_exclusive = _identifier_list(value.get("mutually_exclusive"))
    valid = (
        value.get("schema") == DOCTRINE_DIAGRAM_STATE_SCHEMA
        and isinstance(position, Mapping)
        and set(position) == {"x", "y"}
        and is_finite_number(position.get("x"))
        and is_finite_number(position.get("y"))
        and paths is not None
        and mutually_exclusive is not None
        and not unknown
    )
    if not valid:
        diagnostics.append(
            _Diagnostic(
                code="doctrine.state.invalid_contract",
                message=(
                    f"Doctrine {doctrine_id!r} hidden diagram state must use "
                    f"{DOCTRINE_DIAGRAM_STATE_SCHEMA!r}, one finite x/y "
                    "position, and string path/reference lists."
                ),
                doctrine_id=doctrine_id,
                source_path=document.path,
            )
        )
        return None
    return _DiagramState(
        position=(position["x"], position["y"]),
        paths=paths,
        mutually_exclusive=mutually_exclusive,
    )


def _identifier_list(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or any(not isinstance(item, str) or not item.strip() for item in value):
        return None
    rows = tuple(item.strip() for item in value)
    return rows if len(rows) == len(set(rows)) else None


def _edges(
    records: Sequence[_DoctrineRecord],
    diagnostics: list[_Diagnostic],
) -> list[dict[str, object]]:
    known = {record.object_id for record in records}
    path_edges: dict[tuple[str, str], dict[str, object]] = {}
    mutual_owners: dict[
        tuple[str, str],
        list[_DoctrineRecord],
    ] = defaultdict(list)
    for record in records:
        if record.state is None or record.diagram is None:
            continue
        for target in record.state.paths:
            key = (record.object_id, target)
            if key in path_edges:
                diagnostics.append(
                    _Diagnostic(
                        code="doctrine.edge.duplicate_path",
                        message=(f"Doctrine path {record.object_id!r} -> " f"{target!r} is declared more than once."),
                        severity=_WARNING,
                        doctrine_id=record.object_id,
                        source_path=record.diagram.path,
                    )
                )
                continue
            path_edges[key] = {
                "kind": "path",
                "source": record.object_id,
                "target": target,
                "owner_id": record.object_id,
                "source_path": record.diagram.path,
                "source_revision": record.diagram.revision,
                "editable": target in known,
            }
        for target in record.state.mutually_exclusive:
            mutual_owners[tuple(sorted((record.object_id, target)))].append(record)

    edges = list(path_edges.values())
    for (source, target), owners in sorted(mutual_owners.items()):
        unique_owners = {owner.object_id: owner for owner in owners}
        owner_rows = [unique_owners[key] for key in sorted(unique_owners)]
        edges.append(
            {
                "kind": "mutually_exclusive",
                "source": source,
                "target": target,
                "owner_ids": [row.object_id for row in owner_rows],
                "source_paths": [row.diagram.path for row in owner_rows if row.diagram is not None],
                "editable": (source in known and target in known and {source, target} == set(unique_owners)),
            }
        )
        if {source, target} != set(unique_owners):
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.edge.mutual_asymmetry",
                    message=(f"Doctrine mutual exclusion {source!r} ↔ " f"{target!r} is not declared by both endpoints."),
                    severity=_WARNING,
                )
            )

    for edge in edges:
        if edge["source"] not in known or edge["target"] not in known:
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.edge.unresolved",
                    message=(
                        f"Doctrine {edge['kind']} relationship " f"{edge['source']!r} -> {edge['target']!r} has an " "endpoint outside the reviewed modules."
                    ),
                    severity=_WARNING,
                )
            )
    return sorted(
        edges,
        key=lambda row: (
            str(row["kind"]),
            str(row["source"]),
            str(row["target"]),
        ),
    )


def _node(
    record: _DoctrineRecord,
    *,
    duplicate: bool,
) -> dict[str, object]:
    editable = not duplicate and record.compiled_id is not None and record.diagram is not None and record.state is not None
    row: dict[str, object] = {
        "id": record.object_id,
        "module_id": record.module_id,
        "compiled_id": record.compiled_id,
        "source_path": record.definition.path,
        "definition_source_revision": record.definition.revision,
        "editable": editable,
    }
    if record.diagram is not None:
        row["diagram_source_path"] = record.diagram.path
        row["source_revision"] = record.diagram.revision
    else:
        row["source_revision"] = record.definition.revision
    if record.state is not None:
        row["x"], row["y"] = record.state.position
    return row


def _source_rows(record: _DoctrineRecord) -> list[dict[str, object]]:
    rows = [
        {
            "path": record.definition.path,
            "kind": "definition",
            "module_id": record.module_id,
            "source_revision": record.definition.revision,
            "sha256": record.definition.sha256,
            "size": len(record.definition.text.encode("utf-8")),
        }
    ]
    if record.diagram is not None:
        rows.append(
            {
                "path": record.diagram.path,
                "kind": "diagram_state",
                "module_id": record.module_id,
                "source_revision": record.diagram.revision,
                "sha256": record.diagram.sha256,
                "size": len(record.diagram.text.encode("utf-8")),
            }
        )
    return rows


def _position_intents(
    values: Sequence[DoctrinePositionIntent | Mapping[str, object]],
) -> tuple[list[DoctrinePositionIntent], list[_Diagnostic]]:
    rows: list[DoctrinePositionIntent] = []
    diagnostics: list[_Diagnostic] = []
    seen: dict[str, DoctrinePositionIntent] = {}
    for index, value in enumerate(values):
        if isinstance(value, DoctrinePositionIntent):
            row = value
        elif isinstance(value, Mapping):
            row = DoctrinePositionIntent(
                doctrine_id=value.get("doctrine_id"),  # type: ignore[arg-type]
                x=value.get("x"),  # type: ignore[arg-type]
                y=value.get("y"),  # type: ignore[arg-type]
                source_revision=value.get("source_revision"),  # type: ignore[arg-type]
            )
        else:
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.plan.invalid_position_intent",
                    message=f"Doctrine position intent {index} is not an object.",
                )
            )
            continue
        valid = (
            isinstance(row.doctrine_id, str)
            and bool(row.doctrine_id.strip())
            and is_finite_number(row.x)
            and is_finite_number(row.y)
            and is_source_revision(row.source_revision)
        )
        if not valid:
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.plan.invalid_position_intent",
                    message=(f"Doctrine position intent {index} requires a " "doctrine_id, finite x/y, and canonical source revision."),
                )
            )
            continue
        normalized = DoctrinePositionIntent(
            doctrine_id=row.doctrine_id.strip(),
            x=row.x,
            y=row.y,
            source_revision=row.source_revision,
        )
        previous = seen.get(normalized.doctrine_id)
        if previous is not None and previous != normalized:
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.plan.conflicting_position_intents",
                    message=(f"Doctrine {normalized.doctrine_id!r} has conflicting " "position intents."),
                    doctrine_id=normalized.doctrine_id,
                )
            )
            continue
        if previous is None:
            seen[normalized.doctrine_id] = normalized
            rows.append(normalized)
    return sorted(rows, key=lambda row: row.doctrine_id), diagnostics


def _pending_node_ids(
    values: Sequence[str],
) -> tuple[set[str], list[_Diagnostic]]:
    """Normalize ids created by the transaction enclosing this pure plan."""

    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        return set(), [
            _Diagnostic(
                code="doctrine.plan.invalid_pending_nodes",
                message="Doctrine pending_node_ids must be an array of unique ids.",
            )
        ]
    rows: list[str] = []
    diagnostics: list[_Diagnostic] = []
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.plan.invalid_pending_node",
                    message=f"Pending doctrine id {index} must be non-empty text.",
                )
            )
            continue
        rows.append(value.strip())
    duplicates = _duplicates(rows)
    for doctrine_id in sorted(duplicates):
        diagnostics.append(
            _Diagnostic(
                code="doctrine.plan.duplicate_pending_node",
                message=f"Pending doctrine {doctrine_id!r} is listed more than once.",
                doctrine_id=doctrine_id,
            )
        )
    return set(rows), diagnostics


def _edge_intents(
    values: Sequence[DoctrineEdgeIntent | Mapping[str, object]],
) -> tuple[list[DoctrineEdgeIntent], list[_Diagnostic]]:
    rows: list[DoctrineEdgeIntent] = []
    diagnostics: list[_Diagnostic] = []
    seen: dict[tuple[str, str, str], DoctrineEdgeIntent] = {}
    for index, value in enumerate(values):
        if isinstance(value, DoctrineEdgeIntent):
            row = value
        elif isinstance(value, Mapping):
            row = DoctrineEdgeIntent(
                kind=value.get("kind"),  # type: ignore[arg-type]
                source_id=value.get("source_id"),  # type: ignore[arg-type]
                target_id=value.get("target_id"),  # type: ignore[arg-type]
                present=value.get("present"),  # type: ignore[arg-type]
                source_revision=value.get("source_revision"),  # type: ignore[arg-type]
            )
        else:
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.plan.invalid_edge_intent",
                    message=f"Doctrine edge intent {index} is not an object.",
                )
            )
            continue
        valid = (
            isinstance(row.kind, str)
            and row.kind in _EDGE_KINDS
            and isinstance(row.source_id, str)
            and bool(row.source_id.strip())
            and isinstance(row.target_id, str)
            and bool(row.target_id.strip())
            and row.source_id.strip() != row.target_id.strip()
            and isinstance(row.present, bool)
            and is_source_revision(row.source_revision)
        )
        if not valid:
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.plan.invalid_edge_intent",
                    message=(
                        f"Doctrine edge intent {index} requires a supported " "kind, distinct endpoints, boolean presence, and " "canonical source revision."
                    ),
                )
            )
            continue
        normalized = DoctrineEdgeIntent(
            kind=row.kind,
            source_id=row.source_id.strip(),
            target_id=row.target_id.strip(),
            present=row.present,
            source_revision=row.source_revision,
        )
        key = (
            normalized.kind,
            *(
                sorted((normalized.source_id, normalized.target_id))
                if normalized.kind == "mutually_exclusive"
                else (normalized.source_id, normalized.target_id)
            ),
        )
        previous = seen.get(key)
        if previous is not None and previous.present != normalized.present:
            diagnostics.append(
                _Diagnostic(
                    code="doctrine.plan.conflicting_edge_intents",
                    message=(f"Doctrine {normalized.kind} relationship " f"{normalized.source_id!r} -> " f"{normalized.target_id!r} has conflicting intents."),
                )
            )
            continue
        if previous is None:
            seen[key] = normalized
            rows.append(normalized)
    return (
        sorted(
            rows,
            key=lambda row: (row.kind, row.source_id, row.target_id),
        ),
        diagnostics,
    )


def _unique_records(
    records: Sequence[_DoctrineRecord],
) -> dict[str, _DoctrineRecord]:
    counts = Counter(record.object_id for record in records)
    return {record.object_id: record for record in records if counts[record.object_id] == 1}


def _mutable_state(state: _DiagramState | None) -> dict[str, object]:
    if state is None:
        raise ValueError("Doctrine diagram state is unavailable.")
    return {
        "position": {"x": state.position[0], "y": state.position[1]},
        "paths": set(state.paths),
        "mutually_exclusive": set(state.mutually_exclusive),
    }


def _set_member(values: object, target: str, present: bool) -> None:
    if not isinstance(values, set):
        raise AssertionError("Doctrine diagram relationship state is invalid.")
    if present:
        values.add(target)
    else:
        values.discard(target)


def _render_state(state: Mapping[str, object]) -> str:
    position = state["position"]
    paths = state["paths"]
    mutually_exclusive = state["mutually_exclusive"]
    if not isinstance(position, Mapping) or not isinstance(paths, set) or not isinstance(mutually_exclusive, set):
        raise AssertionError("Doctrine diagram draft state is invalid.")
    return dumps_yaml(
        {
            "schema": DOCTRINE_DIAGRAM_STATE_SCHEMA,
            "position": {
                "x": position["x"],
                "y": position["y"],
            },
            "paths": sorted(paths),
            "mutually_exclusive": sorted(mutually_exclusive),
        },
        sort_keys=False,
    )


def _stale_revision(
    record: _DoctrineRecord,
    provided: str,
) -> _Diagnostic:
    expected = record.diagram.revision if record.diagram is not None else record.definition.revision
    return _Diagnostic(
        code="doctrine.plan.source_revision_mismatch",
        message=(f"Doctrine {record.object_id!r} changed after the diagram was " f"loaded; expected {expected!r}, received {provided!r}."),
        doctrine_id=record.object_id,
        source_path=(record.diagram.path if record.diagram is not None else record.definition.path),
    )


def _duplicates(values: Iterable[str]) -> set[str]:
    rows = list(values)
    counts = Counter(rows)
    return {value for value, count in counts.items() if count > 1}


def _sorted_diagnostics(
    diagnostics: Sequence[_Diagnostic],
) -> tuple[_Diagnostic, ...]:
    return tuple(
        sorted(
            diagnostics,
            key=lambda row: (
                0 if row.severity == _ERROR else 1,
                row.code,
                row.doctrine_id or "",
                row.source_path or "",
                row.message,
            ),
        )
    )
