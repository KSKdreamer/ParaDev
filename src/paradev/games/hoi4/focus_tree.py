"""Source-backed Hearts of Iron IV focus-tree diagram contracts.

This module projects and edits reviewed ``focus_tree`` module ``def.txt``
sources and plans creation against canonical sibling ``main.loc`` sources. It
does not discover modules, inspect derived metadata, or write files.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from paradev._module_diagram_contract import (
    MAX_FOCUS_TREE_NODE_CREATION_OCCUPIED_PATHS,
    MAX_MODULE_DIAGRAM_EDGE_INTENTS,
    MAX_MODULE_DIAGRAM_POSITION_INTENTS,
)
from paradev.localization import canonical_language
from paradev.pdx import PDXBlock, PDXEntry, PDXParseError, PDXScalar, parse_pdx

from ._diagram_source import (
    DiagramSourceDocument,
    DiagramSourceReplacement,
    UnsafeSourcePatch,
    block_child_insertion,
    entry_number,
    entry_scalar_text,
    format_number,
    indent_unit,
    is_finite_number,
    is_source_revision,
    is_utf8_text,
    lex_pdx_tokens,
    merge_source_replacements,
    render_source_drafts,
    scalar_token,
    source_newline,
    source_span,
    stable_payload_hash,
    text_sha256,
    whole_entry_line_replacement,
)

FOCUS_TREE_DIAGRAM_PROJECTION_SCHEMA = "paradev.hoi4.focus-tree-diagram-projection.v1"
FOCUS_TREE_DIAGRAM_PLAN_SCHEMA = "paradev.hoi4.focus-tree-diagram-plan.v1"
FOCUS_TREE_NODE_CREATION_PLAN_SCHEMA = "paradev.hoi4.focus-tree-node-creation-plan.v1"

__all__ = [
    "FOCUS_TREE_DIAGRAM_PLAN_SCHEMA",
    "FOCUS_TREE_DIAGRAM_PROJECTION_SCHEMA",
    "FOCUS_TREE_NODE_CREATION_PLAN_SCHEMA",
    "FocusCreationIntent",
    "FocusEdgeIntent",
    "FocusPositionIntent",
    "FocusTreeLocalizationSource",
    "FocusTreeSource",
    "focus_tree_diagram_projection",
    "plan_focus_tree_diagram_edits",
    "plan_focus_tree_node_creation",
]

_EDGE_KINDS = frozenset({"prerequisite", "mutually_exclusive"})
_ERROR = "error"
_FOCUS_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*\Z")
_LOC_HEADER = re.compile(r"\[([^\].\s]+)\.([^\]\r\n]+)\]\Z")
_MAX_FOCUS_COORDINATE = 100_000
_MAX_FOCUS_DESCRIPTION_BYTES = 16 * 1024
_MAX_FOCUS_ID_BYTES = 128
_MAX_FOCUS_TITLE_BYTES = 512
_MAX_FOCUS_EDGES = 32768
_MAX_FOCUS_NODES = 8192
_MAX_FOCUS_SOURCES = 256
_MAX_SOURCE_BYTES = 4 * 1024 * 1024
_MAX_TOTAL_SOURCE_BYTES = 32 * 1024 * 1024
_WARNING = "warning"


@dataclass(frozen=True, slots=True)
class FocusTreeSource:
    """One reviewed focus-tree module ``def.txt`` source.

    Args:
        path: Stable reader-facing path ending in ``def.txt``.
        text: Complete UTF-8-decoded PDX source, preserving its BOM and newline
            bytes without universal-newline normalization.
    """

    path: str
    text: str


@dataclass(frozen=True, slots=True)
class FocusTreeLocalizationSource:
    """One reviewed focus-tree module localization source.

    Args:
        path: Stable project-relative path ending in ``.loc``.
        text: Complete UTF-8-decoded localization source, preserving its BOM
            and newline bytes without universal-newline normalization.
    """

    path: str
    text: str


@dataclass(frozen=True, slots=True)
class FocusCreationIntent:
    """Reviewed request to add one focus to one canonical tree module.

    Args:
        tree_id: Existing selected focus-tree identifier.
        focus_id: New path-safe, unquoted HoI4 focus identifier.
        x: Integer horizontal coordinate, relative when a parent is supplied.
        y: Integer vertical coordinate, relative when a parent is supplied.
        title: Non-empty one-line English focus title.
        description: Non-empty English focus description.
        source_revision: Exact ``def.txt`` revision exposed during review.
        localization_source_revision: Exact canonical ``main.loc`` revision
            exposed during review.
        relative_position_id: Optional existing focus in the selected tree used
            as HoI4's relative-position parent.
        prerequisite_id: Optional existing focus in the selected tree required
            before the new focus.
        icon_key: Optional path-safe existing HoI4 sprite key. Defaults to the
            base-game fallback ``GFX_goal_unknown``. The separately advertised
            PNG target is editor preview media, not a compiled sprite.
    """

    tree_id: str
    focus_id: str
    x: int
    y: int
    title: str
    description: str
    source_revision: str
    localization_source_revision: str
    relative_position_id: str | None = None
    prerequisite_id: str | None = None
    icon_key: str | None = None


@dataclass(frozen=True, slots=True)
class FocusPositionIntent:
    """Reviewed absolute position for one focus node.

    Args:
        focus_id: Game-facing focus identifier.
        x: Desired finite horizontal coordinate.
        y: Desired finite vertical coordinate.
        source_revision: Exact revision exposed by the reviewed projection.
    """

    focus_id: str
    x: int | float
    y: int | float
    source_revision: str


@dataclass(frozen=True, slots=True)
class FocusEdgeIntent:
    """Reviewed desired presence of one focus relation.

    A prerequisite points from the prerequisite ``source_id`` to its dependent
    ``target_id``. A mutually-exclusive edge is undirected; its endpoint ids
    are normalized deterministically and the planner keeps the two reciprocal
    HoI4 declarations consistent.

    Args:
        kind: ``prerequisite`` or ``mutually_exclusive``.
        source_id: Prerequisite or first mutually-exclusive focus identifier.
        target_id: Dependent or second mutually-exclusive focus identifier.
        present: Whether the relation should exist after applying the draft.
        source_revision: Exact revision exposed by the reviewed edge or, for a
            new same-file relation, either endpoint node.
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
    tree_id: str | None = None
    focus_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        row: dict[str, object] = {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
        }
        if self.source_path is not None:
            row["source_path"] = self.source_path
        if self.tree_id is not None:
            row["tree_id"] = self.tree_id
        if self.focus_id is not None:
            row["focus_id"] = self.focus_id
        return row


@dataclass(frozen=True, slots=True)
class _FocusTreeRecord:
    tree_id: str
    document: DiagramSourceDocument
    entry: PDXEntry
    block: PDXBlock
    id_entry: PDXEntry


@dataclass(frozen=True, slots=True)
class _FocusRecord:
    focus_id: str
    tree_id: str
    document: DiagramSourceDocument
    entry: PDXEntry
    block: PDXBlock
    id_entry: PDXEntry


@dataclass(frozen=True, slots=True)
class _RelationDeclaration:
    kind: str
    source_id: str
    target_id: str
    owner: _FocusRecord
    relation_entry: PDXEntry
    relation_block: PDXBlock
    reference_entry: PDXEntry
    group_index: int


@dataclass(frozen=True, slots=True)
class _FocusTreeModel:
    documents: tuple[DiagramSourceDocument, ...]
    trees: tuple[_FocusTreeRecord, ...]
    records: tuple[_FocusRecord, ...]
    declarations: tuple[_RelationDeclaration, ...]
    edges: tuple[dict[str, object], ...]
    diagnostics: tuple[_Diagnostic, ...]


@dataclass(frozen=True, slots=True)
class _PositionChange:
    focus_id: str
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


@dataclass(frozen=True, slots=True)
class _OwnedRelationChange:
    kind: str
    owner_id: str
    referenced_id: str
    present: bool


@dataclass(frozen=True, slots=True)
class _LocalizationDocument:
    path: str
    text: str
    sha256: str
    revision: str


@dataclass(frozen=True, slots=True)
class _FocusCreation:
    tree_id: str
    focus_id: str
    x: int
    y: int
    title: str
    description: str
    source_revision: str
    localization_source_revision: str
    relative_position_id: str | None
    prerequisite_id: str | None
    icon_key: str


def focus_tree_diagram_projection(
    sources: Sequence[FocusTreeSource | Mapping[str, object]],
) -> dict[str, object]:
    """Return a deterministic focus graph projected from module ``def.txt``.

    Args:
        sources: Exact reviewed source snapshots. Mapping records use ``path``
            and ``text`` fields; callers must decode raw UTF-8 bytes without
            normalizing newlines.

    Returns:
        A bounded JSON-safe graph with focus-tree containers, focus nodes,
        prerequisite and mutually-exclusive edges, content-derived source
        revisions, and fail-closed diagnostics.
    """

    model = _focus_tree_model(sources)
    duplicate_tree_ids = _duplicate_tree_ids(model.trees)
    duplicate_focus_ids = _duplicate_focus_ids(model.records)
    nodes = [
        _focus_node(
            record,
            duplicate=record.focus_id in duplicate_focus_ids,
            tree_duplicate=record.tree_id in duplicate_tree_ids,
        )
        for record in sorted(
            model.records,
            key=lambda row: (row.tree_id, row.focus_id, row.document.path),
        )
    ]
    diagnostics = _sorted_diagnostics(model.diagnostics)
    edge_counts = Counter(str(edge["kind"]) for edge in model.edges)
    node_counts = Counter(record.tree_id for record in model.records)
    edge_tree_counts = Counter(str(edge["tree_id"]) for edge in model.edges)
    trees = [
        {
            "id": tree.tree_id,
            "source_path": tree.document.path,
            "source_revision": tree.document.revision,
            "node_count": node_counts[tree.tree_id],
            "edge_count": edge_tree_counts[tree.tree_id],
            "editable": tree.tree_id not in duplicate_tree_ids,
            **({"source_span": span} if (span := source_span(tree.id_entry.val)) is not None else {}),
        }
        for tree in sorted(
            model.trees,
            key=lambda row: (row.tree_id, row.document.path),
        )
    ]
    return {
        "schema": FOCUS_TREE_DIAGRAM_PROJECTION_SCHEMA,
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
        "trees": trees,
        "nodes": nodes,
        "edges": list(model.edges),
        "diagnostics": [row.to_dict() for row in diagnostics],
        "summary": {
            "source_count": len(model.documents),
            "tree_count": len(trees),
            "node_count": len(nodes),
            "edge_count": len(model.edges),
            "edge_counts": {kind: edge_counts[kind] for kind in sorted(edge_counts)},
            "relation_declaration_count": len(model.declarations),
            "diagnostic_count": len(diagnostics),
        },
    }


def plan_focus_tree_diagram_edits(
    sources: Sequence[FocusTreeSource | Mapping[str, object]],
    *,
    position_intents: Sequence[FocusPositionIntent | Mapping[str, object]] = (),
    edge_intents: Sequence[FocusEdgeIntent | Mapping[str, object]] = (),
) -> dict[str, object]:
    """Purely plan exact focus-tree source edits for reviewed intents.

    The planner never reads or writes the filesystem. Every intent carries a
    content-derived revision from :func:`focus_tree_diagram_projection`. Any
    malformed, ambiguous, stale, or overlapping edit blocks the complete plan
    and returns no drafts.

    Args:
        sources: Current exact ``def.txt`` snapshots, decoded from raw UTF-8
            bytes without BOM or newline normalization.
        position_intents: Absolute focus position intents.
        edge_intents: Desired prerequisite or mutually-exclusive relations.

    Returns:
        A stable-hash plan containing exact source replacements and guarded
        complete drafts, or diagnostics with no changes when blocked.
    """

    model = _focus_tree_model(sources)
    diagnostics = list(model.diagnostics)
    positions, position_diagnostics = _normalize_position_intents(position_intents)
    edges, edge_diagnostics = _normalize_edge_intents(edge_intents)
    diagnostics.extend(position_diagnostics)
    diagnostics.extend(edge_diagnostics)

    records_by_id = _unique_records_by_id(model.records)
    replacements: list[DiagramSourceReplacement] = []
    for intent in positions:
        record = records_by_id.get(intent.focus_id)
        if record is None:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.node_unresolved",
                    message=(f"Focus {intent.focus_id!r} does not resolve to exactly " "one reviewed source node."),
                    focus_id=intent.focus_id,
                )
            )
            continue
        if intent.source_revision != record.document.revision:
            diagnostics.append(
                _stale_revision_diagnostic(
                    focus_id=record.focus_id,
                    source_path=record.document.path,
                    expected=record.document.revision,
                    provided=intent.source_revision,
                )
            )
            continue
        try:
            replacements.extend(_position_replacements(record, intent))
        except UnsafeSourcePatch as error:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.position_unsafe",
                    message=str(error),
                    source_path=record.document.path,
                    tree_id=record.tree_id,
                    focus_id=record.focus_id,
                )
            )

    existing_edges = {
        (
            str(edge["kind"]),
            str(edge["source"]),
            str(edge["target"]),
        ): edge
        for edge in model.edges
    }
    declarations_by_edge = _declarations_by_edge(model.declarations)
    owned_changes: dict[tuple[str, str], dict[str, _OwnedRelationChange]] = defaultdict(dict)
    for intent in edges:
        source_record = records_by_id.get(intent.source_id)
        target_record = records_by_id.get(intent.target_id)
        edge_key = (intent.kind, intent.source_id, intent.target_id)
        edge_exists = edge_key in existing_edges
        declarations = declarations_by_edge.get(edge_key, ())

        if intent.kind == "prerequisite":
            owner = target_record
            if owner is None:
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.plan.edge_owner_unresolved",
                        message=(
                            f"Prerequisite edge {intent.source_id!r} -> "
                            f"{intent.target_id!r} requires its dependent focus "
                            "to resolve to exactly one reviewed node."
                        ),
                    )
                )
                continue
            if intent.present and not edge_exists and source_record is None:
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.plan.edge_node_unresolved",
                        message=(
                            f"Adding prerequisite edge {intent.source_id!r} -> "
                            f"{intent.target_id!r} requires both endpoints to "
                            "resolve to exactly one reviewed node."
                        ),
                    )
                )
                continue
            if intent.source_revision != owner.document.revision:
                diagnostics.append(
                    _stale_revision_diagnostic(
                        focus_id=owner.focus_id,
                        source_path=owner.document.path,
                        expected=owner.document.revision,
                        provided=intent.source_revision,
                    )
                )
                continue
            _register_owned_change(
                owned_changes,
                _OwnedRelationChange(
                    kind=intent.kind,
                    owner_id=owner.focus_id,
                    referenced_id=intent.source_id,
                    present=intent.present,
                ),
            )
            continue

        owner_documents = {declaration.owner.document.path: declaration.owner.document for declaration in declarations}
        if intent.present:
            if source_record is None or target_record is None:
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.plan.edge_node_unresolved",
                        message=(
                            "Adding mutually-exclusive edge "
                            f"{intent.source_id!r} -- {intent.target_id!r} "
                            "requires both endpoints to resolve to exactly one "
                            "reviewed node."
                        ),
                    )
                )
                continue
            endpoint_documents = {
                source_record.document.path: source_record.document,
                target_record.document.path: target_record.document,
            }
            if len(endpoint_documents) != 1:
                diagnostics.append(
                    _Diagnostic(
                        code=("focus_tree.plan." "mutually_exclusive_cross_source_unsafe"),
                        message=(
                            "Adding a mutually-exclusive relation across two "
                            "focus-tree source files requires a multi-source "
                            "review contract and is not safely editable."
                        ),
                    )
                )
                continue
            owner_documents = endpoint_documents
        elif not owner_documents:
            owner_documents = {record.document.path: record.document for record in (source_record, target_record) if record is not None}
        expected_revision = _documents_revision(tuple(owner_documents.values()))
        if expected_revision is None or intent.source_revision != expected_revision:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.source_revision_mismatch",
                    message=(
                        "Mutually-exclusive relation "
                        f"{intent.source_id!r} -- {intent.target_id!r} changed "
                        "after review; expected "
                        f"{expected_revision!r}, received "
                        f"{intent.source_revision!r}."
                    ),
                )
            )
            continue
        if not intent.present and not declarations:
            continue
        for owner, referenced_id in (
            (source_record, intent.target_id),
            (target_record, intent.source_id),
        ):
            if owner is None:
                continue
            _register_owned_change(
                owned_changes,
                _OwnedRelationChange(
                    kind=intent.kind,
                    owner_id=owner.focus_id,
                    referenced_id=referenced_id,
                    present=intent.present,
                ),
            )

    for (kind, owner_id), changes_by_reference in sorted(owned_changes.items()):
        owner = records_by_id[owner_id]
        try:
            replacements.extend(
                _relation_replacements(
                    owner,
                    kind=kind,
                    changes=tuple(changes_by_reference.values()),
                    records_by_id=records_by_id,
                )
            )
        except UnsafeSourcePatch as error:
            diagnostics.append(
                _Diagnostic(
                    code=f"focus_tree.plan.{kind}_unsafe",
                    message=str(error),
                    source_path=owner.document.path,
                    tree_id=owner.tree_id,
                    focus_id=owner.focus_id,
                )
            )

    diagnostics = list(_sorted_diagnostics(diagnostics))
    blocked = any(row.severity == _ERROR for row in diagnostics)
    drafts: list[dict[str, object]] = []
    replacement_rows: list[dict[str, object]] = []
    if not blocked:
        try:
            replacements = merge_source_replacements(replacements)
            drafts, replacement_rows = render_source_drafts(
                model.documents,
                replacements,
            )
        except UnsafeSourcePatch as error:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.replacements_unsafe",
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
                "focus_id": row.focus_id,
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
        "schema": FOCUS_TREE_DIAGRAM_PLAN_SCHEMA,
        "projection_schema": FOCUS_TREE_DIAGRAM_PROJECTION_SCHEMA,
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
    plan["plan_hash"] = stable_payload_hash(plan)
    return plan


def plan_focus_tree_node_creation(
    sources: Sequence[FocusTreeSource | Mapping[str, object]],
    *,
    localization_sources: Sequence[FocusTreeLocalizationSource | Mapping[str, object]],
    intent: FocusCreationIntent | Mapping[str, object],
    occupied_paths: Sequence[str],
) -> dict[str, object]:
    """Plan creation of one focus in one reviewed canonical tree module.

    This pure planner never reads or writes the filesystem. It binds every
    reviewed focus ``def.txt`` and ``.loc`` snapshot into the plan hash so a
    second dry plan can detect concurrent identifier or localization changes.
    A successful plan contains exact guarded drafts for the selected
    ``def.txt`` and sibling ``main.loc`` plus an absent-file precondition for
    ``icons/<focus_id>.png``. It never fabricates compiled DDS or GFX assets.

    Args:
        sources: Exact reviewed canonical focus-tree ``def.txt`` snapshots.
        localization_sources: Exact reviewed focus-tree ``.loc`` snapshots.
            The selected module must contain exactly one sibling ``main.loc``.
        intent: One reviewed focus-creation request with exact source
            revisions.
        occupied_paths: Current project-relative file inventory used to prove
            that the preview PNG target is absent. Paths are compared using
            Unicode NFC and case folding for cross-platform safety.

    Returns:
        A deterministic JSON-safe plan with exact replacements, complete
        two-file drafts, an absent image target, diagnostics, and a reviewed
        ``plan_hash``. Blocking input returns no drafts or file targets.
    """

    model = _focus_tree_model(sources)
    documents, localization_diagnostics = _localization_documents(localization_sources)
    creation, intent_diagnostics = _normalize_creation_intent(intent)
    occupied, occupied_diagnostics = _normalize_occupied_paths(occupied_paths)
    diagnostics = [
        *model.diagnostics,
        *localization_diagnostics,
        *intent_diagnostics,
        *occupied_diagnostics,
    ]

    tree: _FocusTreeRecord | None = None
    localization: _LocalizationDocument | None = None
    image_path: str | None = None
    if creation is not None:
        matching_trees = [row for row in model.trees if row.tree_id == creation.tree_id]
        if len(matching_trees) != 1:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.tree_unresolved",
                    message=(f"Selected focus tree {creation.tree_id!r} must resolve " "to exactly one reviewed canonical source."),
                    tree_id=creation.tree_id,
                )
            )
        else:
            candidate = matching_trees[0]
            source_trees = [row for row in model.trees if row.document.path == candidate.document.path]
            if len(source_trees) != 1:
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.create.source_ambiguous",
                        message=(
                            f"Selected source {candidate.document.path!r} owns " "more than one focus_tree block and is not a " "single-tree authoring target."
                        ),
                        source_path=candidate.document.path,
                        tree_id=creation.tree_id,
                    )
                )
            elif creation.source_revision != candidate.document.revision:
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.create.source_revision_mismatch",
                        message=(
                            f"Focus tree {creation.tree_id!r} changed after "
                            f"review; expected {candidate.document.revision!r}, "
                            f"received {creation.source_revision!r}."
                        ),
                        source_path=candidate.document.path,
                        tree_id=creation.tree_id,
                    )
                )
            else:
                tree = candidate

        matching_focuses = [row for row in model.records if row.focus_id == creation.focus_id]
        if matching_focuses:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.focus_id_exists",
                    message=f"Focus id {creation.focus_id!r} already exists in reviewed sources.",
                    source_path=matching_focuses[0].document.path,
                    tree_id=matching_focuses[0].tree_id,
                    focus_id=creation.focus_id,
                )
            )
        else:
            portable_focuses = sorted(
                (row for row in model.records if _portable_path_key(row.focus_id) == _portable_path_key(creation.focus_id)),
                key=lambda row: (
                    row.document.path,
                    row.tree_id,
                    row.focus_id,
                ),
            )
            if portable_focuses:
                collision = portable_focuses[0]
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.create.focus_id_portable_collision",
                        message=(f"Focus id {creation.focus_id!r} collides with " f"existing id {collision.focus_id!r} across " "supported filesystems."),
                        source_path=collision.document.path,
                        tree_id=collision.tree_id,
                        focus_id=creation.focus_id,
                    )
                )

        records_by_id = _unique_records_by_id(model.records)
        for role, reference_id in (
            ("relative-position parent", creation.relative_position_id),
            ("prerequisite", creation.prerequisite_id),
        ):
            if reference_id is None:
                continue
            reference = records_by_id.get(reference_id)
            if reference is None or reference.tree_id != creation.tree_id:
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.create.reference_unresolved",
                        message=(f"Focus {role} {reference_id!r} must resolve to " f"exactly one node in selected tree " f"{creation.tree_id!r}."),
                        tree_id=creation.tree_id,
                        focus_id=creation.focus_id,
                    )
                )

        if tree is not None:
            source_path = _safe_project_path(tree.document.path, basename="def.txt")
            if source_path is None:
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.create.source_path_unsafe",
                        message=(f"Selected focus-tree path {tree.document.path!r} " "is not a safe project-relative def.txt path."),
                        source_path=tree.document.path,
                        tree_id=creation.tree_id,
                    )
                )
            else:
                module_root = source_path.rsplit("/", 1)[0]
                localization_path = f"{module_root}/main.loc"
                image_path = f"{module_root}/icons/{creation.focus_id}.png"
                matching_localizations = [row for row in documents if row.path == localization_path]
                if len(matching_localizations) != 1:
                    diagnostics.append(
                        _Diagnostic(
                            code="focus_tree.create.localization_source_unresolved",
                            message=(f"Selected tree module requires exactly one " f"reviewed canonical {localization_path!r}."),
                            source_path=localization_path,
                            tree_id=creation.tree_id,
                            focus_id=creation.focus_id,
                        )
                    )
                else:
                    candidate = matching_localizations[0]
                    if creation.localization_source_revision != candidate.revision:
                        diagnostics.append(
                            _Diagnostic(
                                code="focus_tree.create.localization_revision_mismatch",
                                message=(
                                    f"Canonical localization changed after "
                                    f"review; expected {candidate.revision!r}, "
                                    "received "
                                    f"{creation.localization_source_revision!r}."
                                ),
                                source_path=candidate.path,
                                tree_id=creation.tree_id,
                                focus_id=creation.focus_id,
                            )
                        )
                    elif not _is_ini_localization(candidate.text):
                        diagnostics.append(
                            _Diagnostic(
                                code="focus_tree.create.localization_format_unsupported",
                                message=(
                                    f"Canonical localization {candidate.path!r} "
                                    "must use ParaDev's bracketed .loc format "
                                    "before focus creation can append safely."
                                ),
                                source_path=candidate.path,
                                tree_id=creation.tree_id,
                                focus_id=creation.focus_id,
                            )
                        )
                    else:
                        localization = candidate

                occupied_match = occupied.get(_portable_path_key(image_path))
                if occupied_match is not None:
                    diagnostics.append(
                        _Diagnostic(
                            code="focus_tree.create.image_target_exists",
                            message=(f"Focus preview target {image_path!r} collides " f"with existing project file " f"{occupied_match!r}."),
                            source_path=occupied_match,
                            tree_id=creation.tree_id,
                            focus_id=creation.focus_id,
                        )
                    )

        localization_keys, key_diagnostics = _localization_keys(documents)
        diagnostics.extend(key_diagnostics)
        for key in (creation.focus_id, f"{creation.focus_id}_desc"):
            existing = localization_keys.get(("l_english", key))
            if existing is not None:
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.create.localization_key_exists",
                        message=(f"English localization key {key!r} already exists " f"in reviewed source {existing!r}."),
                        source_path=existing,
                        tree_id=creation.tree_id,
                        focus_id=creation.focus_id,
                    )
                )

    diagnostics = list(_sorted_diagnostics(diagnostics))
    blocked = creation is None or tree is None or localization is None or image_path is None or any(row.severity == _ERROR for row in diagnostics)
    drafts: list[dict[str, object]] = []
    replacement_rows: list[dict[str, object]] = []
    absent_targets: list[dict[str, object]] = []
    if not blocked and creation is not None and tree is not None and localization is not None and image_path is not None:
        try:
            def_replacement = _focus_creation_replacement(tree, creation)
            merged = merge_source_replacements((def_replacement,))
            def_drafts, def_replacement_rows = render_source_drafts(
                model.documents,
                merged,
            )
            loc_replacement = _localization_creation_replacement(
                localization,
                creation,
            )
            loc_draft, loc_replacement_row = _render_localization_draft(
                localization,
                loc_replacement,
            )
            drafts = sorted(
                [*def_drafts, loc_draft],
                key=lambda row: str(row["path"]),
            )
            replacement_rows = sorted(
                [*def_replacement_rows, loc_replacement_row],
                key=lambda row: (
                    str(row["path"]),
                    int(row["start"]),
                    int(row["end"]),
                ),
            )
            absent_targets = [
                {
                    "path": image_path,
                    "kind": "focus_preview_png",
                    "content_type": "image/png",
                    "precondition": "absent",
                    "write": False,
                }
            ]
        except UnsafeSourcePatch as error:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.source_patch_unsafe",
                    message=str(error),
                    source_path=tree.document.path,
                    tree_id=creation.tree_id,
                    focus_id=creation.focus_id,
                )
            )
            diagnostics = list(_sorted_diagnostics(diagnostics))
            blocked = True

    if blocked:
        drafts = []
        replacement_rows = []
        absent_targets = []
    creation_row = (
        {
            "tree_id": creation.tree_id,
            "focus_id": creation.focus_id,
            "x": creation.x,
            "y": creation.y,
            "title": creation.title,
            "description": creation.description,
            "source_revision": creation.source_revision,
            "localization_source_revision": creation.localization_source_revision,
            "relative_position_id": creation.relative_position_id,
            "prerequisite_id": creation.prerequisite_id,
            "icon_key": creation.icon_key,
        }
        if creation is not None
        else None
    )
    plan: dict[str, object] = {
        "schema": FOCUS_TREE_NODE_CREATION_PLAN_SCHEMA,
        "projection_schema": FOCUS_TREE_DIAGRAM_PROJECTION_SCHEMA,
        "status": "blocked" if blocked else "planned",
        "write": False,
        "offset_unit": "unicode_codepoint",
        "sources": [
            *[
                {
                    "kind": "focus_def",
                    "path": document.path,
                    "source_revision": document.revision,
                    "sha256": document.sha256,
                }
                for document in model.documents
            ],
            *[
                {
                    "kind": "focus_localization",
                    "path": document.path,
                    "source_revision": document.revision,
                    "sha256": document.sha256,
                }
                for document in documents
            ],
        ],
        "intent": creation_row,
        "source_replacements": replacement_rows,
        "drafts": drafts,
        "absent_file_targets": absent_targets,
        "diagnostics": [row.to_dict() for row in diagnostics],
        "summary": {
            "focus_source_count": len(model.documents),
            "localization_source_count": len(documents),
            "replacement_count": len(replacement_rows),
            "draft_count": len(drafts),
            "absent_file_target_count": len(absent_targets),
            "diagnostic_count": len(diagnostics),
        },
    }
    plan["plan_hash"] = stable_payload_hash(plan)
    return plan


def _normalize_creation_intent(
    intent: FocusCreationIntent | Mapping[str, object],
) -> tuple[_FocusCreation | None, tuple[_Diagnostic, ...]]:
    if isinstance(intent, FocusCreationIntent):
        values: Mapping[str, object] = {
            "tree_id": intent.tree_id,
            "focus_id": intent.focus_id,
            "x": intent.x,
            "y": intent.y,
            "title": intent.title,
            "description": intent.description,
            "source_revision": intent.source_revision,
            "localization_source_revision": intent.localization_source_revision,
            "relative_position_id": intent.relative_position_id,
            "prerequisite_id": intent.prerequisite_id,
            "icon_key": intent.icon_key,
        }
    elif isinstance(intent, Mapping):
        values = intent
    else:
        return None, (
            _Diagnostic(
                code="focus_tree.create.invalid_intent",
                message="Focus creation requires one FocusCreationIntent or mapping.",
            ),
        )

    tree_id = values.get("tree_id")
    focus_id = values.get("focus_id")
    x = values.get("x")
    y = values.get("y")
    title = values.get("title")
    description = values.get("description")
    source_revision = values.get("source_revision")
    localization_source_revision = values.get("localization_source_revision")
    relative_position_id = values.get("relative_position_id")
    prerequisite_id = values.get("prerequisite_id")
    icon_key = values.get("icon_key")
    diagnostics: list[_Diagnostic] = []

    if not _valid_unquoted_identifier(tree_id):
        diagnostics.append(
            _Diagnostic(
                code="focus_tree.create.invalid_tree_id",
                message="Focus creation requires a path-safe unquoted tree_id.",
            )
        )
    if not _valid_unquoted_identifier(focus_id) or len(str(focus_id).encode("utf-8")) > _MAX_FOCUS_ID_BYTES:
        diagnostics.append(
            _Diagnostic(
                code="focus_tree.create.invalid_focus_id",
                message=("Focus creation requires a path-safe unquoted focus_id no " f"larger than {_MAX_FOCUS_ID_BYTES} UTF-8 bytes."),
            )
        )
    for field, value in (("x", x), ("y", y)):
        if not isinstance(value, int) or isinstance(value, bool) or abs(value) > _MAX_FOCUS_COORDINATE:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.invalid_coordinate",
                    message=(f"Focus creation {field} must be an integer between " f"-{_MAX_FOCUS_COORDINATE} and " f"{_MAX_FOCUS_COORDINATE}."),
                    focus_id=focus_id if isinstance(focus_id, str) else None,
                )
            )
    diagnostics.extend(
        _creation_localization_text_diagnostics(
            title,
            field="title",
            max_bytes=_MAX_FOCUS_TITLE_BYTES,
            one_line=True,
            focus_id=focus_id if isinstance(focus_id, str) else None,
        )
    )
    diagnostics.extend(
        _creation_localization_text_diagnostics(
            description,
            field="description",
            max_bytes=_MAX_FOCUS_DESCRIPTION_BYTES,
            one_line=False,
            focus_id=focus_id if isinstance(focus_id, str) else None,
        )
    )
    if not is_source_revision(source_revision):
        diagnostics.append(
            _Diagnostic(
                code="focus_tree.create.review_revision_required",
                message="Focus creation requires the exact reviewed def.txt source_revision.",
                focus_id=focus_id if isinstance(focus_id, str) else None,
            )
        )
    if not is_source_revision(localization_source_revision):
        diagnostics.append(
            _Diagnostic(
                code="focus_tree.create.localization_review_revision_required",
                message=("Focus creation requires the exact reviewed main.loc " "localization_source_revision."),
                focus_id=focus_id if isinstance(focus_id, str) else None,
            )
        )
    for field, value in (
        ("relative_position_id", relative_position_id),
        ("prerequisite_id", prerequisite_id),
    ):
        if value is not None and not _valid_unquoted_identifier(value):
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.invalid_reference",
                    message=f"Focus creation {field} must be a path-safe unquoted focus id.",
                    focus_id=focus_id if isinstance(focus_id, str) else None,
                )
            )
        elif value is not None and value == focus_id:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.self_reference",
                    message=f"New focus {focus_id!r} cannot use itself as {field}.",
                    focus_id=focus_id if isinstance(focus_id, str) else None,
                )
            )
    if icon_key is None:
        icon_key = "GFX_goal_unknown"
    if not _valid_unquoted_identifier(icon_key):
        diagnostics.append(
            _Diagnostic(
                code="focus_tree.create.invalid_icon_key",
                message="Focus creation icon_key must be a path-safe unquoted PDX identifier.",
                focus_id=focus_id if isinstance(focus_id, str) else None,
            )
        )

    if diagnostics:
        return None, tuple(_sorted_diagnostics(diagnostics))
    return (
        _FocusCreation(
            tree_id=str(tree_id),
            focus_id=str(focus_id),
            x=int(x),
            y=int(y),
            title=str(title),
            description=str(description),
            source_revision=str(source_revision),
            localization_source_revision=str(localization_source_revision),
            relative_position_id=str(relative_position_id) if relative_position_id is not None else None,
            prerequisite_id=str(prerequisite_id) if prerequisite_id is not None else None,
            icon_key=str(icon_key),
        ),
        (),
    )


def _creation_localization_text_diagnostics(
    value: object,
    *,
    field: str,
    max_bytes: int,
    one_line: bool,
    focus_id: str | None,
) -> tuple[_Diagnostic, ...]:
    if not isinstance(value, str) or not value or value != value.strip() or not is_utf8_text(value):
        return (
            _Diagnostic(
                code=f"focus_tree.create.invalid_{field}",
                message=f"Focus creation {field} must be non-empty trimmed UTF-8 text.",
                focus_id=focus_id,
            ),
        )
    if any((character == "\n" and one_line) or (character != "\n" and unicodedata.category(character) in {"Cc", "Zl", "Zp"}) for character in value):
        return (
            _Diagnostic(
                code=f"focus_tree.create.invalid_{field}",
                message=(f"Focus creation {field} contains unsupported control or " "line-break characters."),
                focus_id=focus_id,
            ),
        )
    if any(line.lstrip().startswith("[") for line in value.split("\n")):
        return (
            _Diagnostic(
                code=f"focus_tree.create.invalid_{field}",
                message=(f"Focus creation {field} cannot contain a line beginning " "with '[' because .loc reserves it for section headers."),
                focus_id=focus_id,
            ),
        )
    if len(value.encode("utf-8")) > max_bytes:
        return (
            _Diagnostic(
                code=f"focus_tree.create.{field}_size_limit_exceeded",
                message=f"Focus creation {field} exceeds the {max_bytes}-byte safety limit.",
                focus_id=focus_id,
            ),
        )
    return ()


def _localization_documents(
    sources: Sequence[FocusTreeLocalizationSource | Mapping[str, object]],
) -> tuple[tuple[_LocalizationDocument, ...], tuple[_Diagnostic, ...]]:
    if len(sources) > _MAX_FOCUS_SOURCES:
        return (), (
            _Diagnostic(
                code="focus_tree.create.localization_source_limit_exceeded",
                message=("Focus creation accepts at most " f"{_MAX_FOCUS_SOURCES} localization sources."),
            ),
        )

    normalized: list[FocusTreeLocalizationSource] = []
    diagnostics: list[_Diagnostic] = []
    total_bytes = 0
    for index, source in enumerate(sources):
        if isinstance(source, FocusTreeLocalizationSource):
            row = source
        elif isinstance(source, Mapping):
            path = source.get("path")
            text = source.get("text")
            if not isinstance(path, str) or not isinstance(text, str):
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.create.invalid_localization_source",
                        message=(f"Localization source {index} requires string " "'path' and 'text' fields."),
                    )
                )
                continue
            row = FocusTreeLocalizationSource(path=path, text=text)
        else:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.invalid_localization_source",
                    message=(f"Localization source {index} is not a " "FocusTreeLocalizationSource or mapping."),
                )
            )
            continue
        safe_path = _safe_project_path(row.path, suffix=".loc")
        if safe_path is None:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.localization_path_unsafe",
                    message=(f"Localization source {row.path!r} is not a safe " "project-relative .loc path."),
                    source_path=row.path,
                )
            )
            continue
        try:
            size = len(row.text.encode("utf-8"))
        except UnicodeEncodeError:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.localization_invalid_unicode",
                    message="Localization source cannot be encoded as UTF-8.",
                    source_path=safe_path,
                )
            )
            continue
        if size > _MAX_SOURCE_BYTES:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.localization_size_limit_exceeded",
                    message=(f"Localization source {safe_path!r} exceeds the " f"{_MAX_SOURCE_BYTES}-byte safety limit."),
                    source_path=safe_path,
                )
            )
            continue
        total_bytes += size
        normalized.append(FocusTreeLocalizationSource(path=safe_path, text=row.text))
    if total_bytes > _MAX_TOTAL_SOURCE_BYTES:
        diagnostics.append(
            _Diagnostic(
                code="focus_tree.create.localization_total_size_limit_exceeded",
                message=("Focus creation localization sources exceed the " f"{_MAX_TOTAL_SOURCE_BYTES}-byte total safety limit."),
            )
        )
        return (), tuple(_sorted_diagnostics(diagnostics))

    documents: list[_LocalizationDocument] = []
    seen_paths: set[str] = set()
    for source in sorted(normalized, key=lambda row: (row.path, row.text)):
        if source.path in seen_paths:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.localization_duplicate_path",
                    message=f"Localization source path {source.path!r} is repeated.",
                    source_path=source.path,
                )
            )
            continue
        seen_paths.add(source.path)
        digest = text_sha256(source.text)
        documents.append(
            _LocalizationDocument(
                path=source.path,
                text=source.text,
                sha256=digest,
                revision=f"sha256:{digest}",
            )
        )
    return tuple(documents), tuple(_sorted_diagnostics(diagnostics))


def _normalize_occupied_paths(
    paths: Sequence[str],
) -> tuple[dict[str, str], tuple[_Diagnostic, ...]]:
    if len(paths) > MAX_FOCUS_TREE_NODE_CREATION_OCCUPIED_PATHS:
        return {}, (
            _Diagnostic(
                code="focus_tree.create.occupied_path_limit_exceeded",
                message=("Focus creation accepts at most " f"{MAX_FOCUS_TREE_NODE_CREATION_OCCUPIED_PATHS} " "occupied project paths."),
            ),
        )
    occupied: dict[str, str] = {}
    diagnostics: list[_Diagnostic] = []
    for index, path in enumerate(paths):
        safe_path = _safe_project_path(path) if isinstance(path, str) else None
        if safe_path is None:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.occupied_path_unsafe",
                    message=f"Occupied project path {index} is not a safe relative path.",
                )
            )
            continue
        key = _portable_path_key(safe_path)
        previous = occupied.get(key)
        if previous is not None and previous != safe_path:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.create.occupied_path_ambiguous",
                    message=(f"Occupied project paths {previous!r} and " f"{safe_path!r} collide across supported filesystems."),
                    source_path=safe_path,
                )
            )
            continue
        occupied[key] = safe_path
    return occupied, tuple(_sorted_diagnostics(diagnostics))


def _safe_project_path(
    value: object,
    *,
    basename: str | None = None,
    suffix: str | None = None,
) -> str | None:
    if not isinstance(value, str) or not value or value != value.strip() or "\x00" in value or not is_utf8_text(value):
        return None
    normalized = value.replace("\\", "/")
    parts = normalized.split("/")
    if normalized.startswith("/") or not parts:
        return None
    if any(part in {"", ".", ".."} for part in parts) or ":" in parts[0]:
        return None
    name = parts[-1]
    if basename is not None and name != basename:
        return None
    if suffix is not None and not name.endswith(suffix):
        return None
    return normalized


def _portable_path_key(path: str) -> str:
    return unicodedata.normalize("NFC", path).casefold()


def _localization_keys(
    documents: Sequence[_LocalizationDocument],
) -> tuple[dict[tuple[str, str], str], tuple[_Diagnostic, ...]]:
    keys: dict[tuple[str, str], str] = {}
    diagnostics: list[_Diagnostic] = []
    for document in documents:
        for line_number, line in enumerate(document.text.splitlines(), start=1):
            stripped = line.strip().lstrip("\ufeff")
            if not stripped.startswith("["):
                continue
            match = _LOC_HEADER.fullmatch(stripped)
            if match is None:
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.create.localization_header_ambiguous",
                        message=(
                            f"Localization source {document.path!r} line " f"{line_number} begins with '[' but is not one " "unambiguous [language.key] header."
                        ),
                        source_path=document.path,
                    )
                )
                continue
            key = (canonical_language(match.group(1)), match.group(2).strip())
            previous = keys.get(key)
            if previous is not None:
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.create.localization_key_ambiguous",
                        message=(
                            f"Localization key {key[1]!r} for {key[0]!r} is "
                            f"declared more than once in reviewed sources "
                            f"{previous!r} and {document.path!r}."
                        ),
                        source_path=document.path,
                    )
                )
                continue
            keys[key] = document.path
    return keys, tuple(_sorted_diagnostics(diagnostics))


def _is_ini_localization(text: str) -> bool:
    for line in text.splitlines():
        visible = line.strip().lstrip("\ufeff")
        if visible and not visible.startswith("#"):
            return visible.startswith("[")
    return True


def _focus_creation_replacement(
    tree: _FocusTreeRecord,
    creation: _FocusCreation,
) -> DiagramSourceReplacement:
    child_indent, insertion = block_child_insertion(
        tree.document,
        tree.entry,
        tree.block,
    )
    unit = indent_unit(tree.document, tree.block, child_indent)
    field_indent = child_indent + unit
    relation_indent = field_indent + unit
    newline = source_newline(tree.document.text, insertion)
    lines = [
        f"{child_indent}focus = {{",
        f"{field_indent}id = {creation.focus_id}",
        f"{field_indent}icon = {creation.icon_key}",
    ]
    if creation.relative_position_id is not None:
        lines.append(f"{field_indent}relative_position_id = {creation.relative_position_id}")
    if creation.prerequisite_id is not None:
        lines.extend(
            (
                f"{field_indent}prerequisite = {{",
                f"{relation_indent}focus = {creation.prerequisite_id}",
                f"{field_indent}}}",
            )
        )
    lines.extend(
        (
            f"{field_indent}x = {creation.x}",
            f"{field_indent}y = {creation.y}",
            f"{child_indent}}}",
        )
    )
    replacement = newline.join(lines) + newline
    return DiagramSourceReplacement(
        path=tree.document.path,
        start=insertion,
        end=insertion,
        expected="",
        replacement=replacement,
        operations=(f"create_focus:{creation.focus_id}:definition",),
        order_key=f"create_focus:{creation.focus_id}:10:def",
    )


def _localization_creation_replacement(
    document: _LocalizationDocument,
    creation: _FocusCreation,
) -> DiagramSourceReplacement:
    newline = source_newline(document.text, len(document.text))
    visible = document.text.lstrip("\ufeff \t\r\n")
    if not visible:
        separator = ""
    elif document.text.endswith(f"{newline}{newline}"):
        separator = ""
    elif document.text.endswith(newline):
        separator = newline
    else:
        separator = newline + newline
    description = newline.join(creation.description.split("\n"))
    replacement = (
        f"{separator}[en.{creation.focus_id}]{newline}"
        f"{creation.title}{newline}{newline}"
        f"[en.{creation.focus_id}_desc]{newline}"
        f"{description}{newline}"
    )
    return DiagramSourceReplacement(
        path=document.path,
        start=len(document.text),
        end=len(document.text),
        expected="",
        replacement=replacement,
        operations=(f"create_focus:{creation.focus_id}:english_localization",),
        order_key=f"create_focus:{creation.focus_id}:20:localization",
    )


def _render_localization_draft(
    document: _LocalizationDocument,
    replacement: DiagramSourceReplacement,
) -> tuple[dict[str, object], dict[str, object]]:
    if replacement.path != document.path or replacement.start != replacement.end or replacement.start != len(document.text):
        raise UnsafeSourcePatch("Canonical focus localization must be an exact append-only replacement.")
    if document.text[replacement.start : replacement.end] != replacement.expected:
        raise UnsafeSourcePatch("Canonical focus localization no longer matches its reviewed source.")
    text = document.text + replacement.replacement
    try:
        size = len(text.encode("utf-8"))
    except UnicodeEncodeError as error:
        raise UnsafeSourcePatch("Generated focus localization is not valid UTF-8.") from error
    if size > _MAX_SOURCE_BYTES:
        raise UnsafeSourcePatch("Generated focus localization exceeds the " f"{_MAX_SOURCE_BYTES}-byte safety limit.")
    digest = text_sha256(text)
    return (
        {
            "path": document.path,
            "expected_source_revision": document.revision,
            "expected_sha256": document.sha256,
            "text": text,
            "sha256": digest,
            "source_revision": f"sha256:{digest}",
        },
        {
            "path": replacement.path,
            "start": replacement.start,
            "end": replacement.end,
            "expected": replacement.expected,
            "replacement": replacement.replacement,
            "operations": list(replacement.operations),
        },
    )


def _focus_tree_model(
    sources: Sequence[FocusTreeSource | Mapping[str, object]],
) -> _FocusTreeModel:
    documents, diagnostics = _source_documents(sources)
    trees: list[_FocusTreeRecord] = []
    records: list[_FocusRecord] = []
    for document in documents:
        wrappers = document.block.find_all("focus_tree")
        if not wrappers:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.source.missing_wrapper",
                    message="Focus-tree def.txt has no 'focus_tree' block.",
                    severity=_WARNING,
                    source_path=document.path,
                )
            )
            continue
        for wrapper in wrappers:
            if not isinstance(wrapper.val, PDXBlock):
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.source.invalid_wrapper",
                        message="'focus_tree' entry must be a PDX block.",
                        source_path=document.path,
                    )
                )
                continue
            tree_id_entries = wrapper.val.find_all("id")
            if len(tree_id_entries) != 1 or entry_scalar_text(tree_id_entries[0]) is None:
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.tree.id_ambiguous",
                        message=("Each focus_tree block must have exactly one " "scalar id."),
                        source_path=document.path,
                    )
                )
                continue
            tree_id_entry = tree_id_entries[0]
            tree_id = entry_scalar_text(tree_id_entry)
            if tree_id is None:
                continue
            tree = _FocusTreeRecord(
                tree_id=tree_id,
                document=document,
                entry=wrapper,
                block=wrapper.val,
                id_entry=tree_id_entry,
            )
            trees.append(tree)
            for entry in wrapper.val.find_all("focus"):
                if not isinstance(entry.val, PDXBlock):
                    diagnostics.append(
                        _Diagnostic(
                            code="focus_tree.focus.invalid_block",
                            message=(f"Focus entry in tree {tree_id!r} must be a " "PDX block."),
                            source_path=document.path,
                            tree_id=tree_id,
                        )
                    )
                    continue
                id_entries = entry.val.find_all("id")
                if len(id_entries) != 1 or entry_scalar_text(id_entries[0]) is None:
                    diagnostics.append(
                        _Diagnostic(
                            code="focus_tree.focus.id_ambiguous",
                            message=(f"Focus entry in tree {tree_id!r} must have " "exactly one scalar id."),
                            source_path=document.path,
                            tree_id=tree_id,
                        )
                    )
                    continue
                focus_id_entry = id_entries[0]
                focus_id = entry_scalar_text(focus_id_entry)
                if focus_id is None:
                    continue
                records.append(
                    _FocusRecord(
                        focus_id=focus_id,
                        tree_id=tree_id,
                        document=document,
                        entry=entry,
                        block=entry.val,
                        id_entry=focus_id_entry,
                    )
                )

    if len(records) > _MAX_FOCUS_NODES:
        diagnostics.append(
            _Diagnostic(
                code="focus_tree.node.limit_exceeded",
                message=(f"Focus projection exceeds the {_MAX_FOCUS_NODES} node " "safety limit."),
            )
        )
        records = sorted(
            records,
            key=lambda row: (
                row.tree_id,
                row.focus_id,
                row.document.path,
            ),
        )[:_MAX_FOCUS_NODES]

    duplicate_tree_ids = _duplicate_tree_ids(trees)
    for tree_id in sorted(duplicate_tree_ids):
        paths = sorted(tree.document.path for tree in trees if tree.tree_id == tree_id)
        diagnostics.append(
            _Diagnostic(
                code="focus_tree.tree.duplicate_id",
                message=(f"Focus tree {tree_id!r} is declared more than once: " f"{', '.join(paths)}."),
                tree_id=tree_id,
            )
        )

    duplicate_focus_ids = _duplicate_focus_ids(records)
    for focus_id in sorted(duplicate_focus_ids):
        paths = sorted(record.document.path for record in records if record.focus_id == focus_id)
        diagnostics.append(
            _Diagnostic(
                code="focus_tree.focus.duplicate_id",
                message=(f"Focus {focus_id!r} is declared more than once: " f"{', '.join(paths)}."),
                focus_id=focus_id,
            )
        )

    declarations: list[_RelationDeclaration] = []
    for record in records:
        diagnostics.extend(_focus_node_diagnostics(record))
        record_declarations, relation_diagnostics = _focus_relations(record)
        declarations.extend(record_declarations)
        diagnostics.extend(relation_diagnostics)
    if len(declarations) > _MAX_FOCUS_EDGES:
        diagnostics.append(
            _Diagnostic(
                code="focus_tree.edge.limit_exceeded",
                message=(f"Focus projection exceeds the {_MAX_FOCUS_EDGES} relation " "declaration safety limit."),
            )
        )
        declarations = sorted(
            declarations,
            key=lambda row: (
                row.kind,
                row.source_id,
                row.target_id,
                row.owner.document.path,
                row.group_index,
            ),
        )[:_MAX_FOCUS_EDGES]

    edges, edge_diagnostics = _focus_edges(
        declarations,
        known_ids={record.focus_id for record in records},
    )
    diagnostics.extend(edge_diagnostics)
    return _FocusTreeModel(
        documents=tuple(documents),
        trees=tuple(trees),
        records=tuple(records),
        declarations=tuple(declarations),
        edges=tuple(edges),
        diagnostics=tuple(_sorted_diagnostics(diagnostics)),
    )


def _source_documents(
    sources: Sequence[FocusTreeSource | Mapping[str, object]],
) -> tuple[list[DiagramSourceDocument], list[_Diagnostic]]:
    diagnostics: list[_Diagnostic] = []
    if len(sources) > _MAX_FOCUS_SOURCES:
        return [], [
            _Diagnostic(
                code="focus_tree.source.limit_exceeded",
                message=(f"Focus projection accepts at most {_MAX_FOCUS_SOURCES} " "source documents."),
            )
        ]

    normalized: list[FocusTreeSource] = []
    total_bytes = 0
    for index, source in enumerate(sources):
        if isinstance(source, FocusTreeSource):
            row = source
        elif isinstance(source, Mapping):
            path = source.get("path")
            text = source.get("text")
            if not isinstance(path, str) or not isinstance(text, str):
                diagnostics.append(
                    _Diagnostic(
                        code="focus_tree.source.invalid_record",
                        message=(f"Source record {index} requires string 'path' and " "'text' fields."),
                    )
                )
                continue
            row = FocusTreeSource(path=path, text=text)
        else:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.source.invalid_record",
                    message=(f"Source record {index} is not a FocusTreeSource or " "mapping."),
                )
            )
            continue
        if not isinstance(row.path, str) or not isinstance(row.text, str):
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.source.invalid_record",
                    message=(f"Source record {index} requires string 'path' and " "'text' fields."),
                )
            )
            continue
        if not is_utf8_text(row.path):
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.source.invalid_path",
                    message=f"Source record {index} path must be valid UTF-8 text.",
                )
            )
            continue
        if not row.path.strip():
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.source.invalid_path",
                    message=f"Source record {index} has an empty path.",
                )
            )
            continue
        if row.path.replace("\\", "/").rsplit("/", 1)[-1] != "def.txt":
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.source.not_def",
                    message=(f"Focus-tree source {row.path!r} is not a module def.txt."),
                    source_path=row.path,
                )
            )
            continue
        try:
            size = len(row.text.encode("utf-8"))
        except UnicodeEncodeError:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.source.invalid_unicode",
                    message="Focus-tree source cannot be encoded as UTF-8.",
                    source_path=row.path,
                )
            )
            continue
        if size > _MAX_SOURCE_BYTES:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.source.size_limit_exceeded",
                    message=(f"Focus-tree source {row.path!r} exceeds the " f"{_MAX_SOURCE_BYTES}-byte safety limit."),
                    source_path=row.path,
                )
            )
            continue
        total_bytes += size
        normalized.append(row)

    if total_bytes > _MAX_TOTAL_SOURCE_BYTES:
        diagnostics.append(
            _Diagnostic(
                code="focus_tree.source.total_size_limit_exceeded",
                message=("Focus-tree sources exceed the " f"{_MAX_TOTAL_SOURCE_BYTES}-byte total safety limit."),
            )
        )
        return [], diagnostics

    normalized.sort(key=lambda row: (row.path, row.text))
    documents: list[DiagramSourceDocument] = []
    seen_paths: set[str] = set()
    for source in normalized:
        if source.path in seen_paths:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.source.duplicate_path",
                    message=(f"Focus-tree source path {source.path!r} is repeated."),
                    source_path=source.path,
                )
            )
            continue
        seen_paths.add(source.path)
        try:
            digest = text_sha256(source.text)
            block = parse_pdx(source.text)
            tokens = lex_pdx_tokens(source.text)
        except PDXParseError as error:
            for row in error.diagnostics:
                diagnostics.append(
                    _Diagnostic(
                        code=row.code,
                        message=(f"{row.message} (line {row.line}, column " f"{row.column})"),
                        severity=row.severity,
                        source_path=source.path,
                    )
                )
            continue
        except UnsafeSourcePatch as error:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.source.lexical_mismatch",
                    message=str(error),
                    source_path=source.path,
                )
            )
            continue
        documents.append(
            DiagramSourceDocument(
                path=source.path,
                text=source.text,
                sha256=digest,
                revision=f"sha256:{digest}",
                block=block,
                tokens=tokens,
            )
        )
    return documents, diagnostics


def _focus_node(
    record: _FocusRecord,
    *,
    duplicate: bool,
    tree_duplicate: bool,
) -> dict[str, object]:
    x, y, position_valid = _focus_position(record)
    row: dict[str, object] = {
        "id": record.focus_id,
        "tree_id": record.tree_id,
        "x": x,
        "y": y,
        "source_path": record.document.path,
        "source_revision": record.document.revision,
        "editable": position_valid and not duplicate and not tree_duplicate,
    }
    icon_entries = record.block.find_all("icon")
    if len(icon_entries) == 1:
        icon = entry_scalar_text(icon_entries[0])
        if icon is not None:
            row["icon"] = icon
    relative_entries = record.block.find_all("relative_position_id")
    if len(relative_entries) == 1:
        relative_id = entry_scalar_text(relative_entries[0])
        if relative_id is not None:
            row["relative_position_id"] = relative_id
    span = source_span(record.id_entry.val)
    if span is not None:
        row["source_span"] = span
    return row


def _focus_node_diagnostics(
    record: _FocusRecord,
) -> tuple[_Diagnostic, ...]:
    x_entries = record.block.find_all("x")
    y_entries = record.block.find_all("y")
    diagnostics: list[_Diagnostic] = []
    if len(x_entries) != 1 or len(y_entries) != 1 or entry_number(x_entries[0]) is None or entry_number(y_entries[0]) is None:
        diagnostics.append(
            _Diagnostic(
                code="focus_tree.focus.coordinates_ambiguous",
                message=(f"Focus {record.focus_id!r} must have exactly one numeric " "x and y for diagram editing."),
                severity=_WARNING,
                source_path=record.document.path,
                tree_id=record.tree_id,
                focus_id=record.focus_id,
            )
        )
    return tuple(diagnostics)


def _focus_position(
    record: _FocusRecord,
) -> tuple[int | float | None, int | float | None, bool]:
    x_entries = record.block.find_all("x")
    y_entries = record.block.find_all("y")
    if len(x_entries) != 1 or len(y_entries) != 1:
        return None, None, False
    x = entry_number(x_entries[0])
    y = entry_number(y_entries[0])
    return x, y, x is not None and y is not None


def _focus_relations(
    record: _FocusRecord,
) -> tuple[list[_RelationDeclaration], list[_Diagnostic]]:
    declarations: list[_RelationDeclaration] = []
    diagnostics: list[_Diagnostic] = []
    for kind in sorted(_EDGE_KINDS):
        fields = record.block.find_all(kind)
        for group_index, relation_entry in enumerate(fields):
            relation_block = relation_entry.val
            if not isinstance(relation_block, PDXBlock):
                diagnostics.append(
                    _Diagnostic(
                        code=f"focus_tree.{kind}.invalid_block",
                        message=(f"Focus {record.focus_id!r} has a non-block " f"{kind} entry."),
                        severity=_WARNING,
                        source_path=record.document.path,
                        tree_id=record.tree_id,
                        focus_id=record.focus_id,
                    )
                )
                continue
            for reference_entry in relation_block.entries:
                if reference_entry.key_str != "focus":
                    diagnostics.append(
                        _Diagnostic(
                            code=f"focus_tree.{kind}.unsupported_entry",
                            message=(f"Focus {record.focus_id!r} {kind} group " "contains an unsupported non-focus entry."),
                            severity=_WARNING,
                            source_path=record.document.path,
                            tree_id=record.tree_id,
                            focus_id=record.focus_id,
                        )
                    )
                    continue
                referenced_id = entry_scalar_text(reference_entry)
                if referenced_id is None:
                    diagnostics.append(
                        _Diagnostic(
                            code=f"focus_tree.{kind}.invalid_reference",
                            message=(f"Focus {record.focus_id!r} {kind} group has " "a non-scalar focus reference."),
                            severity=_WARNING,
                            source_path=record.document.path,
                            tree_id=record.tree_id,
                            focus_id=record.focus_id,
                        )
                    )
                    continue
                if kind == "prerequisite":
                    source_id = referenced_id
                    target_id = record.focus_id
                else:
                    source_id, target_id = sorted((record.focus_id, referenced_id))
                declarations.append(
                    _RelationDeclaration(
                        kind=kind,
                        source_id=source_id,
                        target_id=target_id,
                        owner=record,
                        relation_entry=relation_entry,
                        relation_block=relation_block,
                        reference_entry=reference_entry,
                        group_index=group_index,
                    )
                )
    return declarations, diagnostics


def _focus_edges(
    declarations: Sequence[_RelationDeclaration],
    *,
    known_ids: set[str],
) -> tuple[list[dict[str, object]], list[_Diagnostic]]:
    grouped: dict[tuple[str, str, str], list[_RelationDeclaration]] = defaultdict(list)
    for declaration in declarations:
        grouped[
            (
                declaration.kind,
                declaration.source_id,
                declaration.target_id,
            )
        ].append(declaration)

    edges: list[dict[str, object]] = []
    diagnostics: list[_Diagnostic] = []
    for (kind, source_id, target_id), rows in sorted(grouped.items()):
        rows = sorted(
            rows,
            key=lambda row: (
                row.owner.document.path,
                row.owner.focus_id,
                row.group_index,
            ),
        )
        paths = sorted({row.owner.document.path for row in rows})
        documents = {row.owner.document.path: row.owner.document for row in rows}
        owners = sorted({row.owner.focus_id for row in rows})
        groups = sorted(
            {
                (
                    row.owner.focus_id,
                    row.group_index,
                )
                for row in rows
            }
        )
        tree_ids = sorted({row.owner.tree_id for row in rows})
        revision = _documents_revision(tuple(documents.values()))
        edge: dict[str, object] = {
            "id": f"{kind}:{source_id}->{target_id}",
            "kind": kind,
            "source": source_id,
            "target": target_id,
            "tree_id": tree_ids[0] if tree_ids else "",
            "owner_ids": owners,
            "source_paths": paths,
            "source_revision": revision,
            "relation_groups": [
                {
                    "owner_id": owner_id,
                    "group_index": group_index,
                }
                for owner_id, group_index in groups
            ],
            "declaration_count": len(rows),
            "editable": revision is not None,
        }
        if len(paths) == 1:
            edge["source_path"] = paths[0]
        edges.append(edge)
        if source_id not in known_ids or target_id not in known_ids:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.edge.unresolved",
                    message=(f"Focus {kind} relation {source_id!r} -> " f"{target_id!r} has an endpoint outside the reviewed " "sources."),
                    severity=_WARNING,
                    source_path=paths[0] if paths else None,
                )
            )
        if kind == "mutually_exclusive":
            direction_count = {row.owner.focus_id for row in rows}
            if source_id in known_ids and target_id in known_ids and direction_count != {source_id, target_id}:
                diagnostics.append(
                    _Diagnostic(
                        code=("focus_tree.mutually_exclusive." "missing_reciprocal"),
                        message=("Mutually-exclusive relation " f"{source_id!r} -- {target_id!r} is not declared " "on both focus endpoints."),
                        severity=_WARNING,
                        source_path=paths[0] if paths else None,
                    )
                )
    return edges, diagnostics


def _normalize_position_intents(
    intents: Sequence[FocusPositionIntent | Mapping[str, object]],
) -> tuple[tuple[_PositionChange, ...], tuple[_Diagnostic, ...]]:
    if len(intents) > MAX_MODULE_DIAGRAM_POSITION_INTENTS:
        return (), (
            _Diagnostic(
                code="focus_tree.plan.position_intent_limit_exceeded",
                message=("Focus edit plans accept at most " f"{MAX_MODULE_DIAGRAM_POSITION_INTENTS} position intents."),
            ),
        )
    normalized: dict[str, _PositionChange] = {}
    diagnostics: list[_Diagnostic] = []
    for index, intent in enumerate(intents):
        if isinstance(intent, FocusPositionIntent):
            focus_id = intent.focus_id
            x = intent.x
            y = intent.y
            revision = intent.source_revision
        elif isinstance(intent, Mapping):
            focus_id = intent.get("focus_id")
            x = intent.get("x")
            y = intent.get("y")
            revision = intent.get("source_revision")
        else:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.invalid_position_intent",
                    message=(f"Position intent {index} is not a FocusPositionIntent " "or mapping."),
                )
            )
            continue
        if not _valid_identifier(focus_id):
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.invalid_position_intent",
                    message=(f"Position intent {index} requires a non-empty focus_id."),
                )
            )
            continue
        if not is_finite_number(x) or not is_finite_number(y):
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.invalid_position_intent",
                    message=(f"Position intent for {focus_id!r} requires finite " "numeric x and y."),
                    focus_id=focus_id,
                )
            )
            continue
        if not is_source_revision(revision):
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.review_revision_required",
                    message=(f"Position intent for {focus_id!r} requires its exact " "reviewed sha256 source_revision."),
                    focus_id=focus_id,
                )
            )
            continue
        row = _PositionChange(
            focus_id=focus_id,
            x=x,
            y=y,
            source_revision=revision,
        )
        previous = normalized.get(focus_id)
        if previous is not None and previous != row:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.conflicting_position_intents",
                    message=(f"Focus {focus_id!r} has conflicting reviewed position " "intents."),
                    focus_id=focus_id,
                )
            )
            continue
        normalized[focus_id] = row
    return (
        tuple(normalized[key] for key in sorted(normalized)),
        tuple(_sorted_diagnostics(diagnostics)),
    )


def _normalize_edge_intents(
    intents: Sequence[FocusEdgeIntent | Mapping[str, object]],
) -> tuple[tuple[_EdgeChange, ...], tuple[_Diagnostic, ...]]:
    if len(intents) > MAX_MODULE_DIAGRAM_EDGE_INTENTS:
        return (), (
            _Diagnostic(
                code="focus_tree.plan.edge_intent_limit_exceeded",
                message=("Focus edit plans accept at most " f"{MAX_MODULE_DIAGRAM_EDGE_INTENTS} edge intents."),
            ),
        )
    normalized: dict[tuple[str, str, str], _EdgeChange] = {}
    diagnostics: list[_Diagnostic] = []
    for index, intent in enumerate(intents):
        if isinstance(intent, FocusEdgeIntent):
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
                    code="focus_tree.plan.invalid_edge_intent",
                    message=(f"Edge intent {index} is not a FocusEdgeIntent or " "mapping."),
                )
            )
            continue
        if not isinstance(kind, str) or kind not in _EDGE_KINDS or not _valid_identifier(source_id) or not _valid_identifier(target_id):
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.invalid_edge_intent",
                    message=(f"Edge intent {index} requires kind " "prerequisite/mutually_exclusive and non-empty " "source_id/target_id."),
                )
            )
            continue
        if source_id == target_id:
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.self_edge",
                    message=(f"Focus {kind} relation {source_id!r} cannot target " "itself."),
                    focus_id=source_id,
                )
            )
            continue
        if not isinstance(present, bool):
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.invalid_edge_intent",
                    message=(f"Focus {kind} relation {source_id!r} -> " f"{target_id!r} requires boolean present."),
                )
            )
            continue
        if not is_source_revision(revision):
            diagnostics.append(
                _Diagnostic(
                    code="focus_tree.plan.review_revision_required",
                    message=(f"Focus {kind} relation {source_id!r} -> " f"{target_id!r} requires its exact reviewed sha256 " "source_revision."),
                )
            )
            continue
        if kind == "mutually_exclusive":
            source_id, target_id = sorted((source_id, target_id))
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
                    code="focus_tree.plan.conflicting_edge_intents",
                    message=(f"Focus {kind} relation {source_id!r} -> " f"{target_id!r} has conflicting reviewed intents."),
                )
            )
            continue
        normalized[key] = row
    return (
        tuple(normalized[key] for key in sorted(normalized)),
        tuple(_sorted_diagnostics(diagnostics)),
    )


def _position_replacements(
    record: _FocusRecord,
    intent: _PositionChange,
) -> list[DiagramSourceReplacement]:
    _x, _y, position_valid = _focus_position(record)
    if not position_valid:
        raise UnsafeSourcePatch(f"Focus {record.focus_id!r} requires one numeric x and y before it " "can be moved.")
    x_entries = record.block.find_all("x")
    y_entries = record.block.find_all("y")
    replacements: list[DiagramSourceReplacement] = []
    for field, entry, value in (
        ("x", x_entries[0], intent.x),
        ("y", y_entries[0], intent.y),
    ):
        current = entry_number(entry)
        if entry.op != "=" or not isinstance(entry.val, PDXScalar) or current is None:
            raise UnsafeSourcePatch(f"Focus {record.focus_id!r} position {field} is not one safely " "replaceable numeric scalar.")
        if current == value:
            continue
        token = scalar_token(record.document, entry.val)
        replacement = format_number(value)
        expected = record.document.text[token.start : token.end]
        replacements.append(
            DiagramSourceReplacement(
                path=record.document.path,
                start=token.start,
                end=token.end,
                expected=expected,
                replacement=replacement,
                operations=(f"position:{record.focus_id}:{field}",),
                order_key=f"position:{record.focus_id}:{field}",
            )
        )
    return replacements


def _relation_replacements(
    owner: _FocusRecord,
    *,
    kind: str,
    changes: Sequence[_OwnedRelationChange],
    records_by_id: Mapping[str, _FocusRecord],
) -> list[DiagramSourceReplacement]:
    relation_fields = owner.block.find_all(kind)
    for field in relation_fields:
        if not isinstance(field.val, PDXBlock):
            raise UnsafeSourcePatch(f"Focus {owner.focus_id!r} has a non-block {kind} entry.")

    entries_by_id: dict[str, list[tuple[PDXEntry, PDXEntry]]] = defaultdict(list)
    for field in relation_fields:
        block = field.val
        if not isinstance(block, PDXBlock):
            continue
        for entry in block.entries:
            if entry.key_str != "focus":
                continue
            referenced_id = entry_scalar_text(entry)
            if referenced_id is None:
                raise UnsafeSourcePatch(f"Focus {owner.focus_id!r} has a non-scalar focus reference " f"inside {kind}.")
            entries_by_id[referenced_id].append((field, entry))

    additions: list[str] = []
    removals_by_field: dict[int, list[PDXEntry]] = defaultdict(list)
    field_by_identity = {id(field): field for field in relation_fields}
    for change in sorted(changes, key=lambda row: row.referenced_id):
        matches = entries_by_id.get(change.referenced_id, [])
        if change.present:
            if not matches:
                additions.append(change.referenced_id)
            continue
        for field, entry in matches:
            removals_by_field[id(field)].append(entry)

    if additions and len(relation_fields) > 1:
        raise UnsafeSourcePatch(f"Focus {owner.focus_id!r} has multiple {kind} groups; adding a " "relation would require choosing an authored group.")

    replacements: list[DiagramSourceReplacement] = []
    additions_target = relation_fields[0] if additions and relation_fields else None
    for identity, removed_entries in sorted(
        removals_by_field.items(),
        key=lambda row: row[0],
    ):
        field = field_by_identity[identity]
        block = field.val
        if not isinstance(block, PDXBlock):
            continue
        removable_ids = {id(entry) for entry in removed_entries}
        retained_entries = [entry for entry in block.entries if id(entry) not in removable_ids]
        field_receives_additions = field is additions_target
        if not retained_entries and not field_receives_additions:
            replacements.append(
                whole_entry_line_replacement(
                    owner.document,
                    field,
                    operation=f"{kind}:{owner.focus_id}:remove_empty_group",
                )
            )
            continue
        replacements.extend(
            whole_entry_line_replacement(
                owner.document,
                entry,
                operation=(f"{kind}:{owner.focus_id}->" f"{entry_scalar_text(entry)}:remove"),
            )
            for entry in removed_entries
        )

    if not additions:
        return replacements
    missing_records = [referenced_id for referenced_id in additions if referenced_id not in records_by_id]
    if missing_records:
        raise UnsafeSourcePatch("Cannot add focus relations for unresolved endpoint ids: " f"{', '.join(sorted(missing_records))}.")

    if additions_target is not None:
        block = additions_target.val
        if not isinstance(block, PDXBlock):
            raise UnsafeSourcePatch(f"Focus {owner.focus_id!r} {kind} entry is not a block.")
        child_indent, insertion = block_child_insertion(
            owner.document,
            additions_target,
            block,
        )
        newline = source_newline(owner.document.text, insertion)
        replacement = "".join(f"{child_indent}focus = " f"{_reference_literal(records_by_id[referenced_id])}{newline}" for referenced_id in sorted(additions))
        replacements.append(
            DiagramSourceReplacement(
                path=owner.document.path,
                start=insertion,
                end=insertion,
                expected="",
                replacement=replacement,
                operations=tuple(f"{kind}:{owner.focus_id}->{referenced_id}:add" for referenced_id in sorted(additions)),
                order_key=f"20:{kind}:{owner.focus_id}",
            )
        )
        return replacements

    direct_indent, insertion = block_child_insertion(
        owner.document,
        owner.entry,
        owner.block,
    )
    unit = indent_unit(owner.document, owner.block, direct_indent)
    nested_indent = direct_indent + unit
    newline = source_newline(owner.document.text, insertion)
    replacement = f"{direct_indent}{kind} = {{{newline}"
    replacement += "".join(f"{nested_indent}focus = " f"{_reference_literal(records_by_id[referenced_id])}{newline}" for referenced_id in sorted(additions))
    replacement += f"{direct_indent}}}{newline}"
    replacements.append(
        DiagramSourceReplacement(
            path=owner.document.path,
            start=insertion,
            end=insertion,
            expected="",
            replacement=replacement,
            operations=tuple(f"{kind}:{owner.focus_id}->{referenced_id}:add" for referenced_id in sorted(additions)),
            order_key=f"20:{kind}:{owner.focus_id}",
        )
    )
    return replacements


def _declarations_by_edge(
    declarations: Sequence[_RelationDeclaration],
) -> dict[tuple[str, str, str], tuple[_RelationDeclaration, ...]]:
    grouped: dict[tuple[str, str, str], list[_RelationDeclaration]] = defaultdict(list)
    for declaration in declarations:
        grouped[
            (
                declaration.kind,
                declaration.source_id,
                declaration.target_id,
            )
        ].append(declaration)
    return {
        key: tuple(
            sorted(
                rows,
                key=lambda row: (
                    row.owner.document.path,
                    row.owner.focus_id,
                    row.group_index,
                ),
            )
        )
        for key, rows in grouped.items()
    }


def _register_owned_change(
    changes: dict[tuple[str, str], dict[str, _OwnedRelationChange]],
    change: _OwnedRelationChange,
) -> None:
    key = (change.kind, change.owner_id)
    previous = changes[key].get(change.referenced_id)
    if previous is not None and previous != change:
        raise ValueError("Normalized focus relation changes must not conflict for one owner.")
    changes[key][change.referenced_id] = change


def _documents_revision(
    documents: Sequence[DiagramSourceDocument],
) -> str | None:
    by_path = {document.path: document for document in documents}
    if not by_path:
        return None
    rows = [
        {
            "path": path,
            "source_revision": by_path[path].revision,
        }
        for path in sorted(by_path)
    ]
    if len(rows) == 1:
        return str(rows[0]["source_revision"])
    return f"sha256:{stable_payload_hash({'sources': rows})}"


def _reference_literal(record: _FocusRecord) -> str:
    token = scalar_token(record.document, record.id_entry.val)
    return record.document.text[token.start : token.end]


def _duplicate_tree_ids(
    records: Sequence[_FocusTreeRecord],
) -> set[str]:
    counts = Counter(record.tree_id for record in records)
    return {tree_id for tree_id, count in counts.items() if count > 1}


def _duplicate_focus_ids(
    records: Sequence[_FocusRecord],
) -> set[str]:
    counts = Counter(record.focus_id for record in records)
    return {focus_id for focus_id, count in counts.items() if count > 1}


def _unique_records_by_id(
    records: Sequence[_FocusRecord],
) -> dict[str, _FocusRecord]:
    duplicates = _duplicate_focus_ids(records)
    return {record.focus_id: record for record in records if record.focus_id not in duplicates}


def _stale_revision_diagnostic(
    *,
    focus_id: str,
    source_path: str,
    expected: str,
    provided: str,
) -> _Diagnostic:
    return _Diagnostic(
        code="focus_tree.plan.source_revision_mismatch",
        message=(f"Focus {focus_id!r} changed after review; expected {expected!r}, " f"received {provided!r}."),
        source_path=source_path,
        focus_id=focus_id,
    )


def _valid_identifier(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value == value.strip() and is_utf8_text(value)


def _valid_unquoted_identifier(value: object) -> bool:
    return isinstance(value, str) and _FOCUS_IDENTIFIER.fullmatch(value) is not None and is_utf8_text(value)


def _sorted_diagnostics(
    diagnostics: Sequence[_Diagnostic],
) -> tuple[_Diagnostic, ...]:
    return tuple(
        sorted(
            diagnostics,
            key=lambda row: (
                0 if row.severity == _ERROR else 1,
                row.source_path or "",
                row.tree_id or "",
                row.focus_id or "",
                row.code,
                row.message,
            ),
        )
    )
