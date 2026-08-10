"""Source-backed Hearts of Iron IV technology diagram contracts.

This module deliberately works from reviewed ``def.txt`` source text. It does
not discover modules, read metadata, inspect legacy summaries, or write files.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from paradev.pdx import PDXBlock, PDXEntry, PDXParseError, PDXScalar, parse_pdx

from ._diagram_source import (
    DiagramSourceDocument as _SourceDocument,
    DiagramSourceReplacement as _Replacement,
    UnsafeSourcePatch as _UnsafePatch,
    block_child_insertion as _block_child_insertion,
    entry_number as _entry_number,
    entry_scalar_text as _entry_scalar_text,
    format_number as _format_number,
    indent_unit as _indent_unit,
    is_finite_number as _is_number,
    is_source_revision as _is_source_revision,
    is_utf8_text as _is_utf8_text,
    lex_pdx_tokens as _lex_tokens,
    merge_source_replacements as _merge_and_validate_replacements,
    render_source_drafts as _render_drafts,
    scalar_text as _scalar_text,
    scalar_token as _scalar_token,
    source_newline as _newline,
    source_span as _source_span,
    stable_payload_hash as _stable_hash,
    text_sha256 as _text_sha256,
    whole_entry_line_replacement as _whole_entry_line_replacement,
)

TECHNOLOGY_DIAGRAM_PROJECTION_SCHEMA = "paradev.hoi4.technology-diagram-projection.v1"
TECHNOLOGY_DIAGRAM_PLAN_SCHEMA = "paradev.hoi4.technology-diagram-plan.v1"

__all__ = [
    "TECHNOLOGY_DIAGRAM_PLAN_SCHEMA",
    "TECHNOLOGY_DIAGRAM_PROJECTION_SCHEMA",
    "TechnologyEdgeIntent",
    "TechnologyPositionIntent",
    "TechnologySource",
    "plan_technology_diagram_edits",
    "technology_diagram_projection",
]

_EDGE_KINDS = frozenset({"dependency", "path"})
_ERROR = "error"
_WARNING = "warning"


@dataclass(frozen=True, slots=True)
class TechnologySource:
    """One reviewed technology module ``def.txt`` source.

    Args:
        path: Stable reader-facing path ending in ``def.txt``.
        text: Complete UTF-8-decoded PDX source, preserving its BOM and newline
            bytes without universal-newline normalization.
    """

    path: str
    text: str


@dataclass(frozen=True, slots=True)
class TechnologyPositionIntent:
    """Reviewed absolute position for one technology node.

    Args:
        technology_id: Game-facing technology identifier.
        x: Desired finite horizontal coordinate.
        y: Desired finite vertical coordinate.
        source_revision: Exact revision exposed by the reviewed projection.
    """

    technology_id: str
    x: int | float
    y: int | float
    source_revision: str


@dataclass(frozen=True, slots=True)
class TechnologyEdgeIntent:
    """Reviewed desired presence of one dependency or path edge.

    Edges always point from prerequisite ``source_id`` to dependent
    ``target_id``. A dependency is stored on the target technology, while a
    path is stored on the source technology.

    Args:
        kind: ``dependency`` or ``path``.
        source_id: Prerequisite technology identifier.
        target_id: Dependent technology identifier.
        present: Whether the edge should exist after applying the draft.
        source_revision: Exact revision of the source file that owns the edge.
    """

    kind: str
    source_id: str
    target_id: str
    present: bool
    source_revision: str


@dataclass(frozen=True, slots=True)
class _Diagnostic:
    code: str
    message: str
    severity: str = _ERROR
    source_path: str | None = None
    technology_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        row: dict[str, object] = {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
        }
        if self.source_path is not None:
            row["source_path"] = self.source_path
        if self.technology_id is not None:
            row["technology_id"] = self.technology_id
        return row


@dataclass(frozen=True, slots=True)
class _TechnologyRecord:
    technology_id: str
    document: _SourceDocument
    entry: PDXEntry
    block: PDXBlock


@dataclass(frozen=True, slots=True)
class _TechnologyModel:
    documents: tuple[_SourceDocument, ...]
    records: tuple[_TechnologyRecord, ...]
    edges: tuple[dict[str, object], ...]
    diagnostics: tuple[_Diagnostic, ...]


@dataclass(frozen=True, slots=True)
class _PositionChange:
    technology_id: str
    x: int | float
    y: int | float
    source_revision: str


@dataclass(frozen=True, slots=True)
class _EdgeChange:
    kind: str
    source_id: str
    target_id: str
    present: bool
    source_revision: str


def technology_diagram_projection(
    sources: Sequence[TechnologySource | Mapping[str, object]],
) -> dict[str, object]:
    """Return a deterministic technology graph projected from ``def.txt``.

    Args:
        sources: Exact reviewed source snapshots. Mapping records use ``path``
            and ``text`` fields; callers must decode raw UTF-8 bytes without
            normalizing newlines.

    Returns:
        A JSON-safe graph with technology nodes, dependency/path edges,
        content-derived source revisions, and fail-closed diagnostics.
    """

    model = _technology_model(sources)
    duplicate_ids = _duplicate_technology_ids(model.records)
    nodes = [
        _technology_node(record, duplicate=record.technology_id in duplicate_ids)
        for record in sorted(model.records, key=lambda row: (row.technology_id, row.document.path))
    ]
    diagnostics = _sorted_diagnostics(model.diagnostics)
    edge_counts = Counter(str(edge["kind"]) for edge in model.edges)
    return {
        "schema": TECHNOLOGY_DIAGRAM_PROJECTION_SCHEMA,
        "source_kind": "module_def_pdx",
        "editable": bool(nodes) and not any(row.severity == _ERROR for row in diagnostics),
        "sources": [
            {
                "path": document.path,
                "source_revision": document.revision,
                "sha256": document.sha256,
                "size": len(document.text.encode("utf-8")),
            }
            for document in model.documents
        ],
        "nodes": nodes,
        "edges": list(model.edges),
        "diagnostics": [row.to_dict() for row in diagnostics],
        "summary": {
            "source_count": len(model.documents),
            "node_count": len(nodes),
            "edge_count": len(model.edges),
            "edge_counts": {kind: edge_counts[kind] for kind in sorted(edge_counts)},
            "diagnostic_count": len(diagnostics),
        },
    }


def plan_technology_diagram_edits(
    sources: Sequence[TechnologySource | Mapping[str, object]],
    *,
    position_intents: Sequence[TechnologyPositionIntent | Mapping[str, object]] = (),
    edge_intents: Sequence[TechnologyEdgeIntent | Mapping[str, object]] = (),
) -> dict[str, object]:
    """Purely plan exact source edits for reviewed diagram intents.

    The planner never reads or writes the filesystem. Every intent must carry
    the exact content-derived ``source_revision`` exposed by the projection.
    On any ambiguous, malformed, stale, or overlapping edit, the complete plan
    is blocked and no draft or replacement is returned.

    Args:
        sources: Current exact ``def.txt`` snapshots, decoded from raw UTF-8
            bytes without BOM or newline normalization.
        position_intents: Absolute node position intents.
        edge_intents: Desired dependency/path edge presence intents.

    Returns:
        A stable-hash plan containing exact source replacements and complete
        guarded drafts, or diagnostics with no changes when blocked.
    """

    model = _technology_model(sources)
    diagnostics = list(model.diagnostics)
    positions, position_diagnostics = _normalize_position_intents(position_intents)
    edges, edge_diagnostics = _normalize_edge_intents(edge_intents)
    diagnostics.extend(position_diagnostics)
    diagnostics.extend(edge_diagnostics)

    records_by_id = _unique_records_by_id(model.records)
    replacements: list[_Replacement] = []
    for intent in positions:
        record = records_by_id.get(intent.technology_id)
        if record is None:
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.node_unresolved",
                    message=f"Technology {intent.technology_id!r} does not resolve to exactly one source node.",
                    technology_id=intent.technology_id,
                )
            )
            continue
        if intent.source_revision != record.document.revision:
            diagnostics.append(_stale_revision_diagnostic(record, intent.source_revision))
            continue
        try:
            replacements.extend(_position_replacements(record, intent))
        except _UnsafePatch as error:
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.position_unsafe",
                    message=str(error),
                    source_path=record.document.path,
                    technology_id=record.technology_id,
                )
            )

    edge_groups: dict[tuple[str, str], list[_EdgeChange]] = defaultdict(list)
    existing_edges = {(str(edge["kind"]), str(edge["source"]), str(edge["target"])) for edge in model.edges}
    for intent in edges:
        source_record = records_by_id.get(intent.source_id)
        target_record = records_by_id.get(intent.target_id)
        owner = target_record if intent.kind == "dependency" else source_record
        if owner is None:
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.edge_owner_unresolved",
                    message=(
                        f"{intent.kind.title()} edge {intent.source_id!r} -> {intent.target_id!r} "
                        "requires its source-owning technology to resolve to exactly one reviewed node."
                    ),
                )
            )
            continue
        edge_exists = (intent.kind, intent.source_id, intent.target_id) in existing_edges
        if intent.present and not edge_exists and (source_record is None or target_record is None):
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.edge_node_unresolved",
                    message=(
                        f"Adding {intent.kind} edge {intent.source_id!r} -> {intent.target_id!r} "
                        "requires both endpoints to resolve to exactly one reviewed node."
                    ),
                )
            )
            continue
        if intent.source_revision != owner.document.revision:
            diagnostics.append(_stale_revision_diagnostic(owner, intent.source_revision))
            continue
        edge_groups[(intent.kind, owner.technology_id)].append(intent)

    for (kind, owner_id), changes in sorted(edge_groups.items()):
        owner = records_by_id[owner_id]
        try:
            if kind == "dependency":
                replacements.extend(_dependency_replacements(owner, changes, records_by_id))
            else:
                replacements.extend(_path_replacements(owner, changes, records_by_id))
        except _UnsafePatch as error:
            diagnostics.append(
                _Diagnostic(
                    code=f"technology.plan.{kind}_unsafe",
                    message=str(error),
                    source_path=owner.document.path,
                    technology_id=owner.technology_id,
                )
            )

    diagnostics = list(_sorted_diagnostics(diagnostics))
    blocked = any(row.severity == _ERROR for row in diagnostics)
    drafts: list[dict[str, object]] = []
    replacement_rows: list[dict[str, object]] = []
    if not blocked:
        try:
            replacements = _merge_and_validate_replacements(replacements)
            drafts, replacement_rows = _render_drafts(model.documents, replacements)
        except _UnsafePatch as error:
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.replacements_unsafe",
                    message=str(error),
                )
            )
            diagnostics = list(_sorted_diagnostics(diagnostics))
            blocked = True

    if blocked:
        drafts = []
        replacement_rows = []
    status = "blocked" if blocked else "planned" if drafts else "unchanged"
    intent_rows = {
        "positions": [
            {
                "technology_id": row.technology_id,
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
    }
    plan: dict[str, object] = {
        "schema": TECHNOLOGY_DIAGRAM_PLAN_SCHEMA,
        "projection_schema": TECHNOLOGY_DIAGRAM_PROJECTION_SCHEMA,
        "status": status,
        "write": False,
        "offset_unit": "unicode_codepoint",
        "sources": [
            {
                "path": document.path,
                "source_revision": document.revision,
                "sha256": document.sha256,
            }
            for document in model.documents
        ],
        "intents": intent_rows,
        "source_replacements": replacement_rows,
        "drafts": drafts,
        "diagnostics": [row.to_dict() for row in diagnostics],
        "summary": {
            "position_intent_count": len(positions),
            "edge_intent_count": len(edges),
            "replacement_count": len(replacement_rows),
            "draft_count": len(drafts),
            "diagnostic_count": len(diagnostics),
        },
    }
    plan["plan_hash"] = _stable_hash(plan)
    return plan


def _technology_model(
    sources: Sequence[TechnologySource | Mapping[str, object]],
) -> _TechnologyModel:
    documents, diagnostics = _source_documents(sources)
    records: list[_TechnologyRecord] = []
    edges: list[dict[str, object]] = []
    for document in documents:
        wrappers = document.block.find_all("technologies")
        if not wrappers:
            diagnostics.append(
                _Diagnostic(
                    code="technology.source.missing_wrapper",
                    message="Technology def.txt has no 'technologies' block.",
                    severity=_WARNING,
                    source_path=document.path,
                )
            )
            continue
        for wrapper in wrappers:
            if not isinstance(wrapper.val, PDXBlock):
                diagnostics.append(
                    _Diagnostic(
                        code="technology.source.invalid_wrapper",
                        message="Technology 'technologies' entry must be a PDX block.",
                        source_path=document.path,
                    )
                )
                continue
            for entry in wrapper.val.entries:
                if entry.key is None or not isinstance(entry.val, PDXBlock):
                    continue
                technology_id = _scalar_text(entry.key)
                if not technology_id:
                    continue
                records.append(
                    _TechnologyRecord(
                        technology_id=technology_id,
                        document=document,
                        entry=entry,
                        block=entry.val,
                    )
                )

    duplicate_ids = _duplicate_technology_ids(records)
    for technology_id in sorted(duplicate_ids):
        paths = sorted(record.document.path for record in records if record.technology_id == technology_id)
        diagnostics.append(
            _Diagnostic(
                code="technology.node.duplicate_id",
                message=f"Technology {technology_id!r} is declared more than once: {', '.join(paths)}.",
                technology_id=technology_id,
            )
        )

    known_ids = {record.technology_id for record in records}
    edge_keys: set[tuple[str, str, str]] = set()
    for record in records:
        diagnostics.extend(_technology_node_diagnostics(record))
        record_edges, record_diagnostics = _technology_edges(record)
        diagnostics.extend(record_diagnostics)
        for edge in record_edges:
            key = (str(edge["kind"]), str(edge["source"]), str(edge["target"]))
            if key in edge_keys:
                diagnostics.append(
                    _Diagnostic(
                        code="technology.edge.duplicate",
                        message=f"Technology {key[0]} edge {key[1]!r} -> {key[2]!r} is declared more than once.",
                        severity=_WARNING,
                        source_path=record.document.path,
                        technology_id=record.technology_id,
                    )
                )
                continue
            edge_keys.add(key)
            edges.append(edge)
            if key[1] not in known_ids or key[2] not in known_ids:
                diagnostics.append(
                    _Diagnostic(
                        code="technology.edge.unresolved",
                        message=f"Technology {key[0]} edge {key[1]!r} -> {key[2]!r} has an endpoint outside the reviewed sources.",
                        severity=_WARNING,
                        source_path=record.document.path,
                        technology_id=record.technology_id,
                    )
                )

    edges.sort(key=lambda row: (str(row["kind"]), str(row["source"]), str(row["target"]), str(row["source_path"])))
    return _TechnologyModel(
        documents=tuple(documents),
        records=tuple(records),
        edges=tuple(edges),
        diagnostics=tuple(_sorted_diagnostics(diagnostics)),
    )


def _source_documents(
    sources: Sequence[TechnologySource | Mapping[str, object]],
) -> tuple[list[_SourceDocument], list[_Diagnostic]]:
    diagnostics: list[_Diagnostic] = []
    normalized: list[TechnologySource] = []
    for index, source in enumerate(sources):
        if isinstance(source, TechnologySource):
            row = source
        elif isinstance(source, Mapping):
            path = source.get("path")
            text = source.get("text")
            if not isinstance(path, str) or not isinstance(text, str):
                diagnostics.append(
                    _Diagnostic(
                        code="technology.source.invalid_record",
                        message=f"Source record {index} requires string 'path' and 'text' fields.",
                    )
                )
                continue
            row = TechnologySource(path=path, text=text)
        else:
            diagnostics.append(
                _Diagnostic(
                    code="technology.source.invalid_record",
                    message=f"Source record {index} is not a TechnologySource or mapping.",
                )
            )
            continue
        if not isinstance(row.path, str) or not isinstance(row.text, str):
            diagnostics.append(
                _Diagnostic(
                    code="technology.source.invalid_record",
                    message=f"Source record {index} requires string 'path' and 'text' fields.",
                )
            )
            continue
        if not _is_utf8_text(row.path):
            diagnostics.append(
                _Diagnostic(
                    code="technology.source.invalid_path",
                    message=f"Source record {index} path must be valid UTF-8 text.",
                )
            )
            continue
        if not row.path.strip():
            diagnostics.append(
                _Diagnostic(
                    code="technology.source.invalid_path",
                    message=f"Source record {index} has an empty path.",
                )
            )
            continue
        if row.path.replace("\\", "/").rsplit("/", 1)[-1] != "def.txt":
            diagnostics.append(
                _Diagnostic(
                    code="technology.source.not_def",
                    message=f"Technology source {row.path!r} is not a module def.txt.",
                    source_path=row.path,
                )
            )
            continue
        normalized.append(row)

    normalized.sort(key=lambda row: (row.path, row.text))
    documents: list[_SourceDocument] = []
    seen_paths: set[str] = set()
    for source in normalized:
        if source.path in seen_paths:
            diagnostics.append(
                _Diagnostic(
                    code="technology.source.duplicate_path",
                    message=f"Technology source path {source.path!r} is repeated.",
                    source_path=source.path,
                )
            )
            continue
        seen_paths.add(source.path)
        try:
            digest = _text_sha256(source.text)
            block = parse_pdx(source.text)
            tokens = _lex_tokens(source.text)
        except PDXParseError as error:
            for row in error.diagnostics:
                diagnostics.append(
                    _Diagnostic(
                        code=row.code,
                        message=f"{row.message} (line {row.line}, column {row.column})",
                        severity=row.severity,
                        source_path=source.path,
                    )
                )
            continue
        except UnicodeEncodeError:
            diagnostics.append(
                _Diagnostic(
                    code="technology.source.invalid_unicode",
                    message="Technology source cannot be encoded as UTF-8.",
                    source_path=source.path,
                )
            )
            continue
        except _UnsafePatch as error:
            diagnostics.append(
                _Diagnostic(
                    code="technology.source.lexical_mismatch",
                    message=str(error),
                    source_path=source.path,
                )
            )
            continue
        documents.append(
            _SourceDocument(
                path=source.path,
                text=source.text,
                sha256=digest,
                revision=f"sha256:{digest}",
                block=block,
                tokens=tokens,
            )
        )
    return documents, diagnostics


def _technology_node(record: _TechnologyRecord, *, duplicate: bool) -> dict[str, object]:
    folder, x, y, position_valid = _folder_position(record)
    row: dict[str, object] = {
        "id": record.technology_id,
        "folder": folder,
        "x": x,
        "y": y,
        "source_path": record.document.path,
        "source_revision": record.document.revision,
        "editable": position_valid and not duplicate,
    }
    span = _source_span(record.entry.key)
    if span is not None:
        row["source_span"] = span
    return row


def _technology_node_diagnostics(
    record: _TechnologyRecord,
) -> tuple[_Diagnostic, ...]:
    fields = record.block.find_all("folder")
    common = {
        "severity": _WARNING,
        "source_path": record.document.path,
        "technology_id": record.technology_id,
    }
    if len(fields) != 1 or not isinstance(fields[0].val, PDXBlock):
        return (
            _Diagnostic(
                code="technology.node.folder_ambiguous",
                message=f"Technology {record.technology_id!r} must have exactly one folder block for diagram editing.",
                **common,
            ),
        )
    folder = fields[0].val
    names = folder.find_all("name")
    positions = folder.find_all("position")
    diagnostics: list[_Diagnostic] = []
    if len(names) != 1 or _entry_scalar_text(names[0]) is None:
        diagnostics.append(
            _Diagnostic(
                code="technology.node.folder_name_ambiguous",
                message=f"Technology {record.technology_id!r} folder must have exactly one scalar name.",
                **common,
            )
        )
    if len(positions) != 1 or not isinstance(positions[0].val, PDXBlock):
        diagnostics.append(
            _Diagnostic(
                code="technology.node.position_ambiguous",
                message=f"Technology {record.technology_id!r} folder must have exactly one position block.",
                **common,
            )
        )
        return tuple(diagnostics)
    position = positions[0].val
    x_entries = position.find_all("x")
    y_entries = position.find_all("y")
    if len(x_entries) != 1 or len(y_entries) != 1 or _entry_number(x_entries[0]) is None or _entry_number(y_entries[0]) is None:
        diagnostics.append(
            _Diagnostic(
                code="technology.node.coordinates_ambiguous",
                message=f"Technology {record.technology_id!r} position must have exactly one numeric x and y.",
                **common,
            )
        )
    return tuple(diagnostics)


def _folder_position(record: _TechnologyRecord) -> tuple[str | None, int | float | None, int | float | None, bool]:
    folders = record.block.find_all("folder")
    if len(folders) != 1 or not isinstance(folders[0].val, PDXBlock):
        return None, None, None, False
    folder = folders[0].val
    names = folder.find_all("name")
    positions = folder.find_all("position")
    if len(names) != 1 or len(positions) != 1 or not isinstance(positions[0].val, PDXBlock):
        return None, None, None, False
    name = _entry_scalar_text(names[0])
    position = positions[0].val
    x_entries = position.find_all("x")
    y_entries = position.find_all("y")
    if len(x_entries) != 1 or len(y_entries) != 1:
        return name, None, None, False
    x = _entry_number(x_entries[0])
    y = _entry_number(y_entries[0])
    return name, x, y, name is not None and x is not None and y is not None


def _technology_edges(
    record: _TechnologyRecord,
) -> tuple[list[dict[str, object]], list[_Diagnostic]]:
    edges: list[dict[str, object]] = []
    diagnostics: list[_Diagnostic] = []
    dependency_entries = record.block.find_all("dependencies")
    if len(dependency_entries) > 1:
        diagnostics.append(
            _Diagnostic(
                code="technology.dependency.ambiguous_blocks",
                message=f"Technology {record.technology_id!r} has more than one dependencies block.",
                severity=_WARNING,
                source_path=record.document.path,
                technology_id=record.technology_id,
            )
        )
    for dependencies in dependency_entries:
        if not isinstance(dependencies.val, PDXBlock):
            diagnostics.append(
                _Diagnostic(
                    code="technology.dependency.invalid_block",
                    message=f"Technology {record.technology_id!r} has a non-block dependencies entry.",
                    severity=_WARNING,
                    source_path=record.document.path,
                    technology_id=record.technology_id,
                )
            )
            continue
        for entry in dependencies.val.entries:
            source_id = entry.key_str
            if not source_id or entry.op is None:
                continue
            edges.append(_edge_row("dependency", source_id, record.technology_id, record))

    for path in record.block.find_all("path"):
        if not isinstance(path.val, PDXBlock):
            diagnostics.append(
                _Diagnostic(
                    code="technology.path.invalid_block",
                    message=f"Technology {record.technology_id!r} has a non-block path entry.",
                    severity=_WARNING,
                    source_path=record.document.path,
                    technology_id=record.technology_id,
                )
            )
            continue
        leads = path.val.find_all("leads_to_tech")
        if not leads and not path.val.entries:
            continue
        if len(leads) != 1:
            diagnostics.append(
                _Diagnostic(
                    code="technology.path.invalid_target",
                    message=f"Technology {record.technology_id!r} path must have exactly one scalar leads_to_tech.",
                    severity=_WARNING,
                    source_path=record.document.path,
                    technology_id=record.technology_id,
                )
            )
            continue
        target_id = _entry_scalar_text(leads[0])
        if not target_id:
            diagnostics.append(
                _Diagnostic(
                    code="technology.path.invalid_target",
                    message=f"Technology {record.technology_id!r} path has no scalar leads_to_tech.",
                    severity=_WARNING,
                    source_path=record.document.path,
                    technology_id=record.technology_id,
                )
            )
            continue
        edges.append(_edge_row("path", record.technology_id, target_id, record))
    return edges, diagnostics


def _edge_row(
    kind: str,
    source_id: str,
    target_id: str,
    owner: _TechnologyRecord,
) -> dict[str, object]:
    return {
        "id": f"{kind}:{source_id}->{target_id}",
        "kind": kind,
        "source": source_id,
        "target": target_id,
        "owner_id": owner.technology_id,
        "source_path": owner.document.path,
        "source_revision": owner.document.revision,
    }


def _normalize_position_intents(
    intents: Sequence[TechnologyPositionIntent | Mapping[str, object]],
) -> tuple[tuple[_PositionChange, ...], tuple[_Diagnostic, ...]]:
    normalized: dict[str, _PositionChange] = {}
    diagnostics: list[_Diagnostic] = []
    for index, intent in enumerate(intents):
        if isinstance(intent, TechnologyPositionIntent):
            technology_id = intent.technology_id
            x = intent.x
            y = intent.y
            revision = intent.source_revision
        elif isinstance(intent, Mapping):
            technology_id = intent.get("technology_id")
            x = intent.get("x")
            y = intent.get("y")
            revision = intent.get("source_revision")
        else:
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.invalid_position_intent",
                    message=f"Position intent {index} is not a TechnologyPositionIntent or mapping.",
                )
            )
            continue
        if not isinstance(technology_id, str) or not technology_id.strip() or technology_id != technology_id.strip() or not _is_utf8_text(technology_id):
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.invalid_position_intent",
                    message=f"Position intent {index} requires a non-empty technology_id.",
                )
            )
            continue
        if not _is_number(x) or not _is_number(y):
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.invalid_position_intent",
                    message=f"Position intent for {technology_id!r} requires finite numeric x and y.",
                    technology_id=technology_id,
                )
            )
            continue
        if not _is_source_revision(revision):
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.review_revision_required",
                    message=f"Position intent for {technology_id!r} requires its exact reviewed sha256 source_revision.",
                    technology_id=technology_id,
                )
            )
            continue
        row = _PositionChange(technology_id=technology_id, x=x, y=y, source_revision=revision)
        previous = normalized.get(technology_id)
        if previous is not None and previous != row:
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.conflicting_position_intents",
                    message=f"Technology {technology_id!r} has conflicting reviewed position intents.",
                    technology_id=technology_id,
                )
            )
            continue
        normalized[technology_id] = row
    return tuple(normalized[key] for key in sorted(normalized)), tuple(_sorted_diagnostics(diagnostics))


def _normalize_edge_intents(
    intents: Sequence[TechnologyEdgeIntent | Mapping[str, object]],
) -> tuple[tuple[_EdgeChange, ...], tuple[_Diagnostic, ...]]:
    normalized: dict[tuple[str, str, str], _EdgeChange] = {}
    diagnostics: list[_Diagnostic] = []
    for index, intent in enumerate(intents):
        if isinstance(intent, TechnologyEdgeIntent):
            kind = intent.kind
            source_id = intent.source_id
            target_id = intent.target_id
            present = intent.present
            revision = intent.source_revision
        elif isinstance(intent, Mapping):
            kind = intent.get("kind")
            source_id = intent.get("source_id")
            target_id = intent.get("target_id")
            present = intent.get("present")
            revision = intent.get("source_revision")
        else:
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.invalid_edge_intent",
                    message=f"Edge intent {index} is not a TechnologyEdgeIntent or mapping.",
                )
            )
            continue
        if (
            not isinstance(kind, str)
            or kind not in _EDGE_KINDS
            or not isinstance(source_id, str)
            or not source_id.strip()
            or source_id != source_id.strip()
            or not _is_utf8_text(source_id)
            or not isinstance(target_id, str)
            or not target_id.strip()
            or target_id != target_id.strip()
            or not _is_utf8_text(target_id)
        ):
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.invalid_edge_intent",
                    message=f"Edge intent {index} requires kind dependency/path and non-empty source_id/target_id.",
                )
            )
            continue
        if source_id == target_id:
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.self_edge",
                    message=f"Technology {kind} edge {source_id!r} -> {target_id!r} cannot target itself.",
                    technology_id=source_id,
                )
            )
            continue
        if not isinstance(present, bool):
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.invalid_edge_intent",
                    message=f"Technology {kind} edge {source_id!r} -> {target_id!r} requires boolean present.",
                )
            )
            continue
        if not _is_source_revision(revision):
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.review_revision_required",
                    message=f"Technology {kind} edge {source_id!r} -> {target_id!r} requires its owner's exact reviewed sha256 source_revision.",
                )
            )
            continue
        key = (kind, source_id, target_id)
        row = _EdgeChange(
            kind=kind,
            source_id=source_id,
            target_id=target_id,
            present=present,
            source_revision=revision,
        )
        previous = normalized.get(key)
        if previous is not None and previous != row:
            diagnostics.append(
                _Diagnostic(
                    code="technology.plan.conflicting_edge_intents",
                    message=f"Technology {kind} edge {source_id!r} -> {target_id!r} has conflicting reviewed intents.",
                )
            )
            continue
        normalized[key] = row
    return tuple(normalized[key] for key in sorted(normalized)), tuple(_sorted_diagnostics(diagnostics))


def _position_replacements(
    record: _TechnologyRecord,
    intent: _PositionChange,
) -> list[_Replacement]:
    _folder, _x, _y, position_valid = _folder_position(record)
    if not position_valid:
        raise _UnsafePatch(f"Technology {record.technology_id!r} requires one scalar folder name and one numeric position before it can be moved.")
    folders = record.block.find_all("folder")
    if len(folders) != 1 or not isinstance(folders[0].val, PDXBlock):
        raise _UnsafePatch(f"Technology {record.technology_id!r} must have exactly one folder block before its position can be edited.")
    positions = folders[0].val.find_all("position")
    if len(positions) != 1 or not isinstance(positions[0].val, PDXBlock):
        raise _UnsafePatch(f"Technology {record.technology_id!r} must have exactly one position block before its position can be edited.")
    x_entries = positions[0].val.find_all("x")
    y_entries = positions[0].val.find_all("y")
    if len(x_entries) != 1 or len(y_entries) != 1:
        raise _UnsafePatch(f"Technology {record.technology_id!r} position must contain exactly one x and one y scalar.")
    replacements: list[_Replacement] = []
    for field, entry, value in (("x", x_entries[0], intent.x), ("y", y_entries[0], intent.y)):
        current = _entry_number(entry)
        if entry.op != "=" or not isinstance(entry.val, PDXScalar) or current is None:
            raise _UnsafePatch(f"Technology {record.technology_id!r} position {field} is not one safely replaceable numeric scalar.")
        if current == value:
            continue
        token = _scalar_token(record.document, entry.val)
        replacement = _format_number(value)
        expected = record.document.text[token.start : token.end]
        replacements.append(
            _Replacement(
                path=record.document.path,
                start=token.start,
                end=token.end,
                expected=expected,
                replacement=replacement,
                operations=(f"position:{record.technology_id}:{field}",),
                order_key=f"position:{record.technology_id}:{field}",
            )
        )
    return replacements


def _dependency_replacements(
    owner: _TechnologyRecord,
    changes: Sequence[_EdgeChange],
    records_by_id: Mapping[str, _TechnologyRecord],
) -> list[_Replacement]:
    dependency_fields = owner.block.find_all("dependencies")
    if len(dependency_fields) > 1:
        raise _UnsafePatch(f"Technology {owner.technology_id!r} has multiple dependencies blocks.")
    if dependency_fields and not isinstance(dependency_fields[0].val, PDXBlock):
        raise _UnsafePatch(f"Technology {owner.technology_id!r} dependencies entry is not a block.")
    dependency_field = dependency_fields[0] if dependency_fields else None
    dependency_block = dependency_field.val if dependency_field is not None else None
    entries_by_id: dict[str, list[PDXEntry]] = defaultdict(list)
    if isinstance(dependency_block, PDXBlock):
        for entry in dependency_block.entries:
            if entry.key_str:
                entries_by_id[entry.key_str].append(entry)

    additions: list[str] = []
    replacements: list[_Replacement] = []
    for change in sorted(changes, key=lambda row: row.source_id):
        matches = entries_by_id.get(change.source_id, [])
        if len(matches) > 1:
            raise _UnsafePatch(f"Technology {owner.technology_id!r} dependency on {change.source_id!r} is declared more than once.")
        if change.present:
            if matches:
                if matches[0].op != "=" or not isinstance(matches[0].val, PDXScalar):
                    raise _UnsafePatch(f"Technology {owner.technology_id!r} dependency on {change.source_id!r} is not a scalar assignment.")
                continue
            additions.append(change.source_id)
            continue
        if not matches:
            continue
        entry = matches[0]
        if entry.op != "=" or not isinstance(entry.val, PDXScalar):
            raise _UnsafePatch(f"Technology {owner.technology_id!r} dependency on {change.source_id!r} is not one removable scalar assignment.")
        replacements.append(
            _whole_entry_line_replacement(
                owner.document,
                entry,
                operation=f"dependency:{change.source_id}->{owner.technology_id}:remove",
            )
        )

    if not additions:
        return replacements
    if dependency_field is not None and isinstance(dependency_block, PDXBlock):
        child_indent, insertion = _block_child_insertion(owner.document, dependency_field, dependency_block)
        newline = _newline(owner.document.text, insertion)
        replacement = "".join(f"{child_indent}{_reference_literal(records_by_id[source_id])} = 1{newline}" for source_id in sorted(additions))
        replacements.append(
            _Replacement(
                path=owner.document.path,
                start=insertion,
                end=insertion,
                expected="",
                replacement=replacement,
                operations=tuple(f"dependency:{source_id}->{owner.technology_id}:add" for source_id in sorted(additions)),
                order_key=f"20:dependency:{owner.technology_id}",
            )
        )
        return replacements

    direct_indent, insertion = _block_child_insertion(owner.document, owner.entry, owner.block)
    unit = _indent_unit(owner.document, owner.block, direct_indent)
    newline = _newline(owner.document.text, insertion)
    nested_indent = direct_indent + unit
    replacement = f"{direct_indent}dependencies = {{{newline}"
    replacement += "".join(f"{nested_indent}{_reference_literal(records_by_id[source_id])} = 1{newline}" for source_id in sorted(additions))
    replacement += f"{direct_indent}}}{newline}"
    replacements.append(
        _Replacement(
            path=owner.document.path,
            start=insertion,
            end=insertion,
            expected="",
            replacement=replacement,
            operations=tuple(f"dependency:{source_id}->{owner.technology_id}:add" for source_id in sorted(additions)),
            order_key=f"20:dependency:{owner.technology_id}",
        )
    )
    return replacements


def _path_replacements(
    owner: _TechnologyRecord,
    changes: Sequence[_EdgeChange],
    records_by_id: Mapping[str, _TechnologyRecord],
) -> list[_Replacement]:
    paths_by_target: dict[str, list[PDXEntry]] = defaultdict(list)
    empty_paths: list[PDXEntry] = []
    for path in owner.block.find_all("path"):
        if not isinstance(path.val, PDXBlock):
            raise _UnsafePatch(f"Technology {owner.technology_id!r} has a non-block path entry.")
        leads = path.val.find_all("leads_to_tech")
        if not leads and not path.val.entries:
            empty_paths.append(path)
            continue
        if len(leads) != 1:
            raise _UnsafePatch(f"Technology {owner.technology_id!r} has a path without exactly one leads_to_tech scalar.")
        target_id = _entry_scalar_text(leads[0])
        if target_id is None:
            raise _UnsafePatch(f"Technology {owner.technology_id!r} has a path with a non-scalar leads_to_tech.")
        paths_by_target[target_id].append(path)

    additions: list[str] = []
    replacements: list[_Replacement] = []
    for change in sorted(changes, key=lambda row: row.target_id):
        matches = paths_by_target.get(change.target_id, [])
        if len(matches) > 1:
            raise _UnsafePatch(f"Technology {owner.technology_id!r} path to {change.target_id!r} is declared more than once.")
        if change.present:
            if not matches:
                additions.append(change.target_id)
            continue
        if not matches:
            continue
        replacements.append(
            _whole_entry_line_replacement(
                owner.document,
                matches[0],
                operation=f"path:{owner.technology_id}->{change.target_id}:remove",
            )
        )

    if not additions:
        return replacements
    if len(empty_paths) > 1:
        raise _UnsafePatch(f"Technology {owner.technology_id!r} has multiple empty path placeholders.")
    if empty_paths:
        placeholder = empty_paths[0]
        placeholder_block = placeholder.val
        if not isinstance(placeholder_block, PDXBlock):
            raise _UnsafePatch(f"Technology {owner.technology_id!r} empty path placeholder is not a block.")
        target_id = additions.pop(0)
        child_indent, insertion = _block_child_insertion(owner.document, placeholder, placeholder_block)
        newline = _newline(owner.document.text, insertion)
        replacements.append(
            _Replacement(
                path=owner.document.path,
                start=insertion,
                end=insertion,
                expected="",
                replacement=(
                    f"{child_indent}leads_to_tech = {_reference_literal(records_by_id[target_id])}{newline}" f"{child_indent}research_cost_coeff = 1{newline}"
                ),
                operations=(f"path:{owner.technology_id}->{target_id}:add",),
                order_key=f"30:path:{owner.technology_id}:{target_id}",
            )
        )
    if not additions:
        return replacements
    direct_indent, insertion = _block_child_insertion(owner.document, owner.entry, owner.block)
    unit = _indent_unit(owner.document, owner.block, direct_indent)
    nested_indent = direct_indent + unit
    newline = _newline(owner.document.text, insertion)
    parts: list[str] = []
    for target_id in sorted(additions):
        parts.extend(
            (
                f"{direct_indent}path = {{{newline}",
                f"{nested_indent}leads_to_tech = {_reference_literal(records_by_id[target_id])}{newline}",
                f"{nested_indent}research_cost_coeff = 1{newline}",
                f"{direct_indent}}}{newline}",
            )
        )
    replacements.append(
        _Replacement(
            path=owner.document.path,
            start=insertion,
            end=insertion,
            expected="",
            replacement="".join(parts),
            operations=tuple(f"path:{owner.technology_id}->{target_id}:add" for target_id in sorted(additions)),
            order_key=f"30:path:{owner.technology_id}",
        )
    )
    return replacements


def _duplicate_technology_ids(
    records: Sequence[_TechnologyRecord],
) -> set[str]:
    counts = Counter(record.technology_id for record in records)
    return {technology_id for technology_id, count in counts.items() if count > 1}


def _unique_records_by_id(
    records: Sequence[_TechnologyRecord],
) -> dict[str, _TechnologyRecord]:
    duplicates = _duplicate_technology_ids(records)
    return {record.technology_id: record for record in records if record.technology_id not in duplicates}


def _stale_revision_diagnostic(
    record: _TechnologyRecord,
    provided: str,
) -> _Diagnostic:
    return _Diagnostic(
        code="technology.plan.source_revision_mismatch",
        message=(f"Technology {record.technology_id!r} changed after review; expected " f"{record.document.revision!r}, received {provided!r}."),
        source_path=record.document.path,
        technology_id=record.technology_id,
    )


def _reference_literal(record: _TechnologyRecord) -> str:
    token = _scalar_token(record.document, record.entry.key)
    return record.document.text[token.start : token.end]


def _sorted_diagnostics(
    diagnostics: Sequence[_Diagnostic],
) -> tuple[_Diagnostic, ...]:
    return tuple(
        sorted(
            diagnostics,
            key=lambda row: (
                0 if row.severity == _ERROR else 1,
                row.source_path or "",
                row.technology_id or "",
                row.code,
                row.message,
            ),
        )
    )
