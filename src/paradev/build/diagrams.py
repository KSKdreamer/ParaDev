"""Registered source-backed module-diagram provider contracts."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from math import isfinite
from typing import Literal, Protocol, runtime_checkable

from .loaders import CollectionSourceBundle, ModuleSourceBundle
from .records import Collection

_CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9_-]*$")
_SELECTION_VALUE_FIELD = "value"


@dataclass(frozen=True, slots=True)
class ModuleDiagramSelectionDefault:
    """Map one selected diagram-node value into an authoring-template field.

    The provider owns this declaration so desktop clients can prefill a
    reviewed create form without learning family-specific HoI4 semantics.
    The selected node remains source-backed and the ordinary scaffold dry plan
    remains the authority before any write.

    Args:
        field: Authoring-template value field to prefill.
        source: Selected projection-node field to read.
        offset: Optional finite numeric offset applied to numeric source values.
        template: Optional string projection containing exactly the
            ``{value}`` placeholder.
    """

    field: str
    source: str
    offset: int | float = 0
    template: str = "{value}"

    def __post_init__(self) -> None:
        """Validate the detached open-vocabulary mapping."""

        _require_capability_id(self.field, "selection default field")
        _require_capability_id(self.source, "selection default source")
        if (
            isinstance(self.offset, bool)
            or not isinstance(self.offset, (int, float))
            or not isfinite(self.offset)
        ):
            raise ValueError(
                "Module diagram selection default offset must be a finite number."
            )
        if not isinstance(self.template, str) or not self.template:
            raise ValueError(
                "Module diagram selection default template must be a non-empty string."
            )
        fields = re.findall(r"\{[A-Za-z_][^{}]*\}", self.template)
        if (
            fields != [f"{{{_SELECTION_VALUE_FIELD}}}"]
            or self.template.count("{value}") != 1
        ):
            raise ValueError(
                "Module diagram selection default template must contain exactly "
                "one plain '{value}' placeholder and no other fields."
            )

    def to_view(self) -> dict[str, object]:
        """Return a detached JSON-safe mapping."""

        return {
            "field": self.field,
            "source": self.source,
            **({"offset": self.offset} if self.offset else {}),
            **({"template": self.template} if self.template != "{value}" else {}),
        }


@dataclass(frozen=True, slots=True)
class ModuleDiagramTextSource:
    """One safely read project-owned UTF-8 source.

    Args:
        path: Stable project-relative POSIX path.
        text: Exact decoded source text without newline normalization.
    """

    path: str
    text: str


@runtime_checkable
class ModuleDiagramContext(Protocol):
    """Narrow project-resource reader available to diagram providers."""

    @property
    def family(self) -> str:
        """Return the active registered source-family id."""

    @property
    def profile(self) -> str:
        """Return the active build profile id."""

    @property
    def preferred_language(self) -> str:
        """Return the project's preferred authoring-language alias."""

    @property
    def registered_family(self) -> object:
        """Return the active registered family compiler."""

    @property
    def modules(self) -> tuple[ModuleSourceBundle, ...]:
        """Return normalized modules discovered for the active family."""

    def collections(self) -> tuple[Collection, ...]:
        """Return discovered collections for the active family."""

    def module_source_path(
        self,
        module: ModuleSourceBundle,
        relative_path: str,
    ) -> str:
        """Validate and return one module-owned project-relative path."""

    def read_module_text(
        self,
        module: ModuleSourceBundle,
        relative_path: str,
    ) -> ModuleDiagramTextSource:
        """Safely read one exact module-owned UTF-8 source."""

    def read_optional_module_text(
        self,
        module: ModuleSourceBundle,
        relative_path: str,
    ) -> ModuleDiagramTextSource | None:
        """Safely read one optional module-owned UTF-8 source."""

    def module_source_inventory(
        self,
        module: ModuleSourceBundle,
        *,
        maximum: int,
    ) -> tuple[str, ...]:
        """Return a bounded, symlink-free inventory below one module root."""

    def collection_source_path(
        self,
        collection: CollectionSourceBundle,
        relative_path: str,
    ) -> str:
        """Validate and return one collection-owned project-relative path."""


ModuleDiagramProjector = Callable[[ModuleDiagramContext], Mapping[str, object]]
ModuleDiagramPlanner = Callable[
    [
        ModuleDiagramContext,
        Sequence[Mapping[str, object]],
        Sequence[Mapping[str, object]],
    ],
    Mapping[str, object],
]


@dataclass(frozen=True, slots=True)
class ModuleDiagramModuleCreation:
    """Provider-owned request to scaffold one new diagram-backed module.

    The provider owns domain validation and template values. The Project SDK
    remains the sole owner of source-root selection, dry planning, plan-hash
    enforcement, atomic installation, Catalog refresh, and build acceptance.
    ``source_plan`` may carry one ordinary provider diagram plan whose existing
    source drafts must commit with the new standalone module.
    This lets project-local Entity extensions create diagram nodes without a
    family-specific SDK, REST, MCP, or desktop operation.
    """

    schema: str
    family_or_template: str
    object_id: str
    values: Mapping[str, object]
    intent: Mapping[str, object]
    source_plan: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        """Validate the transport-neutral scaffold request."""

        for value, label in (
            (self.schema, "schema"),
            (self.family_or_template, "family_or_template"),
            (self.object_id, "object_id"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Module diagram module creation {label} must be a non-empty string."
                )
        if not isinstance(self.values, Mapping):
            raise TypeError("Module diagram module creation values must be a mapping.")
        if not isinstance(self.intent, Mapping):
            raise TypeError("Module diagram module creation intent must be a mapping.")
        if self.source_plan is not None and not isinstance(self.source_plan, Mapping):
            raise TypeError(
                "Module diagram module creation source_plan must be a mapping or None."
            )
        if any(not isinstance(key, str) for key in (*self.values, *self.intent)):
            raise ValueError(
                "Module diagram module creation field names must be strings."
            )
        if self.source_plan is not None and any(
            not isinstance(key, str) for key in self.source_plan
        ):
            raise ValueError(
                "Module diagram module creation source-plan field names must be strings."
            )


ModuleDiagramNodePlan = Mapping[str, object] | ModuleDiagramModuleCreation
ModuleDiagramNodePlanner = Callable[
    [ModuleDiagramContext, Mapping[str, object]],
    ModuleDiagramNodePlan,
]


@dataclass(frozen=True, slots=True)
class ModuleDiagramNodeField:
    """One provider-owned field in a diagram-node creation form."""

    name: str
    label: str
    kind: str = "text"
    required: bool = False
    default: str | int | float | bool | None = None
    description: str = ""
    advanced: bool = False

    def __post_init__(self) -> None:
        """Validate the small transport-neutral form vocabulary."""

        _require_capability_id(self.name, "node field name")
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError(
                "Module diagram node field label must be a non-empty string."
            )
        if self.kind not in {"boolean", "number", "text", "textarea"}:
            raise ValueError(
                "Module diagram node field kind must be boolean, number, "
                "text, or textarea."
            )
        if type(self.required) is not bool or type(self.advanced) is not bool:
            raise ValueError(
                "Module diagram node field required and advanced flags "
                "must be booleans."
            )
        if not isinstance(self.description, str):
            raise TypeError("Module diagram node field description must be a string.")
        default = self.default
        if default is None:
            return
        if self.kind == "boolean" and type(default) is not bool:
            raise TypeError(
                "Boolean module diagram node fields require boolean defaults."
            )
        if self.kind == "number" and (
            isinstance(default, bool)
            or not isinstance(default, (int, float))
            or not isfinite(default)
        ):
            raise TypeError(
                "Number module diagram node fields require finite numeric defaults."
            )
        if self.kind in {"text", "textarea"} and not isinstance(default, str):
            raise TypeError("Text module diagram node fields require string defaults.")

    def to_view(self) -> dict[str, object]:
        """Return a detached JSON-safe field declaration."""

        return {
            "name": self.name,
            "label": self.label.strip(),
            "kind": self.kind,
            "required": self.required,
            **({"default": self.default} if self.default is not None else {}),
            **(
                {"description": self.description.strip()}
                if self.description.strip()
                else {}
            ),
            **({"advanced": True} if self.advanced else {}),
        }


@dataclass(frozen=True, slots=True)
class ModuleDiagramNodeAuthoring:
    """Provider-owned form and selection mapping for one graph node."""

    title: str
    description: str
    fields: tuple[ModuleDiagramNodeField, ...]
    selection_defaults: tuple[ModuleDiagramSelectionDefault, ...] = ()
    requires_selection: bool = True

    def __post_init__(self) -> None:
        """Validate the complete node-authoring declaration."""

        for value, label in (
            (self.title, "title"),
            (self.description, "description"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Module diagram node authoring {label} must be a non-empty string."
                )
        if not self.fields:
            raise ValueError(
                "Module diagram node authoring must declare at least one field."
            )
        if any(not isinstance(item, ModuleDiagramNodeField) for item in self.fields):
            raise TypeError(
                "Module diagram node authoring fields must contain "
                "ModuleDiagramNodeField values."
            )
        field_names = [item.name for item in self.fields]
        if len(set(field_names)) != len(field_names):
            raise ValueError(
                "Module diagram node authoring fields must have unique names."
            )
        if type(self.requires_selection) is not bool:
            raise TypeError(
                "Module diagram node authoring requires_selection must be a boolean."
            )
        if self.requires_selection and not self.selection_defaults:
            raise ValueError(
                "Module diagram node authoring must bind a reviewed selection."
            )
        if any(
            not isinstance(item, ModuleDiagramSelectionDefault)
            for item in self.selection_defaults
        ):
            raise TypeError(
                "Module diagram node authoring selection_defaults must contain "
                "ModuleDiagramSelectionDefault values."
            )
        targets = [item.field for item in self.selection_defaults]
        if len(set(targets)) != len(targets):
            raise ValueError(
                "Module diagram node authoring selection defaults must have "
                "unique target fields."
            )

    def to_view(self) -> dict[str, object]:
        """Return a detached JSON-safe node-authoring capability."""

        return {
            "title": self.title.strip(),
            "description": self.description.strip(),
            "fields": [item.to_view() for item in self.fields],
            "selection_defaults": [item.to_view() for item in self.selection_defaults],
            "requires_selection": self.requires_selection,
        }


@dataclass(frozen=True, slots=True)
class ModuleDiagramRelationship:
    """One provider-owned relationship editing action.

    The declaration is deliberately transport-neutral.  Providers keep all
    source parsing and planning semantics while desktop clients learn only
    how a reviewed edge should be presented and which endpoint owns it.

    Args:
        kind: Open provider intent kind emitted by the diagram edit planner.
        label: Reader-facing action label.
        visual_kind: Shared canvas edge role.
        selected_endpoint: Whether the node being edited is the edge source
            or target.
        owner_endpoint: Endpoint whose reviewed source revision owns a newly
            declared edge.
        symmetric: Whether the endpoints form one unordered relationship.
        cardinality: Whether the selected node may have one or many edges of
            this kind.
    """

    kind: str
    label: str
    visual_kind: str
    selected_endpoint: str
    owner_endpoint: str
    symmetric: bool = False
    cardinality: str = "many"

    def __post_init__(self) -> None:
        """Validate the small shared relationship vocabulary."""

        _require_capability_id(self.kind, "relationship kind")
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError(
                "Module diagram relationship label must be a non-empty string."
            )
        if self.visual_kind not in {"dependency", "path", "reference", "tree"}:
            raise ValueError(
                "Module diagram relationship visual_kind must be 'dependency', "
                "'path', 'reference', or 'tree'."
            )
        if self.selected_endpoint not in {"source", "target"}:
            raise ValueError(
                "Module diagram relationship selected_endpoint must be 'source' or 'target'."
            )
        if self.owner_endpoint not in {"source", "target"}:
            raise ValueError(
                "Module diagram relationship owner_endpoint must be 'source' or 'target'."
            )
        if type(self.symmetric) is not bool:
            raise ValueError("Module diagram relationship symmetric must be a boolean.")
        if self.cardinality not in {"many", "one"}:
            raise ValueError(
                "Module diagram relationship cardinality must be 'many' or 'one'."
            )

    def to_view(self) -> dict[str, object]:
        """Return a detached JSON-safe relationship action."""

        return {
            "kind": self.kind,
            "label": self.label.strip(),
            "visual_kind": self.visual_kind,
            "selected_endpoint": self.selected_endpoint,
            "owner_endpoint": self.owner_endpoint,
            "symmetric": self.symmetric,
            "cardinality": self.cardinality,
        }


@dataclass(frozen=True, slots=True)
class ModuleDiagramProvider:
    """One registry-owned module-diagram capability.

    A provider may name several compatible source families in priority order.
    The first registered family becomes its active owner. This supports a
    profile default such as ``focus_tree`` while allowing a project extension
    to replace it with a modular ``focus`` family without SDK dispatch code.

    Args:
        identifier: Canonical public diagram selector.
        families: Compatible registered source families in priority order.
        renderer: Desktop renderer capability id.
        title: Reader-facing fallback title.
        project: Pure projection entry point using the guarded context.
        aliases: Optional public selector aliases.
        plan: Optional guarded edit planner. Its presence makes the provider
            editable.
        node_plan: Optional guarded node-creation planner.
        node_authoring: Form and selected-node mapping owned by ``node_plan``.
        authoring_kind: Optional create action supported by the desktop.
        scope_authoring_kind: Optional create action for a new diagram scope,
            such as a Registry-backed collection that owns one tree.
        selection_defaults: Provider-owned mappings from the reviewed selected
            node into authoring-template values.
        relationships: Provider-owned relationship editing actions.
        initial_scope: Scope inherited when a client opens the diagram.
            Supported values are ``"selected-entity"``, which may seed the
            diagram from the active source entity, and ``"project"``, which
            starts from the provider's complete project projection.
        show_when_source_hidden: Whether a hidden source family still belongs
            in workspace navigation because the diagram is user-facing.
        replaces_registered_provider: Explicit project-extension override
            marker.
    """

    identifier: str
    families: tuple[str, ...]
    renderer: str
    title: str
    project: ModuleDiagramProjector
    aliases: tuple[str, ...] = ()
    plan: ModuleDiagramPlanner | None = None
    node_plan: ModuleDiagramNodePlanner | None = None
    node_authoring: ModuleDiagramNodeAuthoring | None = None
    authoring_kind: str | None = None
    scope_authoring_kind: str | None = None
    selection_defaults: tuple[ModuleDiagramSelectionDefault, ...] = ()
    relationships: tuple[ModuleDiagramRelationship, ...] = ()
    initial_scope: Literal["project", "selected-entity"] = "selected-entity"
    show_when_source_hidden: bool = False
    replaces_registered_provider: bool = False

    def __post_init__(self) -> None:
        """Validate the provider's stable open-capability vocabulary."""

        _require_capability_id(self.identifier, "identifier")
        _require_capability_id(self.renderer, "renderer")
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError(
                "Module diagram provider title must be a non-empty string."
            )
        if not callable(self.project):
            raise TypeError(
                f"Module diagram provider {self.identifier!r} project must be callable."
            )
        if self.plan is not None and not callable(self.plan):
            raise ValueError(
                f"Module diagram provider {self.identifier!r} plan must be callable."
            )
        if self.node_plan is not None and not callable(self.node_plan):
            raise ValueError(
                f"Module diagram provider {self.identifier!r} node_plan "
                "must be callable."
            )
        if type(self.show_when_source_hidden) is not bool:
            raise ValueError(
                f"Module diagram provider {self.identifier!r} "
                "show_when_source_hidden must be a boolean."
            )
        if type(self.replaces_registered_provider) is not bool:
            raise ValueError(
                f"Module diagram provider {self.identifier!r} "
                "replaces_registered_provider must be a boolean."
            )
        if self.initial_scope not in {"project", "selected-entity"}:
            raise ValueError(
                f"Module diagram provider {self.identifier!r} initial_scope "
                "must be 'project' or 'selected-entity'."
            )
        _require_unique_ids(self.families, "families", provider=self.identifier)
        _require_unique_ids(self.aliases, "aliases", provider=self.identifier)
        if self.identifier in self.aliases:
            raise ValueError(
                f"Module diagram provider {self.identifier!r} aliases cannot repeat its identifier."
            )
        if self.authoring_kind is not None:
            _require_capability_id(self.authoring_kind, "authoring_kind")
        if self.scope_authoring_kind is not None:
            _require_capability_id(
                self.scope_authoring_kind,
                "scope_authoring_kind",
            )
        if (self.node_plan is None) != (self.node_authoring is None):
            raise ValueError(
                f"Module diagram provider {self.identifier!r} node_plan and "
                "node_authoring must be declared together."
            )
        if self.node_authoring is not None:
            if not isinstance(
                self.node_authoring,
                ModuleDiagramNodeAuthoring,
            ):
                raise TypeError(
                    f"Module diagram provider {self.identifier!r} "
                    "node_authoring must be a ModuleDiagramNodeAuthoring."
                )
            if self.authoring_kind != "diagram-node":
                raise ValueError(
                    f"Module diagram provider {self.identifier!r} node "
                    "authoring requires authoring_kind='diagram-node'."
                )
        elif self.authoring_kind == "diagram-node":
            raise ValueError(
                f"Module diagram provider {self.identifier!r} "
                "authoring_kind='diagram-node' requires node authoring."
            )
        if self.selection_defaults and self.authoring_kind is None:
            raise ValueError(
                f"Module diagram provider {self.identifier!r} selection defaults "
                "require an authoring_kind."
            )
        if any(
            not isinstance(item, ModuleDiagramSelectionDefault)
            for item in self.selection_defaults
        ):
            raise TypeError(
                f"Module diagram provider {self.identifier!r} selection_defaults "
                "must contain ModuleDiagramSelectionDefault values."
            )
        fields = [item.field for item in self.selection_defaults]
        if len(set(fields)) != len(fields):
            raise ValueError(
                f"Module diagram provider {self.identifier!r} selection_defaults "
                "must not target the same field more than once."
            )
        if self.relationships and self.plan is None:
            raise ValueError(
                f"Module diagram provider {self.identifier!r} relationships "
                "require an edit planner."
            )
        if any(
            not isinstance(item, ModuleDiagramRelationship)
            for item in self.relationships
        ):
            raise TypeError(
                f"Module diagram provider {self.identifier!r} relationships "
                "must contain ModuleDiagramRelationship values."
            )
        relationship_kinds = [item.kind for item in self.relationships]
        if len(set(relationship_kinds)) != len(relationship_kinds):
            raise ValueError(
                f"Module diagram provider {self.identifier!r} relationships "
                "must have unique kinds."
            )

    @property
    def editable(self) -> bool:
        """Return whether the provider owns a guarded source-edit planner."""

        return self.plan is not None

    @property
    def selectors(self) -> tuple[str, ...]:
        """Return the canonical selector followed by deterministic aliases."""

        return (self.identifier, *self.aliases)

    def to_view(self) -> dict[str, object]:
        """Return a detached JSON-safe capability view."""

        payload: dict[str, object] = {
            "id": self.identifier,
            "aliases": list(self.aliases),
            "renderer": self.renderer,
            "title": self.title.strip(),
            "editable": self.editable,
        }
        if self.authoring_kind is not None:
            payload["authoring_kind"] = self.authoring_kind
        if self.scope_authoring_kind is not None:
            payload["scope_authoring_kind"] = self.scope_authoring_kind
        if self.selection_defaults:
            payload["selection_defaults"] = [
                item.to_view() for item in self.selection_defaults
            ]
        if self.node_authoring is not None:
            payload["node_authoring"] = self.node_authoring.to_view()
        if self.relationships:
            payload["relationships"] = [item.to_view() for item in self.relationships]
        if self.initial_scope != "selected-entity":
            payload["initial_scope"] = self.initial_scope
        if self.show_when_source_hidden:
            payload["show_when_source_hidden"] = True
        return payload


@dataclass(frozen=True, slots=True)
class ResolvedModuleDiagramProvider:
    """One provider resolved to its active registered source family."""

    family: str
    provider: ModuleDiagramProvider


def _require_capability_id(value: object, field: str) -> str:
    if not isinstance(value, str) or _CAPABILITY_ID.fullmatch(value) is None:
        raise ValueError(
            f"Module diagram provider {field} must start with a lowercase "
            "letter and contain only lowercase letters, numbers, '_' or '-'."
        )
    return value


def _require_unique_ids(
    values: object,
    field: str,
    *,
    provider: str,
) -> tuple[str, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise TypeError(
            f"Module diagram provider {provider!r} {field} must be a list of capability ids."
        )
    normalized: list[str] = []
    for value in values:
        normalized.append(_require_capability_id(value, field))
    if not normalized and field == "families":
        raise ValueError(
            f"Module diagram provider {provider!r} families must name at least one source family."
        )
    if len(set(normalized)) != len(normalized):
        raise ValueError(
            f"Module diagram provider {provider!r} {field} must not contain duplicate ids."
        )
    return tuple(normalized)


__all__ = [
    "ModuleDiagramContext",
    "ModuleDiagramNodeAuthoring",
    "ModuleDiagramNodeField",
    "ModuleDiagramNodePlanner",
    "ModuleDiagramPlanner",
    "ModuleDiagramProjector",
    "ModuleDiagramProvider",
    "ModuleDiagramRelationship",
    "ModuleDiagramSelectionDefault",
    "ModuleDiagramTextSource",
    "ResolvedModuleDiagramProvider",
]
