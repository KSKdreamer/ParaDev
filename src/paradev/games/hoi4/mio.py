"""Military Industrial Organization projections and exact source edit plans.

The legacy projection remains available for compiled module bundles. The
source-backed diagram contract operates only on caller-reviewed MIO ``.txt``
text and never discovers projects, reads metadata, or writes files.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from paradev._module_diagram_contract import (
    MAX_MODULE_DIAGRAM_EDGE_INTENTS,
    MAX_MODULE_DIAGRAM_POSITION_INTENTS,
)
from paradev.build import (
    Diagnostic,
    LocalizationEntry,
    ModuleSourceBundle,
    PDXBlockSource,
)
from paradev.localization import canonical_language
from paradev.pdx import PDXBlock, PDXEntry, PDXParseError, PDXScalar, parse_pdx

from ._diagram_source import (
    DiagramSourceDocument,
    DiagramSourceReplacement,
    UnsafeSourcePatch,
    block_child_insertion,
    entry_number,
    entry_owns_comments,
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

MIO_TRAIT_PROJECTION_SCHEMA = "paradev.hoi4.mio-trait-projection.v1"
MIO_TRAIT_DIAGRAM_PROJECTION_SCHEMA = "paradev.hoi4.mio-trait-diagram-projection.v1"
MIO_TRAIT_DIAGRAM_PLAN_SCHEMA = "paradev.hoi4.mio-trait-diagram-plan.v1"
MIO_TRAIT_CREATION_PLAN_SCHEMA = "paradev.hoi4.mio-trait-creation-plan.v1"

__all__ = [
    "MIO_TRAIT_CREATION_PLAN_SCHEMA",
    "MIO_TRAIT_DIAGRAM_PLAN_SCHEMA",
    "MIO_TRAIT_DIAGRAM_PROJECTION_SCHEMA",
    "MIO_TRAIT_PROJECTION_SCHEMA",
    "MIOTraitCreationIntent",
    "MIOTraitEdgeIntent",
    "MIOTraitLocalizationSource",
    "MIOTraitPositionIntent",
    "MIOTraitSource",
    "mio_trait_diagram_projection",
    "mio_trait_projection",
    "plan_mio_trait_creation",
    "plan_mio_trait_diagram_edits",
]

_ORGANIZATION_MARKERS = frozenset(
    {
        "include",
        "initial_trait",
        "trait",
        "tree_header_text",
    }
)
_RELATIONSHIP_FIELDS = (
    ("relative_position", "relative_position_id", "relative_position_id"),
    ("any_parent", "any_parent", "any_parent_ids"),
    ("all_parent", "all_parents", "all_parent_ids"),
    ("mutually_exclusive", "mutually_exclusive", "mutually_exclusive_ids"),
)
_TRAIT_KIND_ORDER = {"initial_trait": 0, "trait": 1}
_EDITABLE_RELATIONSHIP_FIELDS = {
    "all_parent": "all_parents",
    "any_parent": "any_parent",
    "mutually_exclusive": "mutually_exclusive",
    "relative_position": "relative_position_id",
}
_ERROR = "error"
_LOC_HEADER = re.compile(r"\[([^\].\s]+)\.([^\]\r\n]+)\]\Z")
_MIO_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]*\Z")
_MIO_LANGUAGE = re.compile(r"l_[a-z][a-z_]*\Z")
_MAX_MIO_COORDINATE = 100_000
_MAX_MIO_EDGES = 65_536
_MAX_MIO_NODES = 32_768
_MAX_MIO_ORGANIZATIONS = 4_096
_MAX_MIO_SOURCES = 256
_MAX_SOURCE_BYTES = 4 * 1024 * 1024
_MAX_TOTAL_SOURCE_BYTES = 32 * 1024 * 1024
_MAX_TRAIT_ID_BYTES = 128
_MAX_TRAIT_TITLE_BYTES = 512
_WARNING = "warning"


@dataclass(frozen=True, slots=True)
class MIOTraitSource:
    """One reviewed MIO organization ``.txt`` source.

    Args:
        path: Normalized project-relative POSIX path ending in ``.txt``.
        text: Complete UTF-8-decoded PDX source, preserving its BOM and newline
            bytes without universal-newline normalization.
    """

    path: str
    text: str


@dataclass(frozen=True, slots=True)
class MIOTraitLocalizationSource:
    """One reviewed project-owned MIO ``.loc`` source."""

    path: str
    text: str


@dataclass(frozen=True, slots=True)
class MIOTraitCreationIntent:
    """Reviewed request to add one trait to an existing organization."""

    organization_id: str
    parent_trait_id: str
    trait_id: str
    title: str
    icon: str
    x: int | float
    y: int | float
    bonus_key: str
    bonus_value: int | float
    language: str
    source_path: str
    source_revision: str


@dataclass(frozen=True, slots=True)
class MIOTraitPositionIntent:
    """Reviewed absolute position for one organization-scoped MIO trait.

    Args:
        organization_id: Game-facing MIO organization identifier.
        trait_id: Organization-scoped trait token or initial-trait name.
        x: Desired finite horizontal coordinate in the inclusive
            ``[-100000, 100000]`` safety range.
        y: Desired finite vertical coordinate in the inclusive
            ``[-100000, 100000]`` safety range.
        source_revision: Exact revision exposed by the reviewed projection.
    """

    organization_id: str
    trait_id: str
    x: int | float
    y: int | float
    source_revision: str


@dataclass(frozen=True, slots=True)
class MIOTraitEdgeIntent:
    """Reviewed desired presence of one MIO trait relationship declaration.

    Relationships point from referenced ``source_id`` to owning ``target_id``.
    Both identifiers are trait tokens scoped to ``organization_id``. The
    target trait's source owns the declaration and its revision. A
    ``mutually_exclusive`` intent is canonicalized as an undirected pair and
    the planner maintains reciprocal declarations on both endpoints.

    Args:
        kind: ``relative_position``, ``any_parent``, ``all_parent``, or
            ``mutually_exclusive``.
        organization_id: Organization containing both endpoints.
        source_id: Referenced trait token.
        target_id: Owning trait token, except that mutually-exclusive
            endpoints are an unordered pair.
        present: Whether the directed declaration should exist.
        source_revision: Exact revision of the target trait's source.
    """

    kind: str
    organization_id: str
    source_id: str
    target_id: str
    present: bool
    source_revision: str


@dataclass(frozen=True, slots=True)
class _EdgeRef:
    module_id: str | None
    organization_id: str
    kind: str
    source_token: str
    target_id: str
    target_token: str
    source_path: str
    span: Mapping[str, int] | None


def mio_trait_projection(
    source: ModuleSourceBundle | Sequence[ModuleSourceBundle],
) -> dict[str, object]:
    """Project compiled MIO organization sources into trait graph records.

    The projection reads the existing parsed PDX and localization records. It
    does not inspect generated `meta.yaml` summaries and deliberately exposes
    no source-write or patch contract. A sequence projects one complete module
    family while resolving organization and trait identities globally.

    Args:
        source (ModuleSourceBundle | Sequence[ModuleSourceBundle]): One loaded
            module source bundle or a deterministic family sequence containing
            compiled MIO organization PDX and optional localization entries.

    Returns:
        dict[str, object]: Deterministic JSON-safe organization, trait, edge,
            diagnostic, and summary rows. `editable` is always `False`.

    Raises:
        ValueError: If a family sequence contains a non-module source bundle.
    """

    bundles = _source_bundles(source)
    localized = _localization_index(tuple(entry for bundle in bundles for entry in bundle.loc_entries))
    organizations: list[dict[str, object]] = []
    traits: list[dict[str, object]] = []
    edge_refs: list[_EdgeRef] = []
    diagnostics: list[Diagnostic] = []
    trait_ids: dict[tuple[str, str], str] = {}
    organization_ids: set[str] = set()

    for bundle in bundles:
        for pdx_source in sorted(bundle.pdx_sources, key=lambda row: row.path):
            for entry in pdx_source.block.entries:
                organization = entry.val
                if not isinstance(organization, PDXBlock) or not _is_organization(organization):
                    continue
                organization_id = entry.key_str
                if not organization_id:
                    continue
                if organization_id in organization_ids:
                    diagnostics.append(
                        _diagnostic(
                            bundle,
                            pdx_source,
                            code="mio.organization_duplicate",
                            message=(f"MIO organization {organization_id!r} is " "declared more than once in this family."),
                            span=_span(entry.key),
                        )
                    )
                    continue
                organization_ids.add(organization_id)
                organization_row = _organization_row(
                    organization_id,
                    organization,
                    source=pdx_source,
                    localized=localized,
                    key_span=_span(entry.key),
                )
                (
                    organization_traits,
                    organization_edges,
                    organization_diagnostics,
                ) = _trait_rows(
                    bundle,
                    pdx_source,
                    organization_id,
                    organization,
                    localized=localized,
                    trait_ids=trait_ids,
                )
                organization_row["module_id"] = bundle.module_id
                organization_row["initial_trait_count"] = sum(row["kind"] == "initial_trait" for row in organization_traits)
                organization_row["trait_count"] = sum(row["kind"] == "trait" for row in organization_traits)
                organizations.append(organization_row)
                traits.extend(organization_traits)
                edge_refs.extend(organization_edges)
                diagnostics.extend(organization_diagnostics)

    edges, edge_diagnostics = _edge_rows(edge_refs, trait_ids)
    diagnostics.extend(edge_diagnostics)
    organizations.sort(key=lambda row: (str(row["organization_id"]), str(row["source_path"])))
    traits.sort(
        key=lambda row: (
            str(row["organization_id"]),
            _TRAIT_KIND_ORDER[str(row["kind"])],
            str(row["id"]),
        )
    )
    diagnostics.sort(
        key=lambda row: (
            str(row.source_path or ""),
            int((row.span or {}).get("line", 0)),
            row.code,
            row.message,
        )
    )
    edge_counts = Counter(str(row["kind"]) for row in edges)
    initial_count = sum(row["kind"] == "initial_trait" for row in traits)
    positioned_count = sum("position" in row for row in traits)
    payload: dict[str, object] = {
        "schema": MIO_TRAIT_PROJECTION_SCHEMA,
        "module_ids": [bundle.module_id for bundle in bundles if bundle.module_id is not None],
        "source_kind": "compiled_pdx",
        "editable": False,
        "organizations": organizations,
        "traits": traits,
        "nodes": [dict(row) for row in traits],
        "edges": edges,
        "diagnostics": [row.to_dict() for row in diagnostics],
        "summary": {
            "organization_count": len(organizations),
            "trait_count": len(traits),
            "initial_trait_count": initial_count,
            "positioned_trait_count": positioned_count,
            "edge_count": len(edges),
            "edge_counts": {kind: edge_counts[kind] for kind in sorted(edge_counts)},
            "diagnostic_count": len(diagnostics),
        },
    }
    if len(bundles) == 1:
        payload["module_id"] = bundles[0].module_id
    return payload


def _organization_row(
    organization_id: str,
    block: PDXBlock,
    *,
    source: PDXBlockSource,
    localized: Mapping[str, Mapping[str, str]],
    key_span: Mapping[str, int] | None,
) -> dict[str, object]:
    name_key = _entry_text(block.find("name")) or organization_id
    row: dict[str, object] = {
        "id": organization_id,
        "organization_id": organization_id,
        "name_key": name_key,
        "localized_titles": dict(localized.get(name_key, localized.get(organization_id, {}))),
        "source_path": source.path,
    }
    icon = _entry_text(block.find("icon"))
    include = _entry_text(block.find("include"))
    if icon:
        row["icon"] = icon
    if include:
        row["include_id"] = include
    if key_span:
        row["source_span"] = dict(key_span)
    return row


def _trait_rows(
    bundle: ModuleSourceBundle,
    source: PDXBlockSource,
    organization_id: str,
    organization: PDXBlock,
    *,
    localized: Mapping[str, Mapping[str, str]],
    trait_ids: dict[tuple[str, str], str],
) -> tuple[list[dict[str, object]], list[_EdgeRef], list[Diagnostic]]:
    rows: list[dict[str, object]] = []
    edges: list[_EdgeRef] = []
    diagnostics: list[Diagnostic] = []
    for entry in organization.entries:
        kind = entry.key_str
        trait = entry.val
        if kind not in _TRAIT_KIND_ORDER or not isinstance(trait, PDXBlock):
            continue
        token_entry = trait.find("token")
        name_entry = trait.find("name")
        token = _entry_text(token_entry)
        name_key = _entry_text(name_entry) or token
        identifier = (token or name_key) if kind == "trait" else name_key
        span = _span(token_entry.val if token_entry is not None else name_entry.val if name_entry is not None else entry.key)
        if not identifier:
            diagnostics.append(
                _diagnostic(
                    bundle,
                    source,
                    code="mio.trait_missing_id",
                    message=f"MIO {kind} in organization {organization_id!r} has no token or name.",
                    span=span,
                )
            )
            continue
        if kind == "trait" and not token:
            diagnostics.append(
                _diagnostic(
                    bundle,
                    source,
                    code="mio.trait_missing_token",
                    message=f"MIO trait {identifier!r} in organization {organization_id!r} uses its name as a fallback id.",
                    severity="warning",
                    span=span,
                )
            )
        trait_key = (organization_id, identifier)
        if trait_key in trait_ids:
            diagnostics.append(
                _diagnostic(
                    bundle,
                    source,
                    code="mio.trait_duplicate_id",
                    message=f"MIO trait id {identifier!r} is repeated in organization {organization_id!r}.",
                    span=span,
                )
            )
            continue
        node_id = _trait_node_id(organization_id, kind, identifier)
        trait_ids[trait_key] = node_id
        row: dict[str, object] = {
            "id": node_id,
            "kind": kind,
            "module_id": bundle.module_id,
            "organization_id": organization_id,
            "name_key": name_key or identifier,
            "localized_titles": dict(localized.get(name_key or identifier, {})),
            "source_path": source.path,
        }
        if token:
            row["token"] = token
        icon = _entry_text(trait.find("icon"))
        if icon:
            row["icon"] = icon
        if span:
            row["source_span"] = dict(span)
        position_entry = trait.find("position")
        if position_entry is not None:
            position = _position(position_entry.val)
            if position is None:
                diagnostics.append(
                    _diagnostic(
                        bundle,
                        source,
                        code="mio.trait_position_unresolved",
                        message=f"MIO trait {identifier!r} in organization {organization_id!r} has a non-numeric or incomplete position.",
                        severity="warning",
                        span=_span(position_entry.key),
                    )
                )
            else:
                row["position"] = position

        for edge_kind, field, row_field in _RELATIONSHIP_FIELDS:
            relationship_entry = trait.find(field)
            references = _entry_identifiers(relationship_entry)
            if not references:
                continue
            row[row_field] = references[0] if field == "relative_position_id" else list(references)
            edges.extend(
                _EdgeRef(
                    module_id=bundle.module_id,
                    organization_id=organization_id,
                    kind=edge_kind,
                    source_token=reference,
                    target_id=node_id,
                    target_token=identifier,
                    source_path=source.path,
                    span=_span(relationship_entry.key) if relationship_entry is not None else None,
                )
                for reference in references
            )
        rows.append(row)
    return rows, edges, diagnostics


def _edge_rows(
    refs: list[_EdgeRef],
    trait_ids: Mapping[tuple[str, str], str],
) -> tuple[list[dict[str, object]], list[Diagnostic]]:
    edges: dict[tuple[str, str, str], dict[str, object]] = {}
    diagnostics: list[Diagnostic] = []
    for ref in refs:
        resolved_source_id = trait_ids.get((ref.organization_id, ref.source_token))
        if resolved_source_id is None:
            diagnostics.append(
                Diagnostic(
                    code="mio.trait_relationship_unresolved",
                    message=(
                        f"MIO {ref.kind} relationship from {ref.source_token!r} "
                        f"to {ref.target_token!r} cannot be resolved inside organization {ref.organization_id!r}."
                    ),
                    severity="warning",
                    family="military_industrial_organization",
                    module_id=ref.module_id,
                    source_path=ref.source_path,
                    span=ref.span,
                )
            )
            continue
        source, target = resolved_source_id, ref.target_id
        if ref.kind == "mutually_exclusive" and target < source:
            source, target = target, source
        key = (ref.kind, source, target)
        edges.setdefault(
            key,
            {
                "id": f"{ref.kind}:{source}->{target}",
                "kind": ref.kind,
                "organization_id": ref.organization_id,
                "source": source,
                "target": target,
            },
        )
    return [edges[key] for key in sorted(edges)], diagnostics


def _source_bundles(
    source: ModuleSourceBundle | Sequence[ModuleSourceBundle],
) -> tuple[ModuleSourceBundle, ...]:
    if isinstance(source, ModuleSourceBundle):
        return (source,)
    bundles = tuple(source)
    if any(not isinstance(bundle, ModuleSourceBundle) for bundle in bundles):
        raise ValueError("MIO trait projection sources must be module source bundles.")
    return tuple(
        sorted(
            bundles,
            key=lambda bundle: (
                str(bundle.module_id or ""),
                bundle.root,
            ),
        )
    )


def _is_organization(block: PDXBlock) -> bool:
    return bool(_ORGANIZATION_MARKERS.intersection(block.keys()))


def _trait_node_id(organization_id: str, kind: str, identifier: str) -> str:
    return f"{organization_id}::{kind}::{identifier}"


def _localization_index(
    entries: tuple[LocalizationEntry, ...],
) -> dict[str, dict[str, str]]:
    localized: dict[str, dict[str, str]] = {}
    for entry in sorted(entries, key=lambda row: (row.key, row.language, row.source_path, row.text)):
        localized.setdefault(entry.key, {}).setdefault(entry.language, entry.text)
    return {key: dict(sorted(rows.items())) for key, rows in sorted(localized.items())}


def _entry_text(entry: PDXEntry | None) -> str | None:
    if entry is None or not isinstance(entry.val, PDXScalar) or entry.val.val is None:
        return None
    text = str(entry.val.val).strip()
    return text or None


def _entry_identifiers(entry: PDXEntry | None) -> tuple[str, ...]:
    if entry is None:
        return ()
    value = entry.val
    if isinstance(value, PDXScalar):
        text = str(value.val).strip() if value.val is not None else ""
        return (text,) if text else ()
    if not isinstance(value, PDXBlock):
        return ()
    identifiers = [str(child.key.val).strip() for child in value.entries if child.key is not None and child.op is None and str(child.key.val).strip()]
    return tuple(dict.fromkeys(identifiers))


def _position(value: object) -> dict[str, int | float] | None:
    if not isinstance(value, PDXBlock):
        return None
    x = _number(value.find("x"))
    y = _number(value.find("y"))
    return {"x": x, "y": y} if x is not None and y is not None else None


def _number(entry: PDXEntry | None) -> int | float | None:
    if entry is None or not isinstance(entry.val, PDXScalar):
        return None
    value = entry.val.eval()
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _span(value: object) -> dict[str, int] | None:
    if not isinstance(value, PDXScalar):
        return None
    span = value.anno.get("span")
    if not isinstance(span, Mapping):
        return None
    line = span.get("line")
    column = span.get("column")
    return {"line": line, "column": column} if isinstance(line, int) and isinstance(column, int) else None


def _diagnostic(
    bundle: ModuleSourceBundle,
    source: PDXBlockSource,
    *,
    code: str,
    message: str,
    severity: str = "error",
    span: Mapping[str, int] | None = None,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        message=message,
        severity=severity,
        family="military_industrial_organization",
        module_id=bundle.module_id,
        source_path=source.path,
        span=span,
    )


@dataclass(frozen=True, slots=True)
class _SourceDiagnostic:
    code: str
    message: str
    severity: str = _ERROR
    source_path: str | None = None
    organization_id: str | None = None
    trait_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        row: dict[str, object] = {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
        }
        if self.source_path is not None:
            row["source_path"] = self.source_path
        if self.organization_id is not None:
            row["organization_id"] = self.organization_id
        if self.trait_id is not None:
            row["trait_id"] = self.trait_id
        return row


@dataclass(frozen=True, slots=True)
class _SourceOrganization:
    organization_id: str
    document: DiagramSourceDocument
    entry: PDXEntry
    block: PDXBlock


@dataclass(frozen=True, slots=True)
class _SourceTrait:
    organization_id: str
    kind: str
    trait_id: str
    document: DiagramSourceDocument
    organization: _SourceOrganization
    entry: PDXEntry
    block: PDXBlock
    id_entry: PDXEntry

    @property
    def node_id(self) -> str:
        return _trait_node_id(self.organization_id, self.kind, self.trait_id)


@dataclass(frozen=True, slots=True)
class _RelationshipDeclaration:
    kind: str
    field_name: str
    group_index: int
    source_id: str
    owner: _SourceTrait
    field_entry: PDXEntry
    reference_entry: PDXEntry


@dataclass(frozen=True, slots=True)
class _MIOSourceModel:
    documents: tuple[DiagramSourceDocument, ...]
    organizations: tuple[_SourceOrganization, ...]
    traits: tuple[_SourceTrait, ...]
    declarations: tuple[_RelationshipDeclaration, ...]
    edges: tuple[dict[str, object], ...]
    diagnostics: tuple[_SourceDiagnostic, ...]


@dataclass(frozen=True, slots=True)
class _MIOLocalizationDocument:
    path: str
    text: str
    sha256: str
    revision: str


@dataclass(frozen=True, slots=True)
class _TraitCreation:
    organization_id: str
    parent_trait_id: str
    trait_id: str
    title: str
    icon: str
    x: int | float
    y: int | float
    bonus_key: str
    bonus_value: int | float
    language: str
    source_path: str
    source_revision: str


@dataclass(frozen=True, slots=True)
class _PositionChange:
    organization_id: str
    trait_id: str
    x: int | float
    y: int | float
    source_revision: str


@dataclass(frozen=True, slots=True)
class _EdgeChange:
    kind: str
    organization_id: str
    source_id: str
    target_id: str
    present: bool
    source_revision: str


def mio_trait_diagram_projection(
    sources: Sequence[MIOTraitSource | Mapping[str, object]],
) -> dict[str, object]:
    """Project exact reviewed MIO ``.txt`` sources into an editable graph.

    This source-backed projection is intentionally separate from
    :func:`mio_trait_projection`, which preserves the compiled-bundle contract
    used by existing readers.

    Args:
        sources: Exact source snapshots. Mapping records use string ``path``
            and ``text`` fields. Text must be decoded from raw UTF-8 bytes
            without normalizing a BOM or newline sequence.

    Returns:
        A deterministic JSON-safe graph with organization-scoped nodes,
        directed relationship declarations, exact content revisions, and
        fail-closed diagnostics.
    """

    model = _mio_source_model(sources)
    duplicate_organizations = _duplicate_organization_ids(model.organizations)
    duplicate_traits = _duplicate_trait_keys(model.traits)
    diagnostics = _sorted_source_diagnostics(model.diagnostics)
    has_errors = any(row.severity == _ERROR for row in diagnostics)
    organizations = [
        _source_organization_row(
            organization,
            duplicate=organization.organization_id in duplicate_organizations,
        )
        for organization in sorted(
            model.organizations,
            key=lambda row: (row.organization_id, row.document.path),
        )
    ]
    nodes = [
        _source_trait_row(
            trait,
            duplicate=(trait.organization_id in duplicate_organizations or (trait.organization_id, trait.trait_id) in duplicate_traits),
        )
        for trait in sorted(
            model.traits,
            key=lambda row: (
                row.organization_id,
                _TRAIT_KIND_ORDER[row.kind],
                row.trait_id,
                row.document.path,
            ),
        )
    ]
    edge_counts = Counter(str(edge["kind"]) for edge in model.edges)
    return {
        "schema": MIO_TRAIT_DIAGRAM_PROJECTION_SCHEMA,
        "source_kind": "module_pdx_source",
        "editable": (any(row["kind"] == "trait" for row in nodes) and not has_errors),
        "sources": [
            {
                "path": document.path,
                "source_revision": document.revision,
                "sha256": document.sha256,
                "size": len(document.text.encode("utf-8")),
            }
            for document in model.documents
        ],
        "organizations": organizations,
        "traits": nodes,
        "nodes": [dict(row) for row in nodes],
        "edges": list(model.edges),
        "diagnostics": [row.to_dict() for row in diagnostics],
        "summary": {
            "source_count": len(model.documents),
            "organization_count": len(organizations),
            "trait_count": len(nodes),
            "initial_trait_count": sum(row["kind"] == "initial_trait" for row in nodes),
            "positioned_trait_count": sum("position" in row for row in nodes),
            "edge_count": len(model.edges),
            "edge_counts": {kind: edge_counts[kind] for kind in sorted(edge_counts)},
            "diagnostic_count": len(diagnostics),
        },
    }


def plan_mio_trait_diagram_edits(
    sources: Sequence[MIOTraitSource | Mapping[str, object]],
    *,
    position_intents: Sequence[MIOTraitPositionIntent | Mapping[str, object]] = (),
    edge_intents: Sequence[MIOTraitEdgeIntent | Mapping[str, object]] = (),
) -> dict[str, object]:
    """Purely plan exact MIO trait source edits for reviewed intents.

    The planner never reads or writes the filesystem. Every intent carries the
    exact content revision exposed by :func:`mio_trait_diagram_projection`.
    Any malformed, ambiguous, stale, cross-organization, unsupported, unsafe,
    or overlapping change blocks the complete plan and returns no drafts.

    Args:
        sources: Current exact MIO ``.txt`` snapshots, decoded from raw UTF-8
            bytes without BOM or newline normalization.
        position_intents: Reviewed organization-scoped position edits.
        edge_intents: Reviewed directed relationship-presence edits.

    Returns:
        A stable-hash plan containing exact source replacements and guarded
        complete drafts, or diagnostics with no changes when blocked.
    """

    model = _mio_source_model(sources)
    diagnostics = list(model.diagnostics)
    positions, position_diagnostics = _normalize_mio_position_intents(position_intents)
    edges, edge_diagnostics = _normalize_mio_edge_intents(edge_intents)
    diagnostics.extend(position_diagnostics)
    diagnostics.extend(edge_diagnostics)

    records_by_key = _unique_source_traits(model)
    replacements: list[DiagramSourceReplacement] = []
    for intent in positions:
        record = records_by_key.get((intent.organization_id, intent.trait_id))
        if record is None:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.node_unresolved",
                    message=(
                        f"MIO trait {intent.trait_id!r} in organization " f"{intent.organization_id!r} does not resolve to " "exactly one reviewed source node."
                    ),
                    organization_id=intent.organization_id,
                    trait_id=intent.trait_id,
                )
            )
            continue
        if intent.source_revision != record.document.revision:
            diagnostics.append(
                _stale_mio_revision_diagnostic(
                    record,
                    provided=intent.source_revision,
                )
            )
            continue
        try:
            replacements.extend(_mio_position_replacements(record, intent))
        except UnsafeSourcePatch as error:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.position_unsafe",
                    message=str(error),
                    source_path=record.document.path,
                    organization_id=record.organization_id,
                    trait_id=record.trait_id,
                )
            )

    edge_groups: dict[
        tuple[str, str, str],
        list[_EdgeChange],
    ] = defaultdict(list)
    organizations_by_trait = _organizations_by_trait_id(model.traits)
    for intent in edges:
        source_record = records_by_key.get((intent.organization_id, intent.source_id))
        target_record = records_by_key.get((intent.organization_id, intent.target_id))
        if source_record is None:
            diagnostics.append(
                _edge_endpoint_diagnostic(
                    intent,
                    endpoint="source",
                    organizations_by_trait=organizations_by_trait,
                )
            )
            continue
        if target_record is None:
            diagnostics.append(
                _edge_endpoint_diagnostic(
                    intent,
                    endpoint="target",
                    organizations_by_trait=organizations_by_trait,
                )
            )
            continue
        if source_record.kind != "trait" or target_record.kind != "trait":
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.initial_trait_relationship_unsupported",
                    message=(f"MIO {intent.kind} relationship " f"{intent.source_id!r} -> {intent.target_id!r} must " "connect token-bearing trait entries."),
                    organization_id=intent.organization_id,
                )
            )
            continue
        if intent.source_revision != target_record.document.revision:
            diagnostics.append(
                _stale_mio_revision_diagnostic(
                    target_record,
                    provided=intent.source_revision,
                )
            )
            continue
        if source_record.document.path != target_record.document.path:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.edge_cross_source_unsafe",
                    message=(
                        f"MIO {intent.kind} relationship "
                        f"{intent.source_id!r} -> {intent.target_id!r} "
                        "resolved across different organization source files."
                    ),
                    organization_id=intent.organization_id,
                    trait_id=intent.target_id,
                )
            )
            continue
        if intent.kind == "mutually_exclusive":
            reciprocal = _EdgeChange(
                kind=intent.kind,
                organization_id=intent.organization_id,
                source_id=intent.target_id,
                target_id=intent.source_id,
                present=intent.present,
                source_revision=intent.source_revision,
            )
            edge_groups[
                (
                    intent.kind,
                    intent.organization_id,
                    reciprocal.target_id,
                )
            ].append(reciprocal)
        edge_groups[
            (
                intent.kind,
                intent.organization_id,
                intent.target_id,
            )
        ].append(intent)

    for (kind, organization_id, target_id), changes in sorted(edge_groups.items()):
        owner = records_by_key[(organization_id, target_id)]
        try:
            replacements.extend(
                _mio_relationship_replacements(
                    owner,
                    kind=kind,
                    changes=changes,
                    records_by_key=records_by_key,
                )
            )
        except UnsafeSourcePatch as error:
            diagnostics.append(
                _SourceDiagnostic(
                    code=f"mio.plan.{kind}_unsafe",
                    message=str(error),
                    source_path=owner.document.path,
                    organization_id=owner.organization_id,
                    trait_id=owner.trait_id,
                )
            )

    diagnostics = list(_sorted_source_diagnostics(diagnostics))
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
                _SourceDiagnostic(
                    code="mio.plan.replacements_unsafe",
                    message=str(error),
                )
            )
            diagnostics = list(_sorted_source_diagnostics(diagnostics))
            blocked = True

    if blocked:
        drafts = []
        replacement_rows = []
    status = "blocked" if blocked else "planned" if drafts else "unchanged"
    intent_rows = {
        "positions": [
            {
                "organization_id": row.organization_id,
                "trait_id": row.trait_id,
                "x": row.x,
                "y": row.y,
                "source_revision": row.source_revision,
            }
            for row in positions
        ],
        "edges": [
            {
                "kind": row.kind,
                "organization_id": row.organization_id,
                "source_id": row.source_id,
                "target_id": row.target_id,
                "present": row.present,
                "source_revision": row.source_revision,
            }
            for row in edges
        ],
    }
    plan: dict[str, object] = {
        "schema": MIO_TRAIT_DIAGRAM_PLAN_SCHEMA,
        "projection_schema": MIO_TRAIT_DIAGRAM_PROJECTION_SCHEMA,
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


def plan_mio_trait_creation(
    sources: Sequence[MIOTraitSource | Mapping[str, object]],
    *,
    localization_sources: Sequence[MIOTraitLocalizationSource | Mapping[str, object]],
    localization_path: str,
    intent: MIOTraitCreationIntent | Mapping[str, object],
) -> dict[str, object]:
    """Plan one exact trait insertion into a reviewed MIO organization.

    The caller selects the owning localization source from registered module
    resource slots. This pure planner verifies that source together with every
    reviewed MIO definition and localization key, then returns complete,
    revision-guarded PDX and localization drafts.
    """

    model = _mio_source_model(sources)
    localizations, localization_diagnostics = _mio_localization_documents(localization_sources)
    creation, creation_diagnostics = _normalize_mio_trait_creation(intent)
    diagnostics = [
        *model.diagnostics,
        *localization_diagnostics,
        *creation_diagnostics,
    ]
    organization: _SourceOrganization | None = None
    parent: _SourceTrait | None = None
    localization: _MIOLocalizationDocument | None = None

    if creation is not None:
        matching_organizations = [
            row for row in model.organizations if row.organization_id == creation.organization_id and row.document.path == creation.source_path
        ]
        if len(matching_organizations) != 1:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.create.organization_unresolved",
                    message=(f"MIO organization {creation.organization_id!r} must " "resolve to exactly one reviewed selected source."),
                    source_path=creation.source_path,
                    organization_id=creation.organization_id,
                )
            )
        else:
            candidate = matching_organizations[0]
            if candidate.document.revision != creation.source_revision:
                diagnostics.append(
                    _SourceDiagnostic(
                        code="mio.create.source_revision_mismatch",
                        message=(
                            f"MIO organization {creation.organization_id!r} "
                            "changed after review; expected "
                            f"{candidate.document.revision!r}, received "
                            f"{creation.source_revision!r}."
                        ),
                        source_path=candidate.document.path,
                        organization_id=creation.organization_id,
                    )
                )
            else:
                organization = candidate

        matching_parents = [
            row
            for row in model.traits
            if row.organization_id == creation.organization_id
            and row.trait_id == creation.parent_trait_id
            and row.kind == "trait"
            and row.document.path == creation.source_path
        ]
        if len(matching_parents) != 1:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.create.parent_unresolved",
                    message=(
                        f"MIO parent trait {creation.parent_trait_id!r} must "
                        "resolve to exactly one token-bearing trait in the "
                        "selected organization and source."
                    ),
                    source_path=creation.source_path,
                    organization_id=creation.organization_id,
                    trait_id=creation.parent_trait_id,
                )
            )
        else:
            parent = matching_parents[0]

        portable_trait_id = _portable_mio_key(creation.trait_id)
        collisions = [row for row in model.traits if row.organization_id == creation.organization_id and _portable_mio_key(row.trait_id) == portable_trait_id]
        if collisions:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.create.trait_id_exists",
                    message=(
                        f"MIO trait id {creation.trait_id!r} collides with "
                        f"existing trait {collisions[0].trait_id!r} in "
                        f"organization {creation.organization_id!r}."
                    ),
                    source_path=collisions[0].document.path,
                    organization_id=creation.organization_id,
                    trait_id=creation.trait_id,
                )
            )

        safe_localization_path = _safe_mio_localization_path(localization_path)
        matching_localizations = [row for row in localizations if safe_localization_path is not None and row.path == safe_localization_path]
        if len(matching_localizations) != 1:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.create.localization_source_unresolved",
                    message=("MIO trait creation requires exactly one reviewed " "module-owned localization source."),
                    source_path=localization_path,
                    organization_id=creation.organization_id,
                    trait_id=creation.trait_id,
                )
            )
        else:
            localization = matching_localizations[0]

        localization_keys, key_diagnostics = _mio_localization_keys(localizations)
        diagnostics.extend(key_diagnostics)
        existing = localization_keys.get((creation.language, creation.trait_id))
        if existing is not None:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.create.localization_key_exists",
                    message=(f"MIO localization key {creation.trait_id!r} for " f"{creation.language!r} already exists in " f"{existing!r}."),
                    source_path=existing,
                    organization_id=creation.organization_id,
                    trait_id=creation.trait_id,
                )
            )

    diagnostics = list(_sorted_source_diagnostics(diagnostics))
    blocked = creation is None or organization is None or parent is None or localization is None or any(row.severity == _ERROR for row in diagnostics)
    drafts: list[dict[str, object]] = []
    replacement_rows: list[dict[str, object]] = []
    if not blocked and creation is not None and organization is not None and parent is not None and localization is not None:
        try:
            definition_replacement = _mio_trait_creation_replacement(
                organization,
                parent,
                creation,
            )
            merged = merge_source_replacements((definition_replacement,))
            definition_drafts, definition_rows = render_source_drafts(
                model.documents,
                merged,
            )
            localization_draft, localization_row = _mio_localization_creation_draft(
                localization,
                creation,
            )
            drafts = sorted(
                [*definition_drafts, localization_draft],
                key=lambda row: str(row["path"]),
            )
            replacement_rows = sorted(
                [*definition_rows, localization_row],
                key=lambda row: (
                    str(row["path"]),
                    int(row["start"]),
                    int(row["end"]),
                ),
            )
        except UnsafeSourcePatch as error:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.create.replacement_unsafe",
                    message=str(error),
                    source_path=creation.source_path,
                    organization_id=creation.organization_id,
                    trait_id=creation.trait_id,
                )
            )
            diagnostics = list(_sorted_source_diagnostics(diagnostics))
            blocked = True

    if blocked:
        drafts = []
        replacement_rows = []
    status = "blocked" if blocked else "planned"
    intent_row = _mio_trait_creation_intent_row(creation) if creation is not None else {}
    plan: dict[str, object] = {
        "schema": MIO_TRAIT_CREATION_PLAN_SCHEMA,
        "projection_schema": MIO_TRAIT_DIAGRAM_PROJECTION_SCHEMA,
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
        ]
        + [
            {
                "path": document.path,
                "source_revision": document.revision,
                "sha256": document.sha256,
            }
            for document in localizations
        ],
        "intents": {"nodes": [intent_row] if intent_row else []},
        **(
            {
                "created_node_id": _trait_node_id(
                    creation.organization_id,
                    "trait",
                    creation.trait_id,
                ),
                "created_scope_id": creation.organization_id,
            }
            if creation is not None
            else {}
        ),
        "source_replacements": replacement_rows,
        "drafts": drafts,
        "diagnostics": [row.to_dict() for row in diagnostics],
        "summary": {
            "node_intent_count": 1 if intent_row else 0,
            "replacement_count": len(replacement_rows),
            "draft_count": len(drafts),
            "diagnostic_count": len(diagnostics),
        },
    }
    plan["plan_hash"] = stable_payload_hash(plan)
    return plan


def _mio_source_model(
    sources: Sequence[MIOTraitSource | Mapping[str, object]],
) -> _MIOSourceModel:
    documents, diagnostics = _mio_source_documents(sources)
    organizations: list[_SourceOrganization] = []
    traits: list[_SourceTrait] = []
    organization_limit_reported = False
    trait_limit_reported = False
    for document in documents:
        for entry in document.block.entries:
            block = entry.val
            if not isinstance(block, PDXBlock) or not _is_organization(block):
                continue
            organization_id = entry.key_str
            if entry.op != "=" or not _valid_mio_identifier(organization_id):
                diagnostics.append(
                    _SourceDiagnostic(
                        code="mio.source.organization_syntax_unsupported",
                        message=("MIO organization declarations require one " "non-empty scalar id and '=' block assignment."),
                        source_path=document.path,
                    )
                )
                continue
            if len(organizations) >= _MAX_MIO_ORGANIZATIONS:
                if not organization_limit_reported:
                    diagnostics.append(
                        _SourceDiagnostic(
                            code="mio.source.organization_limit_exceeded",
                            message=("MIO projection accepts at most " f"{_MAX_MIO_ORGANIZATIONS} organizations."),
                        )
                    )
                    organization_limit_reported = True
                continue
            organization = _SourceOrganization(
                organization_id=organization_id,
                document=document,
                entry=entry,
                block=block,
            )
            organizations.append(organization)
            for trait_entry in block.entries:
                kind = trait_entry.key_str
                if kind not in _TRAIT_KIND_ORDER:
                    continue
                if len(traits) >= _MAX_MIO_NODES:
                    if not trait_limit_reported:
                        diagnostics.append(
                            _SourceDiagnostic(
                                code="mio.source.trait_limit_exceeded",
                                message=("MIO projection accepts at most " f"{_MAX_MIO_NODES} trait nodes."),
                            )
                        )
                        trait_limit_reported = True
                    continue
                trait, trait_diagnostics = _mio_source_trait(
                    organization,
                    trait_entry,
                    kind=kind,
                )
                diagnostics.extend(trait_diagnostics)
                if trait is not None:
                    traits.append(trait)

    duplicate_organizations = _duplicate_organization_ids(organizations)
    for organization_id in sorted(duplicate_organizations):
        paths = sorted(row.document.path for row in organizations if row.organization_id == organization_id)
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.source.organization_duplicate",
                message=(f"MIO organization {organization_id!r} is declared more " f"than once: {', '.join(paths)}."),
                organization_id=organization_id,
            )
        )

    duplicate_traits = _duplicate_trait_keys(traits)
    for organization_id, trait_id in sorted(duplicate_traits):
        paths = sorted(row.document.path for row in traits if (row.organization_id == organization_id and row.trait_id == trait_id))
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.source.trait_duplicate",
                message=(f"MIO trait id {trait_id!r} is repeated in organization " f"{organization_id!r}: {', '.join(paths)}."),
                organization_id=organization_id,
                trait_id=trait_id,
            )
        )

    declarations: list[_RelationshipDeclaration] = []
    for trait in traits:
        diagnostics.extend(_mio_position_diagnostics(trait))
        trait_declarations, trait_diagnostics = _mio_relationship_declarations(trait)
        declarations.extend(trait_declarations)
        diagnostics.extend(trait_diagnostics)

    if len(declarations) > _MAX_MIO_EDGES:
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.source.edge_limit_exceeded",
                message=(f"MIO projection accepts at most {_MAX_MIO_EDGES} " "relationship declarations."),
            )
        )
        declarations = sorted(
            declarations,
            key=lambda row: (
                row.owner.organization_id,
                row.owner.trait_id,
                row.kind,
                row.source_id,
                row.owner.document.path,
            ),
        )[:_MAX_MIO_EDGES]

    records_by_key = _unique_source_traits_from_rows(
        traits,
        duplicate_organizations=duplicate_organizations,
        duplicate_traits=duplicate_traits,
    )
    organizations_by_trait = _organizations_by_trait_id(traits)
    edges_by_key: dict[
        tuple[str, str, str, str],
        dict[str, object],
    ] = {}
    for declaration in declarations:
        owner = declaration.owner
        source = records_by_key.get((owner.organization_id, declaration.source_id))
        if source is None:
            source_organizations = organizations_by_trait.get(
                declaration.source_id,
                set(),
            )
            cross_organization = bool(source_organizations - {owner.organization_id})
            diagnostics.append(
                _SourceDiagnostic(
                    code=("mio.source.relationship_cross_organization" if cross_organization else "mio.source.relationship_unresolved"),
                    message=(
                        f"MIO {declaration.kind} relationship "
                        f"{declaration.source_id!r} -> {owner.trait_id!r} "
                        f"does not resolve to one token-bearing trait inside "
                        f"organization {owner.organization_id!r}."
                    ),
                    source_path=owner.document.path,
                    organization_id=owner.organization_id,
                    trait_id=owner.trait_id,
                )
            )
            continue
        if source.kind != "trait" or owner.kind != "trait":
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.source.initial_trait_relationship_unsupported",
                    message=(f"MIO {declaration.kind} relationships must connect " "token-bearing trait entries."),
                    source_path=owner.document.path,
                    organization_id=owner.organization_id,
                    trait_id=owner.trait_id,
                )
            )
            continue
        if source.trait_id == owner.trait_id:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.source.relationship_self_edge",
                    message=(f"MIO {declaration.kind} relationship for " f"{owner.trait_id!r} cannot reference itself."),
                    source_path=owner.document.path,
                    organization_id=owner.organization_id,
                    trait_id=owner.trait_id,
                )
            )
            continue
        edge_source, edge_target = source, owner
        if declaration.kind == "mutually_exclusive" and edge_target.node_id < edge_source.node_id:
            edge_source, edge_target = edge_target, edge_source
        key = (
            declaration.kind,
            owner.organization_id,
            edge_source.trait_id,
            edge_target.trait_id,
        )
        previous = edges_by_key.get(key)
        if previous is not None:
            previous["declaration_count"] = int(previous["declaration_count"]) + 1
            owner_ids = previous["owner_ids"]
            if isinstance(owner_ids, list) and owner.node_id not in owner_ids:
                owner_ids.append(owner.node_id)
            relation_groups = previous["relation_groups"]
            relation_group = {
                "owner_id": owner.node_id,
                "group_index": declaration.group_index,
            }
            if isinstance(relation_groups, list) and relation_group not in relation_groups:
                relation_groups.append(relation_group)
            continue
        edge: dict[str, object] = {
            "id": (f"{declaration.kind}:" f"{edge_source.node_id}->{edge_target.node_id}"),
            "kind": declaration.kind,
            "organization_id": owner.organization_id,
            "source": edge_source.node_id,
            "target": edge_target.node_id,
            "source_trait_id": edge_source.trait_id,
            "target_trait_id": edge_target.trait_id,
            "owner_ids": [owner.node_id],
            "relation_groups": [
                {
                    "owner_id": owner.node_id,
                    "group_index": declaration.group_index,
                }
            ],
            "source_path": owner.document.path,
            "source_revision": owner.document.revision,
            "declaration_count": 1,
        }
        if declaration.kind != "mutually_exclusive":
            edge["owner_id"] = owner.node_id
        edges_by_key[key] = edge
    edges = list(edges_by_key.values())
    for edge in edges:
        owner_ids = edge.get("owner_ids")
        if isinstance(owner_ids, list):
            owner_ids.sort()
            if edge.get("kind") == "mutually_exclusive":
                edge["reciprocal"] = len(owner_ids) == 2
        relation_groups = edge.get("relation_groups")
        if isinstance(relation_groups, list):
            relation_groups.sort(
                key=lambda row: (
                    str(row.get("owner_id", "")) if isinstance(row, dict) else "",
                    int(row.get("group_index", 0)) if isinstance(row, dict) else 0,
                )
            )
    edges.sort(
        key=lambda row: (
            str(row["organization_id"]),
            str(row["kind"]),
            str(row["source"]),
            str(row["target"]),
            str(row["source_path"]),
        )
    )
    return _MIOSourceModel(
        documents=tuple(documents),
        organizations=tuple(organizations),
        traits=tuple(traits),
        declarations=tuple(declarations),
        edges=tuple(edges),
        diagnostics=tuple(_sorted_source_diagnostics(diagnostics)),
    )


def _mio_source_documents(
    sources: Sequence[MIOTraitSource | Mapping[str, object]],
) -> tuple[list[DiagramSourceDocument], list[_SourceDiagnostic]]:
    diagnostics: list[_SourceDiagnostic] = []
    if len(sources) > _MAX_MIO_SOURCES:
        return [], [
            _SourceDiagnostic(
                code="mio.source.limit_exceeded",
                message=(f"MIO projection accepts at most {_MAX_MIO_SOURCES} " "source documents."),
            )
        ]

    normalized: list[MIOTraitSource] = []
    total_bytes = 0
    for index, source in enumerate(sources):
        if isinstance(source, MIOTraitSource):
            row = source
        elif isinstance(source, Mapping):
            path = source.get("path")
            text = source.get("text")
            if not isinstance(path, str) or not isinstance(text, str):
                diagnostics.append(
                    _SourceDiagnostic(
                        code="mio.source.invalid_record",
                        message=(f"Source record {index} requires string 'path' " "and 'text' fields."),
                    )
                )
                continue
            row = MIOTraitSource(path=path, text=text)
        else:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.source.invalid_record",
                    message=(f"Source record {index} is not an MIOTraitSource or " "mapping."),
                )
            )
            continue
        if not isinstance(row.path, str) or not isinstance(row.text, str):
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.source.invalid_record",
                    message=(f"Source record {index} requires string 'path' and " "'text' fields."),
                )
            )
            continue
        safe_path = _safe_mio_source_path(row.path)
        if safe_path is None:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.source.invalid_path",
                    message=(f"Source record {index} path must be a normalized, " "safe project-relative POSIX path."),
                )
            )
            continue
        if not safe_path.rsplit("/", 1)[-1].endswith(".txt"):
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.source.not_txt",
                    message=(f"MIO source {row.path!r} is not a PDX .txt source."),
                    source_path=row.path,
                )
            )
            continue
        try:
            size = len(row.text.encode("utf-8"))
        except UnicodeEncodeError:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.source.invalid_unicode",
                    message="MIO source cannot be encoded as UTF-8.",
                    source_path=row.path,
                )
            )
            continue
        if size > _MAX_SOURCE_BYTES:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.source.size_limit_exceeded",
                    message=(f"MIO source {row.path!r} exceeds the " f"{_MAX_SOURCE_BYTES}-byte safety limit."),
                    source_path=row.path,
                )
            )
            continue
        total_bytes += size
        normalized.append(row)

    if total_bytes > _MAX_TOTAL_SOURCE_BYTES:
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.source.total_size_limit_exceeded",
                message=("MIO sources exceed the " f"{_MAX_TOTAL_SOURCE_BYTES}-byte total safety limit."),
            )
        )
        return [], diagnostics

    normalized.sort(key=lambda row: (row.path, row.text))
    documents: list[DiagramSourceDocument] = []
    seen_paths: set[str] = set()
    for source in normalized:
        if source.path in seen_paths:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.source.duplicate_path",
                    message=f"MIO source path {source.path!r} is repeated.",
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
                    _SourceDiagnostic(
                        code=row.code,
                        message=(f"{row.message} (line {row.line}, column " f"{row.column})"),
                        severity=row.severity,
                        source_path=source.path,
                    )
                )
            continue
        except UnsafeSourcePatch as error:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.source.lexical_mismatch",
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


def _mio_source_trait(
    organization: _SourceOrganization,
    entry: PDXEntry,
    *,
    kind: str,
) -> tuple[_SourceTrait | None, tuple[_SourceDiagnostic, ...]]:
    diagnostics: list[_SourceDiagnostic] = []
    if entry.op != "=" or not isinstance(entry.val, PDXBlock):
        return None, (
            _SourceDiagnostic(
                code="mio.source.trait_syntax_unsupported",
                message=(f"MIO {kind} in organization " f"{organization.organization_id!r} must be an '=' block " "assignment."),
                source_path=organization.document.path,
                organization_id=organization.organization_id,
            ),
        )
    block = entry.val
    identity_field = "token" if kind == "trait" else "name"
    identity_entries = block.find_all(identity_field)
    if len(identity_entries) != 1 or identity_entries[0].op != "=" or not isinstance(identity_entries[0].val, PDXScalar):
        return None, (
            _SourceDiagnostic(
                code="mio.source.trait_identity_ambiguous",
                message=(f"MIO {kind} in organization " f"{organization.organization_id!r} requires exactly one " f"scalar {identity_field} assignment."),
                source_path=organization.document.path,
                organization_id=organization.organization_id,
            ),
        )
    trait_id = entry_scalar_text(identity_entries[0])
    if not _valid_mio_identifier(trait_id):
        return None, (
            _SourceDiagnostic(
                code="mio.source.trait_identity_invalid",
                message=(f"MIO {kind} in organization " f"{organization.organization_id!r} has an invalid " f"{identity_field}."),
                source_path=organization.document.path,
                organization_id=organization.organization_id,
            ),
        )

    name_entries = block.find_all("name")
    if len(name_entries) > 1 or (
        name_entries
        and (name_entries[0].op != "=" or not isinstance(name_entries[0].val, PDXScalar) or not _valid_mio_identifier(entry_scalar_text(name_entries[0])))
    ):
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.source.trait_name_ambiguous",
                message=(f"MIO {kind} {trait_id!r} in organization " f"{organization.organization_id!r} has unsupported or " "ambiguous name syntax."),
                source_path=organization.document.path,
                organization_id=organization.organization_id,
                trait_id=trait_id,
            )
        )
    return (
        _SourceTrait(
            organization_id=organization.organization_id,
            kind=kind,
            trait_id=trait_id,
            document=organization.document,
            organization=organization,
            entry=entry,
            block=block,
            id_entry=identity_entries[0],
        ),
        tuple(diagnostics),
    )


def _mio_position_diagnostics(
    trait: _SourceTrait,
) -> tuple[_SourceDiagnostic, ...]:
    positions = trait.block.find_all("position")
    common = {
        "source_path": trait.document.path,
        "organization_id": trait.organization_id,
        "trait_id": trait.trait_id,
    }
    if not positions:
        if trait.kind == "trait":
            return (
                _SourceDiagnostic(
                    code="mio.source.position_missing",
                    message=(f"MIO trait {trait.trait_id!r} has no position block " "and cannot be moved in the diagram."),
                    severity=_WARNING,
                    **common,
                ),
            )
        return ()
    if len(positions) != 1:
        return (
            _SourceDiagnostic(
                code="mio.source.position_ambiguous",
                message=(f"MIO trait {trait.trait_id!r} must have at most one " "position block."),
                **common,
            ),
        )
    position_entry = positions[0]
    if position_entry.op != "=" or not isinstance(position_entry.val, PDXBlock):
        return (
            _SourceDiagnostic(
                code="mio.source.position_syntax_unsupported",
                message=(f"MIO trait {trait.trait_id!r} position must be an '=' " "block assignment."),
                **common,
            ),
        )
    position = position_entry.val
    x_entries = position.find_all("x")
    y_entries = position.find_all("y")
    if (
        len(x_entries) != 1
        or len(y_entries) != 1
        or x_entries[0].op != "="
        or y_entries[0].op != "="
        or not isinstance(x_entries[0].val, PDXScalar)
        or not isinstance(y_entries[0].val, PDXScalar)
    ):
        return (
            _SourceDiagnostic(
                code="mio.source.coordinates_ambiguous",
                message=(f"MIO trait {trait.trait_id!r} position requires exactly " "one scalar x and y assignment."),
                **common,
            ),
        )
    x = entry_number(x_entries[0])
    y = entry_number(y_entries[0])
    if not is_finite_number(x) or not is_finite_number(y):
        return (
            _SourceDiagnostic(
                code="mio.source.coordinates_nonfinite",
                message=(f"MIO trait {trait.trait_id!r} position x and y must be " "finite numbers."),
                **common,
            ),
        )
    if not _mio_coordinate_in_bounds(x) or not _mio_coordinate_in_bounds(y):
        return (
            _SourceDiagnostic(
                code="mio.source.coordinates_out_of_bounds",
                message=(f"MIO trait {trait.trait_id!r} position exceeds the " f"±{_MAX_MIO_COORDINATE} safety range."),
                **common,
            ),
        )
    return ()


def _mio_relationship_declarations(
    trait: _SourceTrait,
) -> tuple[
    tuple[_RelationshipDeclaration, ...],
    tuple[_SourceDiagnostic, ...],
]:
    declarations: list[_RelationshipDeclaration] = []
    diagnostics: list[_SourceDiagnostic] = []
    for kind, field_name in sorted(_EDITABLE_RELATIONSHIP_FIELDS.items()):
        fields = trait.block.find_all(field_name)
        if not fields:
            continue
        common = {
            "source_path": trait.document.path,
            "organization_id": trait.organization_id,
            "trait_id": trait.trait_id,
        }
        if trait.kind != "trait":
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.source.initial_trait_relationship_unsupported",
                    message=(f"MIO initial trait {trait.trait_id!r} cannot own " f"{field_name}."),
                    **common,
                )
            )
            continue
        if kind == "relative_position":
            if len(fields) != 1:
                diagnostics.append(
                    _SourceDiagnostic(
                        code="mio.source.relationship_field_ambiguous",
                        message=(f"MIO trait {trait.trait_id!r} has more than one " f"{field_name} field."),
                        **common,
                    )
                )
                continue
            field = fields[0]
            source_id = entry_scalar_text(field)
            if field.op != "=" or not isinstance(field.val, PDXScalar) or not _valid_mio_identifier(source_id):
                diagnostics.append(
                    _SourceDiagnostic(
                        code="mio.source.relationship_syntax_unsupported",
                        message=(f"MIO trait {trait.trait_id!r} " "relative_position_id must be one scalar '=' " "assignment."),
                        **common,
                    )
                )
                continue
            declarations.append(
                _RelationshipDeclaration(
                    kind=kind,
                    field_name=field_name,
                    group_index=0,
                    source_id=source_id,
                    owner=trait,
                    field_entry=field,
                    reference_entry=field,
                )
            )
            continue
        for group_index, field in enumerate(fields):
            if field.op != "=" or not isinstance(field.val, PDXBlock):
                diagnostics.append(
                    _SourceDiagnostic(
                        code="mio.source.relationship_syntax_unsupported",
                        message=(f"MIO trait {trait.trait_id!r} {field_name} must " "be an '=' block of bare trait identifiers."),
                        **common,
                    )
                )
                continue
            seen_ids: set[str] = set()
            for reference in field.val.entries:
                source_id = _bare_reference_id(reference)
                if not _valid_mio_identifier(source_id):
                    diagnostics.append(
                        _SourceDiagnostic(
                            code=("mio.source." "relationship_syntax_unsupported"),
                            message=(f"MIO trait {trait.trait_id!r} " f"{field_name} contains a non-bare trait " "identifier."),
                            **common,
                        )
                    )
                    continue
                if source_id in seen_ids:
                    diagnostics.append(
                        _SourceDiagnostic(
                            code="mio.source.relationship_duplicate",
                            message=(f"MIO trait {trait.trait_id!r} " f"{field_name} repeats {source_id!r} inside " "one relationship group."),
                            **common,
                        )
                    )
                    continue
                seen_ids.add(source_id)
                declarations.append(
                    _RelationshipDeclaration(
                        kind=kind,
                        field_name=field_name,
                        group_index=group_index,
                        source_id=source_id,
                        owner=trait,
                        field_entry=field,
                        reference_entry=reference,
                    )
                )
    return tuple(declarations), tuple(diagnostics)


def _source_organization_row(
    organization: _SourceOrganization,
    *,
    duplicate: bool,
) -> dict[str, object]:
    name_entries = organization.block.find_all("name")
    name_key = entry_scalar_text(name_entries[0]) if len(name_entries) == 1 else None
    row: dict[str, object] = {
        "id": organization.organization_id,
        "organization_id": organization.organization_id,
        "name_key": name_key or organization.organization_id,
        "source_path": organization.document.path,
        "source_revision": organization.document.revision,
        "editable": not duplicate,
    }
    icon_entries = organization.block.find_all("icon")
    if len(icon_entries) == 1:
        icon = entry_scalar_text(icon_entries[0])
        if icon is not None:
            row["icon"] = icon
    include_entries = organization.block.find_all("include")
    if len(include_entries) == 1:
        include_id = entry_scalar_text(include_entries[0])
        if include_id is not None:
            row["include_id"] = include_id
    span = source_span(organization.entry.key)
    if span is not None:
        row["source_span"] = span
    return row


def _source_trait_row(
    trait: _SourceTrait,
    *,
    duplicate: bool,
) -> dict[str, object]:
    x, y, position_valid = _mio_position(trait)
    name_entries = trait.block.find_all("name")
    name_key = entry_scalar_text(name_entries[0]) if len(name_entries) == 1 else None
    row: dict[str, object] = {
        "id": trait.node_id,
        "kind": trait.kind,
        "organization_id": trait.organization_id,
        "trait_id": trait.trait_id,
        "name_key": name_key or trait.trait_id,
        "source_path": trait.document.path,
        "source_revision": trait.document.revision,
        "editable": position_valid and not duplicate,
    }
    if trait.kind == "trait":
        row["token"] = trait.trait_id
    if position_valid:
        row["x"] = x
        row["y"] = y
        row["position"] = {"x": x, "y": y}
    icon_entries = trait.block.find_all("icon")
    if len(icon_entries) == 1:
        icon = entry_scalar_text(icon_entries[0])
        if icon is not None:
            row["icon"] = icon
    span = source_span(trait.id_entry.val)
    if span is not None:
        row["source_span"] = span
    return row


def _normalize_mio_position_intents(
    intents: Sequence[MIOTraitPositionIntent | Mapping[str, object]],
) -> tuple[tuple[_PositionChange, ...], tuple[_SourceDiagnostic, ...]]:
    if len(intents) > MAX_MODULE_DIAGRAM_POSITION_INTENTS:
        return (), (
            _SourceDiagnostic(
                code="mio.plan.position_intent_limit_exceeded",
                message=("MIO edit plans accept at most " f"{MAX_MODULE_DIAGRAM_POSITION_INTENTS} position intents."),
            ),
        )
    normalized: dict[tuple[str, str], _PositionChange] = {}
    diagnostics: list[_SourceDiagnostic] = []
    for index, intent in enumerate(intents):
        if isinstance(intent, MIOTraitPositionIntent):
            organization_id = intent.organization_id
            trait_id = intent.trait_id
            x = intent.x
            y = intent.y
            revision = intent.source_revision
        elif isinstance(intent, Mapping):
            organization_id = intent.get("organization_id")
            trait_id = intent.get("trait_id")
            x = intent.get("x")
            y = intent.get("y")
            revision = intent.get("source_revision")
        else:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.invalid_position_intent",
                    message=(f"Position intent {index} is not an " "MIOTraitPositionIntent or mapping."),
                )
            )
            continue
        if not _valid_mio_identifier(organization_id) or not _valid_mio_identifier(trait_id):
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.invalid_position_intent",
                    message=(f"Position intent {index} requires non-empty " "organization_id and trait_id."),
                )
            )
            continue
        if not is_finite_number(x) or not is_finite_number(y):
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.invalid_position_intent",
                    message=(f"Position intent for MIO trait {trait_id!r} requires " "finite numeric x and y."),
                    organization_id=organization_id,
                    trait_id=trait_id,
                )
            )
            continue
        if not _mio_coordinate_in_bounds(x) or not _mio_coordinate_in_bounds(y):
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.position_out_of_bounds",
                    message=(f"Position intent for MIO trait {trait_id!r} exceeds " f"the ±{_MAX_MIO_COORDINATE} safety range."),
                    organization_id=organization_id,
                    trait_id=trait_id,
                )
            )
            continue
        if not is_source_revision(revision):
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.review_revision_required",
                    message=(f"Position intent for MIO trait {trait_id!r} requires " "its exact reviewed sha256 source_revision."),
                    organization_id=organization_id,
                    trait_id=trait_id,
                )
            )
            continue
        key = (organization_id, trait_id)
        row = _PositionChange(
            organization_id=organization_id,
            trait_id=trait_id,
            x=x,
            y=y,
            source_revision=revision,
        )
        previous = normalized.get(key)
        if previous is not None and previous != row:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.conflicting_position_intents",
                    message=(f"MIO trait {trait_id!r} in organization " f"{organization_id!r} has conflicting reviewed " "position intents."),
                    organization_id=organization_id,
                    trait_id=trait_id,
                )
            )
            continue
        normalized[key] = row
    return (
        tuple(normalized[key] for key in sorted(normalized)),
        _sorted_source_diagnostics(diagnostics),
    )


def _normalize_mio_edge_intents(
    intents: Sequence[MIOTraitEdgeIntent | Mapping[str, object]],
) -> tuple[tuple[_EdgeChange, ...], tuple[_SourceDiagnostic, ...]]:
    if len(intents) > MAX_MODULE_DIAGRAM_EDGE_INTENTS:
        return (), (
            _SourceDiagnostic(
                code="mio.plan.edge_intent_limit_exceeded",
                message=("MIO edit plans accept at most " f"{MAX_MODULE_DIAGRAM_EDGE_INTENTS} edge intents."),
            ),
        )
    normalized: dict[tuple[str, str, str, str], _EdgeChange] = {}
    diagnostics: list[_SourceDiagnostic] = []
    for index, intent in enumerate(intents):
        if isinstance(intent, MIOTraitEdgeIntent):
            kind = intent.kind
            organization_id = intent.organization_id
            source_id = intent.source_id
            target_id = intent.target_id
            present = intent.present
            revision = intent.source_revision
        elif isinstance(intent, Mapping):
            kind = intent.get("kind")
            organization_id = intent.get("organization_id")
            source_id = intent.get("source_id")
            target_id = intent.get("target_id")
            present = intent.get("present")
            revision = intent.get("source_revision")
        else:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.invalid_edge_intent",
                    message=(f"Edge intent {index} is not an MIOTraitEdgeIntent or " "mapping."),
                )
            )
            continue
        if (
            not isinstance(kind, str)
            or kind not in _EDITABLE_RELATIONSHIP_FIELDS
            or not _valid_mio_identifier(organization_id)
            or not _valid_mio_identifier(source_id)
            or not _valid_mio_identifier(target_id)
        ):
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.invalid_edge_intent",
                    message=(f"Edge intent {index} requires a supported kind and " "non-empty organization_id/source_id/target_id."),
                )
            )
            continue
        if source_id == target_id:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.self_edge",
                    message=(f"MIO {kind} relationship for {source_id!r} cannot " "target itself."),
                    organization_id=organization_id,
                    trait_id=target_id,
                )
            )
            continue
        if not isinstance(present, bool):
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.invalid_edge_intent",
                    message=(f"MIO {kind} relationship {source_id!r} -> " f"{target_id!r} requires boolean present."),
                    organization_id=organization_id,
                    trait_id=target_id,
                )
            )
            continue
        if not is_source_revision(revision):
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.review_revision_required",
                    message=(f"MIO {kind} relationship {source_id!r} -> " f"{target_id!r} requires its owner's exact reviewed " "sha256 source_revision."),
                    organization_id=organization_id,
                    trait_id=target_id,
                )
            )
            continue
        if kind == "mutually_exclusive":
            source_id, target_id = sorted((source_id, target_id))
        key = (kind, organization_id, source_id, target_id)
        row = _EdgeChange(
            kind=kind,
            organization_id=organization_id,
            source_id=source_id,
            target_id=target_id,
            present=present,
            source_revision=revision,
        )
        previous = normalized.get(key)
        if previous is not None and previous != row:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.plan.conflicting_edge_intents",
                    message=(f"MIO {kind} relationship {source_id!r} -> " f"{target_id!r} has conflicting reviewed intents."),
                    organization_id=organization_id,
                    trait_id=target_id,
                )
            )
            continue
        normalized[key] = row
    return (
        tuple(normalized[key] for key in sorted(normalized)),
        _sorted_source_diagnostics(diagnostics),
    )


def _mio_position_replacements(
    record: _SourceTrait,
    intent: _PositionChange,
) -> list[DiagramSourceReplacement]:
    _x, _y, position_valid = _mio_position(record)
    if not position_valid:
        raise UnsafeSourcePatch(f"MIO trait {record.trait_id!r} requires one safely bounded " "numeric position before it can be moved.")
    positions = record.block.find_all("position")
    if len(positions) != 1 or positions[0].op != "=" or not isinstance(positions[0].val, PDXBlock):
        raise UnsafeSourcePatch(f"MIO trait {record.trait_id!r} must have exactly one position " "block before it can be moved.")
    x_entries = positions[0].val.find_all("x")
    y_entries = positions[0].val.find_all("y")
    if len(x_entries) != 1 or len(y_entries) != 1:
        raise UnsafeSourcePatch(f"MIO trait {record.trait_id!r} position must contain exactly one " "x and one y scalar.")
    replacements: list[DiagramSourceReplacement] = []
    for field, entry, value in (
        ("x", x_entries[0], intent.x),
        ("y", y_entries[0], intent.y),
    ):
        current = entry_number(entry)
        if entry.op != "=" or not isinstance(entry.val, PDXScalar) or not is_finite_number(current) or not _mio_coordinate_in_bounds(current):
            raise UnsafeSourcePatch(f"MIO trait {record.trait_id!r} position {field} is not one " "safely replaceable bounded numeric scalar.")
        if current == value:
            continue
        token = scalar_token(record.document, entry.val)
        replacement = format_number(value)
        replacements.append(
            DiagramSourceReplacement(
                path=record.document.path,
                start=token.start,
                end=token.end,
                expected=record.document.text[token.start : token.end],
                replacement=replacement,
                operations=(f"position:{record.organization_id}:{record.trait_id}:{field}",),
                order_key=(f"10:position:{record.organization_id}:" f"{record.trait_id}:{field}"),
            )
        )
    return replacements


def _mio_relationship_replacements(
    owner: _SourceTrait,
    *,
    kind: str,
    changes: Sequence[_EdgeChange],
    records_by_key: Mapping[tuple[str, str], _SourceTrait],
) -> list[DiagramSourceReplacement]:
    if kind == "relative_position":
        return _relative_position_replacements(
            owner,
            changes=changes,
            records_by_key=records_by_key,
        )
    return _list_relationship_replacements(
        owner,
        kind=kind,
        changes=changes,
        records_by_key=records_by_key,
    )


def _relative_position_replacements(
    owner: _SourceTrait,
    *,
    changes: Sequence[_EdgeChange],
    records_by_key: Mapping[tuple[str, str], _SourceTrait],
) -> list[DiagramSourceReplacement]:
    fields = owner.block.find_all("relative_position_id")
    if len(fields) > 1:
        raise UnsafeSourcePatch(f"MIO trait {owner.trait_id!r} has multiple " "relative_position_id fields.")
    current_id: str | None = None
    field = fields[0] if fields else None
    if field is not None:
        current_id = entry_scalar_text(field)
        if field.op != "=" or not isinstance(field.val, PDXScalar) or not _valid_mio_identifier(current_id):
            raise UnsafeSourcePatch(f"MIO trait {owner.trait_id!r} relative_position_id is not " "one safely editable scalar.")
    desired = {current_id} if current_id is not None else set()
    for change in changes:
        if change.present:
            desired.add(change.source_id)
        else:
            desired.discard(change.source_id)
    if len(desired) > 1:
        raise UnsafeSourcePatch(f"MIO trait {owner.trait_id!r} can have only one " "relative_position_id; remove the old parent in the same review.")
    desired_id = next(iter(desired), None)
    if desired_id == current_id:
        return []
    if desired_id is not None:
        referenced = records_by_key.get((owner.organization_id, desired_id))
        if referenced is None or referenced.kind != "trait":
            raise UnsafeSourcePatch(f"MIO relative_position endpoint {desired_id!r} does not " f"resolve inside organization {owner.organization_id!r}.")
        literal = _mio_reference_literal(referenced)
        if field is not None and isinstance(field.val, PDXScalar):
            token = scalar_token(owner.document, field.val)
            return [
                DiagramSourceReplacement(
                    path=owner.document.path,
                    start=token.start,
                    end=token.end,
                    expected=owner.document.text[token.start : token.end],
                    replacement=literal,
                    operations=(
                        (f"relative_position:{owner.organization_id}:" f"{current_id}->{owner.trait_id}:remove"),
                        (f"relative_position:{owner.organization_id}:" f"{desired_id}->{owner.trait_id}:add"),
                    ),
                    order_key=(f"20:relative_position:{owner.organization_id}:" f"{owner.trait_id}"),
                )
            ]
        direct_indent, insertion = block_child_insertion(
            owner.document,
            owner.entry,
            owner.block,
        )
        newline = source_newline(owner.document.text, insertion)
        return [
            DiagramSourceReplacement(
                path=owner.document.path,
                start=insertion,
                end=insertion,
                expected="",
                replacement=(f"{direct_indent}relative_position_id = " f"{literal}{newline}"),
                operations=((f"relative_position:{owner.organization_id}:" f"{desired_id}->{owner.trait_id}:add"),),
                order_key=(f"20:relative_position:{owner.organization_id}:" f"{owner.trait_id}"),
            )
        ]
    if field is None:
        return []
    return [
        whole_entry_line_replacement(
            owner.document,
            field,
            operation=(f"relative_position:{owner.organization_id}:" f"{current_id}->{owner.trait_id}:remove"),
        )
    ]


def _list_relationship_replacements(
    owner: _SourceTrait,
    *,
    kind: str,
    changes: Sequence[_EdgeChange],
    records_by_key: Mapping[tuple[str, str], _SourceTrait],
) -> list[DiagramSourceReplacement]:
    field_name = _EDITABLE_RELATIONSHIP_FIELDS[kind]
    fields = owner.block.find_all(field_name)
    blocks_by_field: dict[int, PDXBlock] = {}
    entries_by_id: dict[str, list[tuple[PDXEntry, PDXEntry]]] = defaultdict(list)
    ids_by_field: dict[int, set[str]] = defaultdict(set)
    fields_by_identity: dict[int, PDXEntry] = {}
    for field in fields:
        if field.op != "=" or not isinstance(field.val, PDXBlock):
            raise UnsafeSourcePatch(f"MIO trait {owner.trait_id!r} {field_name} is not one " "safely editable block.")
        identity = id(field)
        fields_by_identity[identity] = field
        blocks_by_field[identity] = field.val
        for entry in field.val.entries:
            reference_id = _bare_reference_id(entry)
            if not _valid_mio_identifier(reference_id):
                raise UnsafeSourcePatch(f"MIO trait {owner.trait_id!r} {field_name} contains " "unsupported relationship syntax.")
            if reference_id in ids_by_field[identity]:
                raise UnsafeSourcePatch(f"MIO trait {owner.trait_id!r} {field_name} repeats " f"{reference_id!r} inside one relationship group.")
            ids_by_field[identity].add(reference_id)
            entries_by_id[reference_id].append((field, entry))

    desired = set(entries_by_id)
    for change in changes:
        if change.present:
            desired.add(change.source_id)
        else:
            desired.discard(change.source_id)
    additions = sorted(desired - set(entries_by_id))
    removals = sorted(set(entries_by_id) - desired)
    if not additions and not removals:
        return []
    for reference_id in additions:
        referenced = records_by_key.get((owner.organization_id, reference_id))
        if referenced is None or referenced.kind != "trait":
            raise UnsafeSourcePatch(f"MIO {field_name} endpoint {reference_id!r} does not resolve " f"inside organization {owner.organization_id!r}.")

    if additions and len(fields) > 1:
        raise UnsafeSourcePatch(
            f"MIO trait {owner.trait_id!r} has multiple authored " f"{field_name} groups; adding a relationship would require " "choosing one group."
        )

    removal_entries_by_field: dict[int, list[tuple[str, PDXEntry]]] = defaultdict(list)
    for reference_id in removals:
        for field, entry in entries_by_id[reference_id]:
            removal_entries_by_field[id(field)].append((reference_id, entry))

    replacements: list[DiagramSourceReplacement] = []
    for identity, removal_entries in sorted(
        removal_entries_by_field.items(),
        key=lambda row: row[0],
    ):
        field = fields_by_identity[identity]
        removed_ids = {_bare_reference_id(entry) for _reference_id, entry in removal_entries}
        retained_ids = ids_by_field[identity] - removed_ids
        field_receives_additions = bool(additions) and len(fields) == 1
        if not retained_ids and not field_receives_additions:
            replacements.append(
                whole_entry_line_replacement(
                    owner.document,
                    field,
                    operation=(f"{kind}:{owner.organization_id}:" f"{owner.trait_id}:remove_empty_group"),
                )
            )
            continue
        replacements.extend(
            _bare_entry_line_replacement(
                owner.document,
                entry,
                operation=(f"{kind}:{owner.organization_id}:" f"{reference_id}->{owner.trait_id}:remove"),
            )
            for reference_id, entry in removal_entries
        )
    if not additions:
        return replacements

    field = fields[0] if fields else None
    block = blocks_by_field.get(id(field)) if field is not None else None
    if field is not None and block is not None:
        child_indent, insertion = block_child_insertion(
            owner.document,
            field,
            block,
        )
        newline = source_newline(owner.document.text, insertion)
        replacements.append(
            DiagramSourceReplacement(
                path=owner.document.path,
                start=insertion,
                end=insertion,
                expected="",
                replacement="".join(
                    f"{child_indent}" f"{_mio_reference_literal(records_by_key[(owner.organization_id, reference_id)])}" f"{newline}"
                    for reference_id in additions
                ),
                operations=tuple(f"{kind}:{owner.organization_id}:" f"{reference_id}->{owner.trait_id}:add" for reference_id in additions),
                order_key=(f"30:{kind}:{owner.organization_id}:{owner.trait_id}"),
            )
        )
        return replacements

    direct_indent, insertion = block_child_insertion(
        owner.document,
        owner.entry,
        owner.block,
    )
    unit = indent_unit(owner.document, owner.block, direct_indent)
    child_indent = direct_indent + unit
    newline = source_newline(owner.document.text, insertion)
    replacement = f"{direct_indent}{field_name} = {{{newline}"
    replacement += "".join(
        f"{child_indent}" f"{_mio_reference_literal(records_by_key[(owner.organization_id, reference_id)])}" f"{newline}" for reference_id in additions
    )
    replacement += f"{direct_indent}}}{newline}"
    replacements.append(
        DiagramSourceReplacement(
            path=owner.document.path,
            start=insertion,
            end=insertion,
            expected="",
            replacement=replacement,
            operations=tuple(f"{kind}:{owner.organization_id}:" f"{reference_id}->{owner.trait_id}:add" for reference_id in additions),
            order_key=(f"30:{kind}:{owner.organization_id}:{owner.trait_id}"),
        )
    )
    return replacements


def _bare_entry_line_replacement(
    document: DiagramSourceDocument,
    entry: PDXEntry,
    *,
    operation: str,
) -> DiagramSourceReplacement:
    if entry.key is None or entry.op is not None or entry.val is not None or entry_owns_comments(entry):
        raise UnsafeSourcePatch(f"Source entry for {operation} is not one comment-free bare " "relationship identifier.")
    token = scalar_token(document, entry.key)
    line_start = document.text.rfind("\n", 0, token.start) + 1
    if document.text[line_start : token.start].strip():
        raise UnsafeSourcePatch(f"Source entry for {operation} is not on its own indented line.")
    newline_index = document.text.find("\n", token.end)
    line_end = len(document.text) if newline_index < 0 else newline_index + 1
    suffix_end = len(document.text) if newline_index < 0 else newline_index
    if document.text[token.end : suffix_end].strip():
        raise UnsafeSourcePatch(f"Source entry for {operation} has trailing source on its line.")
    return DiagramSourceReplacement(
        path=document.path,
        start=line_start,
        end=line_end,
        expected=document.text[line_start:line_end],
        replacement="",
        operations=(operation,),
        order_key=operation,
    )


def _mio_position(
    trait: _SourceTrait,
) -> tuple[int | float | None, int | float | None, bool]:
    positions = trait.block.find_all("position")
    if len(positions) != 1 or positions[0].op != "=" or not isinstance(positions[0].val, PDXBlock):
        return None, None, False
    x_entries = positions[0].val.find_all("x")
    y_entries = positions[0].val.find_all("y")
    if len(x_entries) != 1 or len(y_entries) != 1 or x_entries[0].op != "=" or y_entries[0].op != "=":
        return None, None, False
    x = entry_number(x_entries[0])
    y = entry_number(y_entries[0])
    valid = is_finite_number(x) and is_finite_number(y) and _mio_coordinate_in_bounds(x) and _mio_coordinate_in_bounds(y)
    return x, y, valid


def _mio_coordinate_in_bounds(value: float) -> bool:
    return is_finite_number(value) and -_MAX_MIO_COORDINATE <= value <= _MAX_MIO_COORDINATE


def _bare_reference_id(entry: PDXEntry) -> str | None:
    if entry.key is None or entry.op is not None or entry.val is not None or entry.key.val is None:
        return None
    value = str(entry.key.val).strip()
    return value or None


def _mio_reference_literal(record: _SourceTrait) -> str:
    if record.kind != "trait" or not isinstance(record.id_entry.val, PDXScalar):
        raise UnsafeSourcePatch(f"MIO relationship endpoint {record.trait_id!r} has no exact " "token literal.")
    token = scalar_token(record.document, record.id_entry.val)
    return record.document.text[token.start : token.end]


def _duplicate_organization_ids(
    organizations: Sequence[_SourceOrganization],
) -> set[str]:
    counts = Counter(row.organization_id for row in organizations)
    return {organization_id for organization_id, count in counts.items() if count > 1}


def _duplicate_trait_keys(
    traits: Sequence[_SourceTrait],
) -> set[tuple[str, str]]:
    counts = Counter((row.organization_id, row.trait_id) for row in traits)
    return {key for key, count in counts.items() if count > 1}


def _unique_source_traits(
    model: _MIOSourceModel,
) -> dict[tuple[str, str], _SourceTrait]:
    return _unique_source_traits_from_rows(
        model.traits,
        duplicate_organizations=_duplicate_organization_ids(model.organizations),
        duplicate_traits=_duplicate_trait_keys(model.traits),
    )


def _unique_source_traits_from_rows(
    traits: Sequence[_SourceTrait],
    *,
    duplicate_organizations: set[str],
    duplicate_traits: set[tuple[str, str]],
) -> dict[tuple[str, str], _SourceTrait]:
    return {
        (row.organization_id, row.trait_id): row
        for row in traits
        if (row.organization_id not in duplicate_organizations and (row.organization_id, row.trait_id) not in duplicate_traits)
    }


def _organizations_by_trait_id(
    traits: Sequence[_SourceTrait],
) -> dict[str, set[str]]:
    rows: dict[str, set[str]] = defaultdict(set)
    for trait in traits:
        if trait.kind == "trait":
            rows[trait.trait_id].add(trait.organization_id)
    return rows


def _edge_endpoint_diagnostic(
    intent: _EdgeChange,
    *,
    endpoint: str,
    organizations_by_trait: Mapping[str, set[str]],
) -> _SourceDiagnostic:
    endpoint_id = intent.source_id if endpoint == "source" else intent.target_id
    known_organizations = organizations_by_trait.get(endpoint_id, set())
    cross_organization = bool(known_organizations - {intent.organization_id})
    return _SourceDiagnostic(
        code=("mio.plan.edge_cross_organization" if cross_organization else "mio.plan.edge_node_unresolved"),
        message=(
            f"MIO {intent.kind} relationship "
            f"{intent.source_id!r} -> {intent.target_id!r} has no unique "
            f"{endpoint} endpoint inside organization "
            f"{intent.organization_id!r}."
        ),
        organization_id=intent.organization_id,
        trait_id=(intent.target_id if endpoint == "target" else intent.source_id),
    )


def _stale_mio_revision_diagnostic(
    record: _SourceTrait,
    *,
    provided: str,
) -> _SourceDiagnostic:
    return _SourceDiagnostic(
        code="mio.plan.source_revision_mismatch",
        message=(
            f"MIO trait {record.trait_id!r} in organization "
            f"{record.organization_id!r} changed after review; expected "
            f"{record.document.revision!r}, received {provided!r}."
        ),
        source_path=record.document.path,
        organization_id=record.organization_id,
        trait_id=record.trait_id,
    )


def _normalize_mio_trait_creation(
    intent: MIOTraitCreationIntent | Mapping[str, object],
) -> tuple[_TraitCreation | None, tuple[_SourceDiagnostic, ...]]:
    if isinstance(intent, MIOTraitCreationIntent):
        values: Mapping[str, object] = {
            field: getattr(intent, field)
            for field in (
                "organization_id",
                "parent_trait_id",
                "trait_id",
                "title",
                "icon",
                "x",
                "y",
                "bonus_key",
                "bonus_value",
                "language",
                "source_path",
                "source_revision",
            )
        }
    elif isinstance(intent, Mapping):
        values = intent
    else:
        return None, (
            _SourceDiagnostic(
                code="mio.create.invalid_intent",
                message=("MIO trait creation intent must be an " "MIOTraitCreationIntent or mapping."),
            ),
        )

    diagnostics: list[_SourceDiagnostic] = []
    organization_id = values.get("organization_id")
    parent_trait_id = values.get("parent_trait_id")
    trait_id = values.get("trait_id")
    title = values.get("title")
    icon = values.get("icon")
    x = values.get("x")
    y = values.get("y")
    bonus_key = values.get("bonus_key")
    bonus_value = values.get("bonus_value")
    language = values.get("language")
    source_path = values.get("source_path")
    source_revision = values.get("source_revision")

    if not _valid_mio_identifier(organization_id):
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.create.invalid_organization_id",
                message=("MIO trait creation organization_id must be non-empty " "trimmed UTF-8 text."),
            )
        )
    for name, value in (
        ("parent_trait_id", parent_trait_id),
        ("trait_id", trait_id),
        ("icon", icon),
        ("bonus_key", bonus_key),
    ):
        if not isinstance(value, str) or _MIO_TOKEN.fullmatch(value) is None:
            diagnostics.append(
                _SourceDiagnostic(
                    code=f"mio.create.invalid_{name}",
                    message=(f"MIO trait creation {name} must be one unquoted " "identifier."),
                    organization_id=(organization_id if isinstance(organization_id, str) else None),
                    trait_id=(trait_id if isinstance(trait_id, str) else None),
                )
            )
    if isinstance(trait_id, str) and len(trait_id.encode("utf-8")) > _MAX_TRAIT_ID_BYTES:
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.create.trait_id_size_limit_exceeded",
                message=(f"MIO trait id exceeds the {_MAX_TRAIT_ID_BYTES}-byte " "safety limit."),
                organization_id=(organization_id if isinstance(organization_id, str) else None),
                trait_id=trait_id,
            )
        )
    if (
        not isinstance(title, str)
        or not title
        or title != title.strip()
        or "\n" in title
        or "\r" in title
        or any(unicodedata.category(character) in {"Cc", "Zl", "Zp"} for character in title)
        or title.lstrip().startswith("[")
    ):
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.create.invalid_title",
                message=("MIO trait title must be non-empty one-line trimmed " "UTF-8 text without control characters."),
                organization_id=(organization_id if isinstance(organization_id, str) else None),
                trait_id=(trait_id if isinstance(trait_id, str) else None),
            )
        )
    elif len(title.encode("utf-8")) > _MAX_TRAIT_TITLE_BYTES:
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.create.title_size_limit_exceeded",
                message=(f"MIO trait title exceeds the {_MAX_TRAIT_TITLE_BYTES}-byte " "safety limit."),
                organization_id=(organization_id if isinstance(organization_id, str) else None),
                trait_id=(trait_id if isinstance(trait_id, str) else None),
            )
        )
    for name, value in (("x", x), ("y", y)):
        if not is_finite_number(value) or not _mio_coordinate_in_bounds(value):
            diagnostics.append(
                _SourceDiagnostic(
                    code=f"mio.create.invalid_{name}",
                    message=(f"MIO trait creation {name} must be a finite number " f"inside ±{_MAX_MIO_COORDINATE}."),
                    organization_id=(organization_id if isinstance(organization_id, str) else None),
                    trait_id=(trait_id if isinstance(trait_id, str) else None),
                )
            )
    if not is_finite_number(bonus_value) or abs(bonus_value) > _MAX_MIO_COORDINATE:
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.create.invalid_bonus_value",
                message=("MIO trait bonus_value must be a finite number inside " f"±{_MAX_MIO_COORDINATE}."),
                organization_id=(organization_id if isinstance(organization_id, str) else None),
                trait_id=(trait_id if isinstance(trait_id, str) else None),
            )
        )
    canonical = canonical_language(language)
    if _MIO_LANGUAGE.fullmatch(canonical) is None:
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.create.invalid_language",
                message=("MIO trait creation language must resolve to a canonical " "HoI4 l_<language> id."),
                organization_id=(organization_id if isinstance(organization_id, str) else None),
                trait_id=(trait_id if isinstance(trait_id, str) else None),
            )
        )
    safe_source_path = _safe_mio_source_path(source_path)
    if safe_source_path is None or not safe_source_path.endswith(".txt"):
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.create.source_path_unsafe",
                message=("MIO trait creation source_path must be one safe " "project-relative .txt path."),
                organization_id=(organization_id if isinstance(organization_id, str) else None),
                trait_id=(trait_id if isinstance(trait_id, str) else None),
            )
        )
    if not is_source_revision(source_revision):
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.create.invalid_source_revision",
                message=("MIO trait creation source_revision must be a " "sha256:<digest> revision."),
                source_path=(source_path if isinstance(source_path, str) else None),
                organization_id=(organization_id if isinstance(organization_id, str) else None),
                trait_id=(trait_id if isinstance(trait_id, str) else None),
            )
        )
    if diagnostics:
        return None, tuple(_sorted_source_diagnostics(diagnostics))
    assert isinstance(organization_id, str)
    assert isinstance(parent_trait_id, str)
    assert isinstance(trait_id, str)
    assert isinstance(title, str)
    assert isinstance(icon, str)
    assert isinstance(x, (int, float)) and not isinstance(x, bool)
    assert isinstance(y, (int, float)) and not isinstance(y, bool)
    assert isinstance(bonus_key, str)
    assert isinstance(bonus_value, (int, float)) and not isinstance(
        bonus_value,
        bool,
    )
    assert safe_source_path is not None
    assert isinstance(source_revision, str)
    return (
        _TraitCreation(
            organization_id=organization_id,
            parent_trait_id=parent_trait_id,
            trait_id=trait_id,
            title=title,
            icon=icon,
            x=x,
            y=y,
            bonus_key=bonus_key,
            bonus_value=bonus_value,
            language=canonical,
            source_path=safe_source_path,
            source_revision=source_revision,
        ),
        (),
    )


def _mio_localization_documents(
    sources: Sequence[MIOTraitLocalizationSource | Mapping[str, object]],
) -> tuple[
    tuple[_MIOLocalizationDocument, ...],
    tuple[_SourceDiagnostic, ...],
]:
    diagnostics: list[_SourceDiagnostic] = []
    if len(sources) > _MAX_MIO_SOURCES:
        return (), (
            _SourceDiagnostic(
                code="mio.create.localization_source_limit_exceeded",
                message=("MIO trait creation accepts at most " f"{_MAX_MIO_SOURCES} localization sources."),
            ),
        )
    normalized: list[MIOTraitLocalizationSource] = []
    total_bytes = 0
    for index, source in enumerate(sources):
        if isinstance(source, MIOTraitLocalizationSource):
            row = source
        elif isinstance(source, Mapping):
            path = source.get("path")
            text = source.get("text")
            if not isinstance(path, str) or not isinstance(text, str):
                diagnostics.append(
                    _SourceDiagnostic(
                        code="mio.create.invalid_localization_source",
                        message=(f"MIO localization source {index} requires " "string path and text fields."),
                    )
                )
                continue
            row = MIOTraitLocalizationSource(path=path, text=text)
        else:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.create.invalid_localization_source",
                    message=(f"MIO localization source {index} is not a " "MIOTraitLocalizationSource or mapping."),
                )
            )
            continue
        safe_path = _safe_mio_localization_path(row.path)
        if safe_path is None:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.create.localization_path_unsafe",
                    message=(f"MIO localization path {row.path!r} is not a safe " "project-relative .loc path."),
                    source_path=row.path,
                )
            )
            continue
        try:
            size = len(row.text.encode("utf-8"))
        except UnicodeEncodeError:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.create.localization_invalid_unicode",
                    message="MIO localization must be valid UTF-8 text.",
                    source_path=safe_path,
                )
            )
            continue
        if size > _MAX_SOURCE_BYTES:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.create.localization_size_limit_exceeded",
                    message=(f"MIO localization {safe_path!r} exceeds the " f"{_MAX_SOURCE_BYTES}-byte limit."),
                    source_path=safe_path,
                )
            )
            continue
        total_bytes += size
        normalized.append(MIOTraitLocalizationSource(path=safe_path, text=row.text))
    if total_bytes > _MAX_TOTAL_SOURCE_BYTES:
        diagnostics.append(
            _SourceDiagnostic(
                code="mio.create.localization_total_size_limit_exceeded",
                message=("MIO localization sources exceed the " f"{_MAX_TOTAL_SOURCE_BYTES}-byte total limit."),
            )
        )
        return (), tuple(_sorted_source_diagnostics(diagnostics))

    documents: list[_MIOLocalizationDocument] = []
    seen: set[str] = set()
    for source in sorted(normalized, key=lambda row: row.path):
        portable = _portable_mio_key(source.path)
        if portable in seen:
            diagnostics.append(
                _SourceDiagnostic(
                    code="mio.create.localization_path_duplicate",
                    message=(f"MIO localization path {source.path!r} is repeated " "across supported filesystems."),
                    source_path=source.path,
                )
            )
            continue
        seen.add(portable)
        digest = text_sha256(source.text)
        documents.append(
            _MIOLocalizationDocument(
                path=source.path,
                text=source.text,
                sha256=digest,
                revision=f"sha256:{digest}",
            )
        )
    return (
        tuple(documents),
        tuple(_sorted_source_diagnostics(diagnostics)),
    )


def _mio_localization_keys(
    documents: Sequence[_MIOLocalizationDocument],
) -> tuple[
    dict[tuple[str, str], str],
    tuple[_SourceDiagnostic, ...],
]:
    keys: dict[tuple[str, str], str] = {}
    diagnostics: list[_SourceDiagnostic] = []
    for document in documents:
        for line_number, line in enumerate(
            document.text.splitlines(),
            start=1,
        ):
            visible = line.strip().lstrip("\ufeff")
            if not visible.startswith("["):
                continue
            match = _LOC_HEADER.fullmatch(visible)
            if match is None:
                diagnostics.append(
                    _SourceDiagnostic(
                        code="mio.create.localization_header_ambiguous",
                        message=(
                            f"MIO localization {document.path!r} line " f"{line_number} begins with '[' but is not one " "unambiguous [language.key] header."
                        ),
                        source_path=document.path,
                    )
                )
                continue
            key = (
                canonical_language(match.group(1)),
                match.group(2).strip(),
            )
            previous = keys.get(key)
            if previous is not None:
                diagnostics.append(
                    _SourceDiagnostic(
                        code="mio.create.localization_key_ambiguous",
                        message=(f"MIO localization key {key[1]!r} for " f"{key[0]!r} is declared more than once in " f"{previous!r} and {document.path!r}."),
                        source_path=document.path,
                    )
                )
                continue
            keys[key] = document.path
    return keys, tuple(_sorted_source_diagnostics(diagnostics))


def _mio_trait_creation_replacement(
    organization: _SourceOrganization,
    parent: _SourceTrait,
    creation: _TraitCreation,
) -> DiagramSourceReplacement:
    child_indent, insertion = block_child_insertion(
        organization.document,
        organization.entry,
        organization.block,
    )
    unit = indent_unit(
        organization.document,
        organization.block,
        child_indent,
    )
    field_indent = child_indent + unit
    nested_indent = field_indent + unit
    newline = source_newline(organization.document.text, insertion)
    parent_literal = _mio_reference_literal(parent)
    lines = (
        f"{child_indent}trait = {{",
        f"{field_indent}token = {creation.trait_id}",
        f"{field_indent}name = {creation.trait_id}",
        f"{field_indent}icon = {creation.icon}",
        f"{field_indent}position = {{",
        f"{nested_indent}x = {format_number(creation.x)}",
        f"{nested_indent}y = {format_number(creation.y)}",
        f"{field_indent}}}",
        f"{field_indent}relative_position_id = {parent_literal}",
        f"{field_indent}any_parent = {{",
        f"{nested_indent}{parent_literal}",
        f"{field_indent}}}",
        f"{field_indent}equipment_bonus = {{",
        (f"{nested_indent}{creation.bonus_key} = " f"{format_number(creation.bonus_value)}"),
        f"{field_indent}}}",
        f"{child_indent}}}",
    )
    return DiagramSourceReplacement(
        path=organization.document.path,
        start=insertion,
        end=insertion,
        expected="",
        replacement=newline.join(lines) + newline,
        operations=(("create_mio_trait:" f"{creation.organization_id}:{creation.trait_id}:definition"),),
        order_key=("create_mio_trait:" f"{creation.organization_id}:{creation.trait_id}:10:def"),
    )


def _mio_localization_creation_draft(
    document: _MIOLocalizationDocument,
    creation: _TraitCreation,
) -> tuple[dict[str, object], dict[str, object]]:
    newline = source_newline(document.text, len(document.text))
    visible = document.text.lstrip("\ufeff \t\r\n")
    if not visible or document.text.endswith(f"{newline}{newline}"):
        separator = ""
    elif document.text.endswith(newline):
        separator = newline
    else:
        separator = newline + newline
    replacement = f"{separator}[{creation.language}.{creation.trait_id}]" f"{newline}{creation.title}{newline}"
    text = document.text + replacement
    try:
        size = len(text.encode("utf-8"))
    except UnicodeEncodeError as error:
        raise UnsafeSourcePatch("Generated MIO localization is not valid UTF-8.") from error
    if size > _MAX_SOURCE_BYTES:
        raise UnsafeSourcePatch("Generated MIO localization exceeds the source-size limit.")
    digest = text_sha256(text)
    operation = "create_mio_trait:" f"{creation.organization_id}:{creation.trait_id}:localization"
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
            "path": document.path,
            "start": len(document.text),
            "end": len(document.text),
            "expected": "",
            "replacement": replacement,
            "operations": [operation],
        },
    )


def _mio_trait_creation_intent_row(
    creation: _TraitCreation,
) -> dict[str, object]:
    return {
        "organization_id": creation.organization_id,
        "parent_trait_id": creation.parent_trait_id,
        "trait_id": creation.trait_id,
        "title": creation.title,
        "icon": creation.icon,
        "x": creation.x,
        "y": creation.y,
        "bonus_key": creation.bonus_key,
        "bonus_value": creation.bonus_value,
        "language": creation.language,
        "source_path": creation.source_path,
        "source_revision": creation.source_revision,
    }


def _portable_mio_key(value: str) -> str:
    return unicodedata.normalize("NFC", value).casefold()


def _valid_mio_identifier(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value == value.strip() and is_utf8_text(value)


def _safe_mio_source_path(value: object) -> str | None:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "\\" in value
        or "\x00" in value
        or not is_utf8_text(value)
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        return None
    parts = value.split("/")
    if value.startswith("/") or any(part in {"", ".", ".."} for part in parts) or any(":" in part for part in parts):
        return None
    return value


def _safe_mio_localization_path(value: object) -> str | None:
    path = _safe_mio_source_path(value)
    return path if path is not None and path.endswith(".loc") else None


def _sorted_source_diagnostics(
    diagnostics: Sequence[_SourceDiagnostic],
) -> tuple[_SourceDiagnostic, ...]:
    return tuple(
        sorted(
            diagnostics,
            key=lambda row: (
                0 if row.severity == _ERROR else 1,
                row.source_path or "",
                row.organization_id or "",
                row.trait_id or "",
                row.code,
                row.message,
            ),
        )
    )
