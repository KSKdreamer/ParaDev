"""Registries for build families, diagrams, writers, and postprocessors."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from string import Formatter
from typing import Any

from paradev._api_table import append_index_entry

from .diagrams import ModuleDiagramProvider, ResolvedModuleDiagramProvider
from .loaders import METADATA_KEYS
from .presentation import FamilyPresentation, normalize_family_selector
from .slots import Slot, slot_match_escapes_root

_FORMATTER = Formatter()
_SLOT_AUTHORING_FIELDS = frozenset({"extension", "filename", "object_id", "stem"})
_MODULE_TEMPLATE_FIELDS = frozenset(
    {
        "family",
        "module_id",
        "object_id",
        "source_path",
        "source_name",
        "source_stem",
        "source_suffix",
        "source_slot",
        "slot",
        "language",
        "language_folder",
    }
)
_COLLECTION_TEMPLATE_FIELDS = frozenset(
    {
        "family",
        "collection_id",
        "object_id",
        "source_path",
        "source_name",
        "source_stem",
        "source_suffix",
        "source_slot",
        "slot",
        "language",
        "language_folder",
    }
)
_COLLECTION_MEMBER_TEMPLATE_FIELDS = _MODULE_TEMPLATE_FIELDS & _COLLECTION_TEMPLATE_FIELDS
_SPRITE_NAME_TEMPLATE_FIELDS = _MODULE_TEMPLATE_FIELDS - frozenset({"language", "language_folder"})
_SPRITE_GFX_TEMPLATE_FIELDS = _SPRITE_NAME_TEMPLATE_FIELDS | frozenset({"project_id"})
_REQUIRED_LOC_TEMPLATE_FIELDS = frozenset({"family", "module_id", "collection_id", "object_id"})
_SIMPLE_TEMPLATE_FIELDS = {
    "pdx": _MODULE_TEMPLATE_FIELDS,
    "loc": _MODULE_TEMPLATE_FIELDS,
    "copy": _MODULE_TEMPLATE_FIELDS,
    "sprite_gfx": _SPRITE_GFX_TEMPLATE_FIELDS,
    "sprite_name": _SPRITE_NAME_TEMPLATE_FIELDS,
}
_COLLECTION_SOURCE_TEMPLATE_FIELDS = {
    "pdx": _COLLECTION_TEMPLATE_FIELDS,
    "view": _COLLECTION_TEMPLATE_FIELDS,
    "module_pdx": _MODULE_TEMPLATE_FIELDS,
    "loc": _COLLECTION_MEMBER_TEMPLATE_FIELDS,
    "copy": _COLLECTION_MEMBER_TEMPLATE_FIELDS,
}
_ROUTED_TEMPLATE_FIELDS = {
    "pdx": _MODULE_TEMPLATE_FIELDS,
    "loc": _MODULE_TEMPLATE_FIELDS,
    "copy": _MODULE_TEMPLATE_FIELDS,
}
_TEMPLATE_ATTRS = (
    ("pdx", "pdx_path_template"),
    ("view", "view_path_template"),
    ("module_pdx", "module_pdx_path_template"),
    ("loc", "loc_path_template"),
    ("copy", "copy_path_template"),
    ("sprite_gfx", "sprite_gfx_path_template"),
    ("sprite_name", "sprite_name_template"),
)
_OUTPUT_TEMPLATE_KEYS = tuple(key for key, _attr in _TEMPLATE_ATTRS if key != "sprite_name")
_OUTPUT_ARTIFACT_TYPES = {
    "pdx": "pdx",
    "view": "view",
    "module_pdx": "pdx",
    "loc": "loc",
    "copy": "copy",
    "sprite_gfx": "sprite_gfx",
}
_GENERATED_OUTPUT_FIELDS = frozenset(
    {
        "artifact_type",
        "description",
        "owner_kinds",
        "route",
        "source_slots",
        "target_root",
    }
)
_OUTPUT_OWNER_KINDS = frozenset({"collection", "module", "project"})
_OUTPUT_TARGET_ROOTS = frozenset({"build", "output"})
_UNKNOWN_METADATA_KEY_POLICY = {
    "code": "metadata.unknown_key",
    "loose_severity": "warning",
    "strict_severity": "error",
}


@dataclass(slots=True)
class BuildRegistry:
    """Registry for build families, diagram providers, and output hooks."""

    _families: dict[str, Any] = field(default_factory=dict)
    _presentations: dict[str, FamilyPresentation] = field(default_factory=dict)
    _publication_replacements: dict[str, tuple[str, ...]] = field(default_factory=dict)
    _diagram_providers: dict[str, ModuleDiagramProvider] = field(default_factory=dict)
    _writers: dict[str, Any] = field(default_factory=dict)
    _postprocessors: dict[str, Any] = field(default_factory=dict)
    source_slots: Sequence[Slot] = ()
    collection_source_slots: Sequence[Slot] = ()

    def __post_init__(self) -> None:
        """Validate profile-level default source slots."""

        _validate_registry_slots("source_slots", self.source_slots)
        _validate_registry_slots("collection_source_slots", self.collection_source_slots)

    def add(self, item: Any) -> "BuildRegistry":
        """Register a family, diagram provider, writer, or postprocessor.

        Args:
            item: A :class:`ModuleDiagramProvider` or object with a `family`,
                `artifact_type`, or `postprocessor_id` attribute.

        Returns:
            This registry, for fluent setup.

        Raises:
            ValueError: If the object cannot be registered or duplicates an existing key.
        """

        if isinstance(item, ModuleDiagramProvider):
            self.add_diagram_provider(item)
            return self
        if getattr(item, "family", None):
            self.add_family(item)
            return self
        if getattr(item, "artifact_type", None):
            self.add_writer(item)
            return self
        if getattr(item, "postprocessor_id", None):
            self.add_postprocessor(item)
            return self
        raise ValueError("Build registry items must be a ModuleDiagramProvider or define " "'family', 'artifact_type', or 'postprocessor_id'.")

    def add_family(
        self,
        family: Any,
        *,
        presentation: FamilyPresentation | None = None,
    ) -> "BuildRegistry":
        """Register one module family."""

        key = str(getattr(family, "family", "")).strip()
        if not key:
            raise ValueError("Build family must define a non-empty 'family'.")
        if key in self._families:
            raise ValueError(f"Build family {key!r} is already registered.")
        _validate_family_contract(key, family)
        family_presentation = _family_presentation(
            key,
            family,
            presentation=presentation,
        )
        self._validate_presentation_selectors(key, family_presentation)
        claimed_by = {
            replaced_family: active_key for active_key, replaced_families in self._publication_replacements.items() for replaced_family in replaced_families
        }
        if key in claimed_by:
            raise ValueError(f"Build family {key!r} is replaced for publication by active " f"family {claimed_by[key]!r} and cannot also be registered.")
        self._families[key] = family
        self._presentations[key] = family_presentation
        try:
            self._validate_active_diagram_bindings()
        except Exception:
            self._families.pop(key, None)
            self._presentations.pop(key, None)
            raise
        return self

    def replace_family(
        self,
        family: Any,
        *,
        presentation: FamilyPresentation | None = None,
    ) -> "BuildRegistry":
        """Replace one registered family through an explicit extension override.

        Project extensions use this operation only after declaring
        ``replaces_registered_family``. Validation stays atomic: a failed
        replacement restores the previous family.
        """

        key = str(getattr(family, "family", "")).strip()
        if not key:
            raise ValueError("Build family must define a non-empty 'family'.")
        if key not in self._families:
            raise ValueError(f"Build family {key!r} is not registered and cannot be replaced.")
        previous = self._families.pop(key)
        previous_presentation = self._presentations.pop(key)
        try:
            self.add_family(family, presentation=presentation)
        except Exception:
            self._families[key] = previous
            self._presentations[key] = previous_presentation
            raise
        return self

    def add_diagram_provider(
        self,
        provider: ModuleDiagramProvider,
    ) -> "BuildRegistry":
        """Register one source-backed module-diagram provider."""

        if not isinstance(provider, ModuleDiagramProvider):
            raise TypeError("Build diagram providers must use ModuleDiagramProvider.")
        key = provider.identifier
        if key in self._diagram_providers:
            raise ValueError(f"Module diagram provider {key!r} is already registered.")
        claimed_selectors = {selector: active.identifier for active in self._diagram_providers.values() for selector in active.selectors}
        conflicts = sorted(selector for selector in provider.selectors if selector in claimed_selectors)
        if conflicts:
            selector = conflicts[0]
            raise ValueError(f"Module diagram selector {selector!r} is already claimed by " f"provider {claimed_selectors[selector]!r}.")
        self._diagram_providers[key] = provider
        try:
            self._validate_active_diagram_bindings()
        except Exception:
            self._diagram_providers.pop(key, None)
            raise
        return self

    def replace_diagram_provider(
        self,
        provider: ModuleDiagramProvider,
    ) -> "BuildRegistry":
        """Atomically replace one explicitly overridden diagram provider."""

        if not isinstance(provider, ModuleDiagramProvider):
            raise TypeError("Build diagram providers must use ModuleDiagramProvider.")
        key = provider.identifier
        if key not in self._diagram_providers:
            raise ValueError(f"Module diagram provider {key!r} is not registered and " "cannot be replaced.")
        previous = self._diagram_providers.pop(key)
        try:
            self.add_diagram_provider(provider)
        except Exception:
            self._diagram_providers[key] = previous
            raise
        return self

    def add_writer(self, writer: Any) -> "BuildRegistry":
        """Register one artifact writer."""

        key = str(getattr(writer, "artifact_type", "")).strip()
        if not key:
            raise ValueError("Artifact writer must define a non-empty 'artifact_type'.")
        if key in self._writers:
            raise ValueError(f"Artifact writer {key!r} is already registered.")
        self._writers[key] = writer
        return self

    def add_postprocessor(self, postprocessor: Any) -> "BuildRegistry":
        """Register one whole-plan artifact postprocessor.

        Args:
            postprocessor: Object with a unique ``postprocessor_id`` and a
                callable ``process(ctx, artifacts)`` method.

        Returns:
            This registry, for fluent setup.

        Raises:
            ValueError: If the postprocessor contract is invalid or its id is
                already registered.
        """

        key = str(getattr(postprocessor, "postprocessor_id", "")).strip()
        if not key:
            raise ValueError("Build postprocessor must define a non-empty 'postprocessor_id'.")
        if key in self._postprocessors:
            raise ValueError(f"Build postprocessor {key!r} is already registered.")
        if not callable(getattr(postprocessor, "process", None)):
            raise ValueError(f"Build postprocessor {key!r} must define process(ctx, artifacts).")
        self._postprocessors[key] = postprocessor
        return self

    def family(self, key: str) -> Any:
        """Return a registered family by key."""

        try:
            return self._families[key]
        except KeyError as error:
            raise ValueError(f"Build family {key!r} is not registered.") from error

    def resolve_family(self, selector: str) -> str:
        """Resolve a family key, presentation id, or declared alias."""

        normalized = normalize_family_selector(selector)
        if not normalized:
            raise ValueError("Build family selector must be a non-empty string.")
        matches = [family for family, presentation in self._presentations.items() if normalized in presentation.selectors(family)]
        if not matches:
            raise ValueError(f"Build family selector {selector!r} is not registered.")
        return matches[0]

    def presentation_for(self, family: str) -> FamilyPresentation:
        """Return the presentation capability owned by one registered family."""

        key = self.resolve_family(family)
        return self._presentations[key]

    def presentation_views_by_family(self) -> dict[str, dict[str, object]]:
        """Return presentation capabilities keyed by compiler family."""

        return {family: self._presentations[family].to_view() for family in sorted(self._presentations)}

    def add_publication_replacements(
        self,
        family: str,
        replaced_families: Sequence[str],
    ) -> "BuildRegistry":
        """Register descriptor-owned publication migration state.

        Args:
            family: Active successor family.
            replaced_families: Previous family identities whose tracked
                publication rows may be reconciled by a family-wide build.

        Returns:
            This registry, for fluent extension activation.

        Raises:
            ValueError: If the family is unknown, the declaration is malformed,
                names an active family, or conflicts with another successor.
        """

        successor = str(family).strip()
        self.family(successor)
        replacements = _publication_replacement_values(
            successor,
            replaced_families,
        )
        if not replacements:
            return self
        if successor in self._publication_replacements:
            raise ValueError(f"Build family {successor!r} already declares publication " "replacement state.")
        active_conflicts = sorted(set(replacements).intersection(self._families))
        if active_conflicts:
            raise ValueError(f"Build family {successor!r} publication replacements cannot " f"name active families: {', '.join(active_conflicts)}.")
        claimed_by = {replaced: active for active, values in self._publication_replacements.items() for replaced in values}
        ambiguous = sorted(replaced for replaced in replacements if replaced in claimed_by)
        if ambiguous:
            replaced = ambiguous[0]
            raise ValueError(f"Publication family {replaced!r} is already replaced by " f"active family {claimed_by[replaced]!r}.")
        self._publication_replacements[successor] = replacements
        return self

    def publication_replacements_for(self, family: str) -> tuple[str, ...]:
        """Return descriptor-owned publication replacements for a family.

        Args:
            family: Active registered successor family.

        Returns:
            Sorted previous family identities whose tracked publication rows
            may be reconciled by a family-wide build.

        Raises:
            ValueError: If the active family is unknown.
        """

        successor = str(family).strip()
        self.family(successor)
        return self._publication_replacements.get(successor, ())

    def writer(self, key: str) -> Any:
        """Return a registered artifact writer by key."""

        try:
            return self._writers[key]
        except KeyError as error:
            raise ValueError(f"Artifact writer {key!r} is not registered.") from error

    @property
    def families(self) -> tuple[Any, ...]:
        """Return registered families in deterministic key order."""

        return tuple(self._families[key] for key in sorted(self._families))

    @property
    def diagram_providers(self) -> tuple[ModuleDiagramProvider, ...]:
        """Return registered diagram providers in deterministic id order."""

        return tuple(self._diagram_providers[key] for key in sorted(self._diagram_providers))

    def diagram_provider(
        self,
        selector: str,
        *,
        editable: bool = False,
    ) -> ResolvedModuleDiagramProvider:
        """Resolve a public selector to one active registered provider."""

        if not isinstance(selector, str) or not selector.strip():
            raise ValueError("Module diagram family must be a non-empty string.")
        normalized = selector.strip().casefold()
        provider = next(
            (candidate for candidate in self.diagram_providers if normalized in candidate.selectors),
            None,
        )
        if provider is None:
            supported = ", ".join(repr(candidate.identifier) for candidate in self._active_diagram_providers())
            suffix = f" Supported providers are {supported}." if supported else ""
            raise ValueError(f"Module diagram family {selector!r} has no registered " f"source provider.{suffix}")
        family = self._active_diagram_family(provider)
        if family is None:
            raise ValueError(f"Module diagram provider {provider.identifier!r} has no " "compatible registered source family.")
        if editable and not provider.editable:
            raise ValueError(f"Module diagram family {selector!r} has no guarded " "source-edit provider.")
        return ResolvedModuleDiagramProvider(
            family=family,
            provider=provider,
        )

    def diagram_views_by_family(self) -> dict[str, dict[str, object]]:
        """Return active JSON-safe diagram capabilities by source family."""

        views: dict[str, dict[str, object]] = {}
        for provider in self._active_diagram_providers():
            family = self._active_diagram_family(provider)
            if family is not None:
                views[family] = provider.to_view()
        return views

    @property
    def writers(self) -> tuple[Any, ...]:
        """Return registered writers in deterministic key order."""

        return tuple(self._writers[key] for key in sorted(self._writers))

    @property
    def postprocessors(self) -> tuple[Any, ...]:
        """Return registered artifact postprocessors in deterministic order."""

        return tuple(self._postprocessors[key] for key in sorted(self._postprocessors))

    def source_slots_for(self, family: str) -> tuple[Slot, ...]:
        """Return source slots for a family, falling back to registry defaults."""

        registered = self._families.get(family)
        if _family_kind(registered) == "project_metadata":
            return ()
        family_slots = getattr(registered, "source_slots", ()) if registered is not None else ()
        return tuple(family_slots or self.source_slots)

    def source_slots_by_family(self) -> dict[str, tuple[Slot, ...]]:
        """Return source slots keyed by registered family."""

        slots_by_family: dict[str, tuple[Slot, ...]] = {}
        for family in self.families:
            key = str(getattr(family, "family"))
            slots = self.source_slots_for(key)
            if slots:
                slots_by_family[key] = slots
        return slots_by_family

    def collection_source_slots_for(self, family: str) -> tuple[Slot, ...]:
        """Return collection descriptor slots for a family, falling back to registry defaults."""

        registered = self._families.get(family)
        if _family_kind(registered) == "project_metadata":
            return ()
        family_slots = getattr(registered, "collection_source_slots", ()) if registered is not None else ()
        return tuple(family_slots or self.collection_source_slots)

    def collection_source_slots_by_family(self) -> dict[str, tuple[Slot, ...]]:
        """Return collection descriptor slots keyed by registered family."""

        slots_by_family: dict[str, tuple[Slot, ...]] = {}
        for family in self.families:
            key = str(getattr(family, "family"))
            slots = self.collection_source_slots_for(key)
            if slots:
                slots_by_family[key] = slots
        return slots_by_family

    def metadata_keys_for(self, family: str) -> tuple[str, ...]:
        """Return family-specific top-level metadata keys."""

        registered = self._families.get(family)
        return _strings(getattr(registered, "metadata_keys", ())) if registered is not None else ()

    def metadata_keys_by_family(self) -> dict[str, tuple[str, ...]]:
        """Return family-specific metadata keys keyed by registered family."""

        metadata_keys: dict[str, tuple[str, ...]] = {}
        for family in self.families:
            key = str(getattr(family, "family"))
            keys = self.metadata_keys_for(key)
            if keys:
                metadata_keys[key] = keys
        return metadata_keys

    def default_assets_for(self, family: str) -> dict[str, dict[str, object]]:
        """Return normalized class-level default assets for a family."""

        registered = self._families.get(family)
        return _default_assets(registered) if registered is not None else {}

    def visible_for(self, family: str) -> bool:
        """Return whether a registered family belongs in discovery navigation."""

        registered = self._families.get(family)
        if registered is None:
            return True
        visible = getattr(registered, "visible", True)
        if not isinstance(visible, bool):
            raise ValueError(f"Build family {family!r} visible must be a boolean.")
        return visible

    def visibility_by_family(self) -> dict[str, bool]:
        """Return discovery visibility keyed by registered family id."""

        return {str(getattr(family, "family")): self.visible_for(str(getattr(family, "family"))) for family in self.families}

    def default_assets_by_family(self) -> dict[str, dict[str, dict[str, object]]]:
        """Return default assets keyed by registered family."""

        assets: dict[str, dict[str, dict[str, object]]] = {}
        for family in self.families:
            key = str(getattr(family, "family"))
            family_assets = self.default_assets_for(key)
            if family_assets:
                assets[key] = family_assets
        return assets

    def identity_rewriter_for(self, family: str) -> Any | None:
        """Return the module-identity rewriter owned by one family.

        Args:
            family (str): Registered compiler family identifier.

        Returns:
            Any | None: Validated identity rewriter, or `None` when the family
            intentionally supports literal copies only.

        Raises:
            ValueError: If the family is not registered.
        """

        registered = self.family(family)
        return getattr(registered, "identity_rewriter", None)

    def to_view(
        self,
        *,
        family: str | None = None,
        kind: str | None = None,
        source_slot: str | None = None,
        collection_source_slot: str | None = None,
        sprite_slot: str | None = None,
        route: str | None = None,
        artifact_type: str | None = None,
    ) -> dict[str, Any]:
        """Return a JSON-safe registry capability view."""

        diagram_by_family = self.diagram_views_by_family()
        families = tuple(
            _family_view(
                registered_family,
                presentation=self.presentation_for(str(getattr(registered_family, "family"))).to_view(),
                source_slots=[_slot_view(slot) for slot in self.source_slots_for(str(getattr(registered_family, "family")))],
                collection_source_slots=[_slot_view(slot) for slot in self.collection_source_slots_for(str(getattr(registered_family, "family")))],
                diagram=diagram_by_family.get(str(getattr(registered_family, "family"))),
            )
            for registered_family in self.families
        )
        families = tuple(
            row
            for row in families
            if _family_row_matches(
                row,
                family=family,
                kind=kind,
                source_slot=source_slot,
                collection_source_slot=collection_source_slot,
                sprite_slot=sprite_slot,
                route=route,
                artifact_type=artifact_type,
            )
        )
        writers = tuple(
            {
                "artifact_type": str(getattr(writer, "artifact_type")),
                "kind": type(writer).__name__,
            }
            for writer in self.writers
        )
        writers = tuple(row for row in writers if _matches(row.get("artifact_type"), artifact_type))
        postprocessors = tuple(
            {
                "postprocessor_id": str(getattr(postprocessor, "postprocessor_id")),
                "kind": type(postprocessor).__name__,
            }
            for postprocessor in self.postprocessors
        )
        return {
            "families": list(families),
            "writers": list(writers),
            "postprocessors": list(postprocessors),
            "index": _registry_index(families, writers, postprocessors),
        }

    def _active_diagram_family(
        self,
        provider: ModuleDiagramProvider,
    ) -> str | None:
        return next(
            (family for family in provider.families if family in self._families),
            None,
        )

    def _active_diagram_providers(self) -> tuple[ModuleDiagramProvider, ...]:
        return tuple(provider for provider in self.diagram_providers if self._active_diagram_family(provider) is not None)

    def _validate_active_diagram_bindings(self) -> None:
        owners: dict[str, str] = {}
        for provider in self._active_diagram_providers():
            family = self._active_diagram_family(provider)
            if family is None:
                continue
            previous = owners.get(family)
            if previous is not None:
                raise ValueError(f"Build family {family!r} is claimed by module diagram " f"providers {previous!r} and {provider.identifier!r}.")
            owners[family] = provider.identifier

    def _validate_presentation_selectors(
        self,
        family: str,
        presentation: FamilyPresentation,
    ) -> None:
        """Reject aliases that would make family resolution ambiguous."""

        candidate = presentation.selectors(family)
        for active_family, active_presentation in self._presentations.items():
            overlap = sorted(candidate.intersection(active_presentation.selectors(active_family)))
            if overlap:
                raise ValueError(f"Build family {family!r} presentation selector " f"{overlap[0]!r} is already claimed by family " f"{active_family!r}.")


def _family_row_matches(
    row: Mapping[str, Any],
    *,
    family: str | None,
    kind: str | None,
    source_slot: str | None,
    collection_source_slot: str | None,
    sprite_slot: str | None,
    route: str | None,
    artifact_type: str | None,
) -> bool:
    return (
        _matches(row.get("family"), family)
        and _matches(row.get("kind"), kind)
        and _slot_contracts_match(row.get("source_slots"), source_slot)
        and _slot_contracts_match(row.get("collection_source_slots"), collection_source_slot)
        and _strings_match(row.get("sprite_slots"), sprite_slot)
        and _mapping_key_matches(row.get("routes"), route)
        and _output_contracts_match(row.get("outputs"), artifact_type)
    )


def _matches(value: object, expected: str | None) -> bool:
    return expected is None or value == expected


def _slot_contracts_match(slots: object, expected: str | None) -> bool:
    if expected is None:
        return True
    for slot in slots if isinstance(slots, list) else ():
        if isinstance(slot, Mapping) and slot.get("name") == expected:
            return True
    return False


def _strings_match(values: object, expected: str | None) -> bool:
    if expected is None:
        return True
    return expected in values if isinstance(values, list) else False


def _mapping_key_matches(value: object, expected: str | None) -> bool:
    if expected is None:
        return True
    return expected in value if isinstance(value, Mapping) else False


def _output_contracts_match(outputs: object, expected: str | None) -> bool:
    if expected is None:
        return True
    for output in outputs if isinstance(outputs, list) else ():
        if isinstance(output, Mapping) and output.get("artifact_type") == expected:
            return True
    return False


def _registry_index(
    families: Sequence[Mapping[str, Any]],
    writers: Sequence[Mapping[str, Any]],
    postprocessors: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, list[int]]]:
    index: dict[str, dict[str, list[int]]] = {
        "family": {},
        "presentation_id": {},
        "presentation_alias": {},
        "presentation_group": {},
        "kind": {},
        "diagram": {},
        "diagram_renderer": {},
        "source_slot": {},
        "collection_source_slot": {},
        "sprite_slot": {},
        "route": {},
        "output_artifact_type": {},
        "artifact_type": {},
        "postprocessor_id": {},
        "postprocessor_kind": {},
    }
    for row_index, row in enumerate(families):
        _append_registry_index(index["family"], row.get("family"), row_index)
        presentation = row.get("presentation")
        if isinstance(presentation, Mapping):
            _append_registry_index(index["presentation_id"], presentation.get("id"), row_index)
            _append_registry_index(index["presentation_group"], presentation.get("group"), row_index)
            for alias in (presentation.get("aliases") if isinstance(presentation.get("aliases"), list) else ()):
                _append_registry_index(index["presentation_alias"], alias, row_index)
        _append_registry_index(index["kind"], row.get("kind"), row_index)
        diagram = row.get("diagram")
        if isinstance(diagram, Mapping):
            _append_registry_index(index["diagram"], diagram.get("id"), row_index)
            _append_registry_index(
                index["diagram_renderer"],
                diagram.get("renderer"),
                row_index,
            )
        _index_slot_contracts(index["source_slot"], row.get("source_slots"), row_index)
        _index_slot_contracts(
            index["collection_source_slot"],
            row.get("collection_source_slots"),
            row_index,
        )
        for sprite_slot in (row.get("sprite_slots") if isinstance(row.get("sprite_slots"), list) else ()):
            _append_registry_index(index["sprite_slot"], sprite_slot, row_index)
        routes = row.get("routes")
        for route in sorted(routes) if isinstance(routes, Mapping) else ():
            _append_registry_index(index["route"], route, row_index)
        _index_output_contracts(index["output_artifact_type"], row.get("outputs"), row_index)
    for row_index, row in enumerate(writers):
        _append_registry_index(index["artifact_type"], row.get("artifact_type"), row_index)
    for row_index, row in enumerate(postprocessors):
        _append_registry_index(
            index["postprocessor_id"],
            row.get("postprocessor_id"),
            row_index,
        )
        _append_registry_index(
            index["postprocessor_kind"],
            row.get("kind"),
            row_index,
        )
    return {name: {key: bucket[key] for key in sorted(bucket)} for name, bucket in index.items() if bucket}


def _index_output_contracts(bucket: dict[str, list[int]], outputs: object, row_index: int) -> None:
    if not isinstance(outputs, list):
        return
    artifact_types = sorted(
        {str(output["artifact_type"]) for output in outputs if isinstance(output, Mapping) and isinstance(output.get("artifact_type"), str)}
    )
    for artifact_type in artifact_types:
        _append_registry_index(bucket, artifact_type, row_index)


def _index_slot_contracts(bucket: dict[str, list[int]], slots: object, row_index: int) -> None:
    names = sorted(
        {
            str(slot["name"])
            for slot in (slots if isinstance(slots, list) else ())
            if isinstance(slot, Mapping) and isinstance(slot.get("name"), str) and slot["name"]
        }
    )
    for name in names:
        _append_registry_index(bucket, name, row_index)


def _append_registry_index(bucket: dict[str, list[int]], value: object, row_index: int) -> None:
    if isinstance(value, str) and value:
        append_index_entry(bucket, value, row_index)


def _family_presentation(
    family: str,
    value: object,
    *,
    presentation: FamilyPresentation | None,
) -> FamilyPresentation:
    """Resolve an explicit sidecar or compiler-owned presentation capability."""

    candidate = presentation if presentation is not None else getattr(value, "presentation", None)
    if candidate is None:
        return FamilyPresentation.default(family)
    if not isinstance(candidate, FamilyPresentation):
        raise ValueError(f"Build family {family!r} presentation must use FamilyPresentation.")
    own_selectors = candidate.selectors(family)
    if len(own_selectors) < 1:
        raise ValueError(f"Build family {family!r} presentation must define a resolvable id.")
    return candidate


def _family_view(
    family: Any,
    *,
    presentation: Mapping[str, object],
    source_slots: Sequence[dict[str, Any]] = (),
    collection_source_slots: Sequence[dict[str, Any]] = (),
    diagram: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    kind = _family_kind(family)
    row: dict[str, Any] = {
        "family": str(getattr(family, "family")),
        "kind": kind,
        "presentation": dict(presentation),
    }
    if getattr(family, "visible", True) is False:
        row["visible"] = False
    if diagram is not None:
        row["diagram"] = dict(diagram)
    stages = _stage_view(
        family,
        kind=kind,
        source_slots=source_slots,
        collection_source_slots=collection_source_slots,
    )
    if stages:
        row["stages"] = stages
    localization = _localization_view(family)
    if localization:
        row["localization"] = localization
    assets = _assets_view(family)
    if assets:
        row["assets"] = assets
    if hasattr(family, "identity_rewriter"):
        identity_rewriter = getattr(family, "identity_rewriter", None)
        row["authoring"] = {
            "identity_copy": (
                {
                    "supported": True,
                    "rewriter": str(getattr(identity_rewriter, "identifier")),
                }
                if identity_rewriter is not None
                else {"supported": False}
            )
        }
    row["metadata"] = _metadata_view(family)
    if source_slots:
        row["source_slots"] = list(source_slots)
    if collection_source_slots:
        row["collection_source_slots"] = list(collection_source_slots)
    sprite_slots = _strings(getattr(family, "sprite_slots", ()))
    if sprite_slots:
        row["sprite_slots"] = list(sprite_slots)
    if kind == "routed_source":
        settings_key = str(getattr(family, "settings_key", "subtype"))
        default_route = getattr(family, "default_route", None)
        routes = getattr(family, "routes", {})
        templates = _templates(family)
        outputs = _family_outputs(
            family,
            kind=kind,
            templates=templates,
            routes=routes,
            route_setting=f"settings.{settings_key}",
        )
        if outputs:
            row["outputs"] = outputs
        if templates:
            row["templates"] = templates
        row["route_setting"] = f"settings.{settings_key}"
        if default_route is not None:
            row["default_route"] = default_route
        row["routes"] = {name: _route_view(route) for name, route in sorted(routes.items())}
        return row
    templates = _templates(family)
    outputs = _family_outputs(family, kind=kind, templates=templates)
    if outputs:
        row["outputs"] = outputs
    if templates:
        row["templates"] = templates
    return row


def _validate_family_contract(key: str, family: Any) -> None:
    if hasattr(family, "retired_families"):
        raise ValueError(f"Build family {key!r} must keep publication replacement state in " "its extension descriptor, not retired_families.")
    visible = getattr(family, "visible", True)
    if not isinstance(visible, bool):
        raise ValueError(f"Build family {key!r} visible must be a boolean.")
    _validate_family_slots(key, family, "source_slots")
    _validate_family_slots(key, family, "collection_source_slots")
    _validate_family_string_list(key, family, "metadata_keys")
    _validate_family_string_list(key, family, "settings_keys")
    _validate_family_string_list(key, family, "required_settings")
    _validate_family_required_loc_keys(key, family)
    _validate_family_title_loc_keys(key, family)
    _validate_family_identity_rewriter(key, family)
    _validate_family_asset_constraints(key, family)
    _validate_family_default_assets(key, family)
    _validate_family_settings_values(key, family)
    _validate_family_settings_normalizers(key, family)
    family_kind = getattr(family, "family_kind", None)
    _validate_family_templates(key, family, family_kind)
    _validate_family_generated_outputs(key, family, _family_kind(family))
    if family_kind != "routed_source":
        return
    routes = getattr(family, "routes", None)
    if not isinstance(routes, Mapping) or not routes:
        raise ValueError(f"Routed build family {key!r} must define at least one route.")
    settings_key = getattr(family, "settings_key", None)
    if not isinstance(settings_key, str) or not settings_key.strip() or "." in settings_key:
        raise ValueError(f"Routed build family {key!r} settings_key must name a key under settings.")
    default_route = getattr(family, "default_route", None)
    if default_route is not None and (not isinstance(default_route, str) or default_route not in routes):
        raise ValueError(f"Routed build family {key!r} default_route must name one of: " f"{', '.join(sorted(str(route) for route in routes))}.")
    for route_name, route in routes.items():
        if not isinstance(route_name, str) or not route_name.strip():
            raise ValueError(f"Routed build family {key!r} route ids must be non-empty strings.")
    for route_name, route in sorted(routes.items()):
        route_templates = _validated_templates(route, f"Routed build family {key!r} route {route_name!r} templates")
        emits_artifacts = getattr(route, "emits_artifacts", True)
        if type(emits_artifacts) is not bool:
            raise ValueError(f"Routed build family {key!r} route {route_name!r} emits_artifacts must be a boolean.")
        if emits_artifacts and route_templates:
            continue
        if emits_artifacts:
            raise ValueError(f"Routed build family {key!r} route {route_name!r} must define at least one artifact template.")
        if route_templates:
            raise ValueError(f"Routed build family {key!r} route {route_name!r} cannot define artifact templates when emits_artifacts is false.")
    for route_name, route in sorted(routes.items()):
        route_templates = _validated_templates(route, f"Routed build family {key!r} route {route_name!r} templates")
        _validate_templates(
            route_templates,
            f"Routed build family {key!r} route {route_name!r} templates",
            _ROUTED_TEMPLATE_FIELDS,
        )


def _validate_family_string_list(key: str, family: Any, attr: str) -> None:
    _family_string_values(key, family, attr)


def _validate_family_identity_rewriter(key: str, family: Any) -> None:
    rewriter = getattr(family, "identity_rewriter", None)
    if rewriter is None:
        return
    identifier = getattr(rewriter, "identifier", None)
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError(f"Build family {key!r} identity_rewriter must define a non-empty identifier.")
    required_methods = ("rewrite_path", "rewrites_content", "rewrite_content")
    missing = [method for method in required_methods if not callable(getattr(rewriter, method, None))]
    if missing:
        raise ValueError(f"Build family {key!r} identity_rewriter must define callable " f"{', '.join(missing)}.")


def _validate_family_generated_outputs(key: str, family: Any, family_kind: str | None) -> None:
    raw = getattr(family, "generated_outputs", ())
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise ValueError(f"Build family {key!r} generated_outputs must be a list of output contract mappings.")
    routes = getattr(family, "routes", {})
    for index, output in enumerate(raw):
        label = f"Build family {key!r} generated_outputs[{index}]"
        if not isinstance(output, Mapping):
            raise ValueError(f"{label} must be an output contract mapping.")
        unknown = sorted(str(field) for field in output if field not in _GENERATED_OUTPUT_FIELDS)
        if unknown:
            raise ValueError(f"{label} uses unknown fields: {', '.join(unknown)}.")
        _required_output_string(output, "artifact_type", label)
        _required_output_strings(output, "owner_kinds", label, allowed=_OUTPUT_OWNER_KINDS)
        _required_output_string(output, "target_root", label, allowed=_OUTPUT_TARGET_ROOTS)
        description = output.get("description")
        if description is not None and (not isinstance(description, str) or not description.strip()):
            raise ValueError(f"{label}.description must be a non-empty string.")
        source_slots = _optional_output_strings(output, "source_slots", label)
        known_slots = {str(getattr(slot, "name", "")) for slot in getattr(family, "source_slots", ())}
        unknown_slots = sorted(set(source_slots) - known_slots)
        if unknown_slots:
            raise ValueError(f"{label}.source_slots names unknown source slots: {', '.join(unknown_slots)}.")
        route = output.get("route")
        if route is None:
            continue
        route_name = _required_output_string(output, "route", label)
        if family_kind != "routed_source":
            raise ValueError(f"{label}.route is only valid for routed_source families.")
        if not isinstance(routes, Mapping) or route_name not in routes:
            raise ValueError(f"{label}.route names unknown route {route_name!r}.")


def _required_output_string(
    output: Mapping[object, object],
    field: str,
    label: str,
    *,
    allowed: frozenset[str] | None = None,
) -> str:
    value = output.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}.{field} must be a non-empty string.")
    value = value.strip()
    if allowed is not None and value not in allowed:
        raise ValueError(f"{label}.{field} must be one of: {', '.join(sorted(allowed))}.")
    return value


def _required_output_strings(
    output: Mapping[object, object],
    field: str,
    label: str,
    *,
    allowed: frozenset[str] | None = None,
) -> tuple[str, ...]:
    values = _optional_output_strings(output, field, label)
    if not values:
        raise ValueError(f"{label}.{field} must define at least one value.")
    if allowed is not None:
        unsupported = sorted(set(values) - allowed)
        if unsupported:
            raise ValueError(f"{label}.{field} must contain only: {', '.join(sorted(allowed))}.")
    return values


def _optional_output_strings(output: Mapping[object, object], field: str, label: str) -> tuple[str, ...]:
    raw = output.get(field, ())
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise ValueError(f"{label}.{field} must be a list of non-empty strings.")
    values: list[str] = []
    for value in raw:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label}.{field} must be a list of non-empty strings.")
        normalized = value.strip()
        if normalized in values:
            raise ValueError(f"{label}.{field} must not contain duplicate values.")
        values.append(normalized)
    return tuple(values)


def _validate_family_templates(key: str, family: Any, family_kind: str | None) -> None:
    templates = _validated_templates(family, f"Build family {key!r} templates")
    _validate_family_sprite_templates(key, family, family_kind, templates)
    if not templates:
        return
    _validate_templates(
        templates,
        f"Build family {key!r} templates",
        _family_template_fields(family, family_kind),
    )


def _family_template_fields(family: Any, family_kind: str | None) -> Mapping[str, frozenset[str]]:
    if family_kind in {"collection_pdx", "collection_source"}:
        if getattr(family, "aggregate_member_localization", False) is True:
            return {
                **_COLLECTION_SOURCE_TEMPLATE_FIELDS,
                "loc": _COLLECTION_TEMPLATE_FIELDS,
            }
        return _COLLECTION_SOURCE_TEMPLATE_FIELDS
    if family_kind == "simple_source":
        return _SIMPLE_TEMPLATE_FIELDS
    if hasattr(family, "view_path_template") or hasattr(family, "module_pdx_path_template"):
        return _COLLECTION_SOURCE_TEMPLATE_FIELDS
    return _SIMPLE_TEMPLATE_FIELDS


def _validate_family_sprite_templates(
    key: str,
    family: Any,
    family_kind: str | None,
    templates: Mapping[str, str],
) -> None:
    sprite_slots = _family_string_values(key, family, "sprite_slots")
    sprite_keys = {"sprite_gfx", "sprite_name"} & set(templates)
    label = f"Build family {key!r}"
    kind = family_kind if isinstance(family_kind, str) and family_kind else _family_kind(family)
    if kind not in {"simple_source", "routed_source"}:
        if sprite_keys:
            template_key = sorted(sprite_keys)[0]
            raise ValueError(f"{label} templates.{template_key} is only valid for simple_source and routed_source families.")
        if sprite_slots:
            raise ValueError(f"{label} sprite_slots is only valid for simple_source and routed_source families.")
        return
    if not sprite_keys and not sprite_slots:
        return
    if kind == "simple_source" and "copy" not in templates:
        raise ValueError(f"{label} templates.copy must be defined when sprite templates are declared.")
    if kind == "routed_source" and not _routed_family_has_copy_template(family):
        raise ValueError(f"{label} routes must define at least one copy template when sprite templates are declared.")
    if "sprite_gfx" not in templates:
        raise ValueError(f"{label} templates.sprite_gfx must be defined when sprite slots are declared.")
    if "sprite_name" not in templates:
        raise ValueError(f"{label} templates.sprite_name must be defined when sprite slots are declared.")
    if not sprite_slots:
        raise ValueError(f"{label} sprite_slots must define at least one slot when sprite templates are declared.")


def _routed_family_has_copy_template(family: Any) -> bool:
    routes = getattr(family, "routes", {})
    if not isinstance(routes, Mapping):
        return False
    for route in routes.values():
        template = getattr(route, "copy_path_template", None)
        if isinstance(template, str) and template.strip():
            return True
    return False


def _validate_templates(
    templates: Mapping[str, str],
    label: str,
    fields_by_key: Mapping[str, frozenset[str]],
) -> None:
    for template_key, template in templates.items():
        allowed_fields = fields_by_key.get(template_key)
        if allowed_fields is None:
            continue
        _validate_template_fields(template, f"{label}.{template_key}", allowed_fields)


def _validated_templates(value: Any, label: str) -> dict[str, str]:
    templates: dict[str, str] = {}
    for key, attr in _TEMPLATE_ATTRS:
        template = getattr(value, attr, None)
        if template is None:
            continue
        if not isinstance(template, str) or not template.strip():
            raise ValueError(f"{label}.{key} must be a non-empty string.")
        templates[key] = template.strip()
    return templates


def _validate_family_slots(key: str, family: Any, attr: str) -> None:
    raw = getattr(family, attr, ())
    if raw is None:
        return
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise ValueError(f"Build family {key!r} {attr} must be a list of Slot values.")
    for index, slot in enumerate(raw):
        _validate_family_slot(key, attr, index, slot)


def _validate_family_slot(key: str, attr: str, index: int, slot: Any) -> None:
    _validate_slot_contract(f"Build family {key!r} {attr}[{index}]", slot)


def _validate_registry_slots(attr: str, raw: Any) -> None:
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise ValueError(f"Build registry {attr} must be a list of Slot values.")
    for index, slot in enumerate(raw):
        _validate_slot_contract(f"Build registry {attr}[{index}]", slot)


def _validate_slot_contract(label: str, slot: Any) -> None:
    name = getattr(slot, "name", None)
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"{label}.name must be a non-empty string.")
    match = getattr(slot, "match", None)
    if not isinstance(match, str) or not match.strip():
        raise ValueError(f"{label}.match must be a non-empty string.")
    for flag in ("required", "many", "regex", "shared"):
        value = getattr(slot, flag, False)
        if type(value) is not bool:
            raise ValueError(f"{label}.{flag} must be a boolean.")
    if getattr(slot, "regex", False):
        _validate_regex(match, f"{label}.match")
    if slot_match_escapes_root(match, regex=bool(getattr(slot, "regex", False))):
        raise ValueError(f"{label}.match must be relative and stay under the source root.")
    kind = getattr(slot, "kind", None)
    if kind is not None and (not isinstance(kind, str) or not kind.strip()):
        raise ValueError(f"{label}.kind must be a non-empty string.")
    authoring_path = getattr(slot, "authoring_path", None)
    if authoring_path is None:
        return
    if kind != "copy":
        raise ValueError(f"{label}.authoring_path requires kind='copy'.")
    if not isinstance(authoring_path, str) or not authoring_path.strip():
        raise ValueError(f"{label}.authoring_path must be a non-empty string.")
    path = PurePosixPath(authoring_path.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label}.authoring_path must be relative and stay under the source root.")
    try:
        fields = {field_name for _literal, field_name, _format_spec, _conversion in _FORMATTER.parse(authoring_path) if field_name is not None}
    except ValueError as error:
        raise ValueError(f"{label}.authoring_path must use valid format placeholders: {error}.") from error
    unknown = sorted(fields - _SLOT_AUTHORING_FIELDS)
    if unknown:
        raise ValueError(
            f"{label}.authoring_path uses unsupported fields: {', '.join(unknown)}. " f"Expected only: {', '.join(sorted(_SLOT_AUTHORING_FIELDS))}."
        )


def _validate_regex(pattern: str, label: str) -> None:
    try:
        re.compile(pattern)
    except re.error as error:
        raise ValueError(f"{label} must be a valid regex: {error}.") from error


def _family_string_values(key: str, family: Any, attr: str) -> tuple[str, ...]:
    raw = getattr(family, attr, ())
    values = (raw,) if isinstance(raw, str) else raw
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise ValueError(f"Build family {key!r} {attr} must be a string or list of strings.")
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Build family {key!r} {attr} must be a string or list of strings.")
        result.append(value)
    return tuple(result)


def _publication_replacement_values(
    key: str,
    raw: object,
) -> tuple[str, ...]:
    values = (raw,) if isinstance(raw, str) else raw
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise ValueError(f"Build family {key!r} publication replacements must be a list of strings.")
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Build family {key!r} publication replacements must be a " "list of strings.")
        normalized.append(value)
    if key in normalized:
        raise ValueError(f"Build family {key!r} publication replacements cannot include itself.")
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"Build family {key!r} publication replacements must not contain " "duplicate values.")
    if any(value != value.strip() for value in normalized):
        raise ValueError(f"Build family {key!r} publication replacement values must not " "have surrounding whitespace.")
    return tuple(sorted(normalized))


def _validate_family_required_loc_keys(key: str, family: Any) -> None:
    label = f"Build family {key!r} required_loc_keys"
    for template in _family_string_values(key, family, "required_loc_keys"):
        _validate_template_fields(template, label, _REQUIRED_LOC_TEMPLATE_FIELDS)


def _validate_family_title_loc_keys(key: str, family: Any) -> None:
    raw = getattr(family, "title_loc_keys", None)
    if raw is None:
        return
    label = f"Build family {key!r} title_loc_keys"
    templates = _family_string_values(key, family, "title_loc_keys")
    if len(set(templates)) != len(templates):
        raise ValueError(f"{label} must not contain duplicate templates.")
    for template in templates:
        _validate_template_fields(template, label, _REQUIRED_LOC_TEMPLATE_FIELDS)


def _validate_template_fields(template: str, label: str, allowed_fields: frozenset[str]) -> None:
    for template_field in _template_fields(template, label):
        if template_field in allowed_fields:
            continue
        allowed = ", ".join(sorted(allowed_fields))
        raise ValueError(f"{label} uses unknown template field {template_field!r}; supported fields: {allowed}.")


def _template_fields(template: str, label: str) -> tuple[str, ...]:
    fields: list[str] = []
    try:
        parsed = tuple(_FORMATTER.parse(template))
    except ValueError as error:
        raise ValueError(f"{label} must use valid Python format fields: {error}.") from error
    for _literal, field_name, format_spec, _conversion in parsed:
        if field_name is not None:
            if not field_name:
                raise ValueError(f"{label} must use named template fields.")
            if not field_name.isidentifier():
                raise ValueError(f"{label} uses unsupported template field {field_name!r}.")
            fields.append(field_name)
        if format_spec:
            fields.extend(_template_fields(format_spec, label))
    return tuple(fields)


def _validate_family_asset_constraints(key: str, family: Any) -> None:
    raw = getattr(family, "asset_constraints", {})
    if not isinstance(raw, Mapping):
        raise ValueError(f"Build family {key!r} asset_constraints must be a mapping.")
    for slot, raw_constraint in raw.items():
        if not isinstance(slot, str) or not slot.strip():
            raise ValueError(f"Build family {key!r} asset_constraints keys must be non-empty strings.")
        slot_name = slot.strip()
        if not isinstance(raw_constraint, Mapping):
            raise ValueError(f"Build family {key!r} asset_constraints.{slot_name} must be a mapping.")
        _validate_family_asset_constraint(key, slot_name, raw_constraint)


def _validate_family_asset_constraint(key: str, slot: str, raw: Mapping[str, object]) -> None:
    label = f"Build family {key!r} asset_constraints.{slot}"
    has_constraint = False
    raw_formats = raw.get("formats", raw.get("format"))
    if raw_formats is not None and _validated_asset_formats(raw_formats, f"{label}.formats"):
        has_constraint = True
    for dimension in ("width", "height"):
        value = raw.get(dimension)
        if value is None:
            continue
        if type(value) is not int or value <= 0:
            raise ValueError(f"{label}.{dimension} must be a positive integer.")
        has_constraint = True
    if not has_constraint:
        raise ValueError(f"{label} must define at least one of: formats, width, height.")


def _validate_family_default_assets(key: str, family: Any) -> None:
    raw = getattr(family, "default_assets", {})
    if not isinstance(raw, Mapping):
        raise ValueError(f"Build family {key!r} default_assets must be a mapping.")
    for slot, raw_asset in raw.items():
        if not isinstance(slot, str) or not slot.strip():
            raise ValueError(f"Build family {key!r} default_assets keys must be non-empty strings.")
        slot_name = slot.strip()
        if not isinstance(raw_asset, Mapping):
            raise ValueError(f"Build family {key!r} default_assets.{slot_name} must be a mapping.")
        _validate_family_default_asset(key, slot_name, raw_asset)


def _validate_family_default_asset(key: str, slot: str, raw: Mapping[str, object]) -> None:
    label = f"Build family {key!r} default_assets.{slot}"
    if "path" not in raw and "asset_id" not in raw:
        raise ValueError(f"{label} must define path or asset_id.")
    for asset_field in ("asset_id", "path", "source", "title"):
        value = raw.get(asset_field)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError(f"{label}.{asset_field} must be a non-empty string.")
    path = raw.get("path")
    if isinstance(path, str):
        _validate_default_asset_path(path, f"{label}.path")
    editable = raw.get("editable")
    if editable is not None and type(editable) is not bool:
        raise ValueError(f"{label}.editable must be a boolean.")


def _validate_default_asset_path(value: str, label: str) -> None:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ValueError(f"{label} must be relative and stay inside the project.")


def _validated_asset_formats(raw: object, label: str) -> tuple[str, ...]:
    if isinstance(raw, str):
        values = (raw,)
    elif isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
        values = tuple(raw)
    else:
        raise ValueError(f"{label} must be a string or list of strings.")
    formats: list[str] = []
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label}[{index}] must be a non-empty string.")
        formats.append(value.strip().lower().lstrip("."))
    return tuple(sorted(set(formats)))


def _validate_family_settings_values(key: str, family: Any) -> None:
    raw = getattr(family, "settings_values", {})
    if not isinstance(raw, Mapping):
        raise ValueError(f"Build family {key!r} settings_values must be a mapping.")
    for setting, raw_values in raw.items():
        if not isinstance(setting, str) or not setting.strip():
            raise ValueError(f"Build family {key!r} settings_values keys must be non-empty strings.")
        values = (raw_values,) if isinstance(raw_values, str) else raw_values
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
            raise ValueError(f"Build family {key!r} settings_values.{setting} must be a string or list of strings.")
        for value in values:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Build family {key!r} settings_values.{setting} must be a string or list of strings.")


def _validate_family_settings_normalizers(key: str, family: Any) -> None:
    raw = getattr(family, "settings_normalizers", {})
    if not isinstance(raw, Mapping):
        raise ValueError(f"Build family {key!r} settings_normalizers must be a mapping.")
    for setting, normalizer in raw.items():
        if not isinstance(setting, str) or not setting.strip():
            raise ValueError(f"Build family {key!r} settings_normalizers keys must be non-empty strings.")
        if not callable(normalizer):
            raise ValueError(f"Build family {key!r} settings_normalizers.{setting} must be callable.")


def _stage_view(
    family: Any,
    *,
    kind: str,
    source_slots: Sequence[dict[str, Any]] = (),
    collection_source_slots: Sequence[dict[str, Any]] = (),
) -> list[str]:
    stages: list[str] = []
    if source_slots or collection_source_slots:
        stages.extend(("discover", "load"))
    if callable(getattr(family, "normalize", None)):
        stages.append("normalize")
    if kind in {"collection_pdx", "collection_source"}:
        stages.append("aggregate")
    if callable(getattr(family, "compile", None)):
        stages.append("compile")
    else:
        if callable(getattr(family, "check", None)):
            stages.append("check")
        if callable(getattr(family, "emit", None)):
            stages.append("emit")
    return stages


def _family_kind(family: Any) -> str:
    family_kind = getattr(family, "family_kind", None)
    if isinstance(family_kind, str) and family_kind:
        return family_kind
    if hasattr(family, "routes"):
        return "routed_source"
    if hasattr(family, "view_path_template") or hasattr(family, "module_pdx_path_template"):
        return "collection_pdx"
    if any(
        hasattr(family, attr)
        for attr in (
            "pdx_path_template",
            "loc_path_template",
            "copy_path_template",
            "sprite_gfx_path_template",
        )
    ):
        return "simple_source"
    return type(family).__name__


def _templates(value: Any) -> dict[str, str]:
    return {key: template for key, attr in _TEMPLATE_ATTRS for template in (getattr(value, attr, None),) if isinstance(template, str) and template}


def _route_view(route: Any) -> dict[str, Any]:
    view: dict[str, Any] = _templates(route)
    if getattr(route, "emits_artifacts", True) is False:
        view["emits_artifacts"] = False
    return view


def _family_outputs(
    family: Any,
    *,
    kind: str,
    templates: Mapping[str, str],
    routes: Mapping[str, Any] | None = None,
    route_setting: str | None = None,
) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    if kind == "routed_source" and routes:
        for route_name, route in sorted(routes.items()):
            outputs.extend(
                _output_views(
                    family,
                    kind=kind,
                    templates=_templates(route),
                    route=str(route_name),
                    route_setting=route_setting,
                )
            )
        outputs.extend(_output_views(family, kind=kind, templates=templates))
        outputs.extend(_generated_output_views(family, route_setting=route_setting))
        return outputs
    outputs.extend(_output_views(family, kind=kind, templates=templates))
    outputs.extend(_generated_output_views(family))
    return outputs


def _generated_output_views(family: Any, *, route_setting: str | None = None) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for raw in getattr(family, "generated_outputs", ()):
        output: dict[str, Any] = {
            "artifact_type": str(raw["artifact_type"]).strip(),
            "generated": True,
            "owner_kinds": list(_output_strings(raw, "owner_kinds")),
            "target_root": str(raw["target_root"]).strip(),
        }
        description = raw.get("description")
        if isinstance(description, str):
            output["description"] = description.strip()
        route = raw.get("route")
        if isinstance(route, str):
            output["route"] = route.strip()
            if route_setting is not None:
                output["route_setting"] = route_setting
        source_slots = _output_strings(raw, "source_slots")
        if source_slots:
            output["source_slots"] = list(source_slots)
        outputs.append(output)
    return outputs


def _output_strings(output: Mapping[object, object], field: str) -> tuple[str, ...]:
    raw = output.get(field, ())
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return ()
    return tuple(value.strip() for value in raw if isinstance(value, str))


def _output_views(
    family: Any,
    *,
    kind: str,
    templates: Mapping[str, str],
    route: str | None = None,
    route_setting: str | None = None,
) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for template_key in _OUTPUT_TEMPLATE_KEYS:
        template = templates.get(template_key)
        if not template:
            continue
        output = _output_view(family, kind=kind, template_key=template_key, template=template)
        if route is not None:
            output["route"] = route
        if route_setting is not None and route is not None:
            output["route_setting"] = route_setting
        outputs.append(output)
    return outputs


def _output_view(family: Any, *, kind: str, template_key: str, template: str) -> dict[str, Any]:
    output = {
        "artifact_type": _OUTPUT_ARTIFACT_TYPES[template_key],
        "template_key": template_key,
        "template": template,
        "owner_kinds": list(_output_owner_kinds(kind, template_key)),
        "target_root": _output_target_root(template_key),
    }
    if template_key == "sprite_gfx":
        sprite_slots = _strings(getattr(family, "sprite_slots", ()))
        if sprite_slots:
            output["source_slots"] = list(sprite_slots)
    return output


def _output_owner_kinds(kind: str, template_key: str) -> tuple[str, ...]:
    if template_key == "sprite_gfx":
        return ("project",)
    if template_key == "module_pdx":
        return ("module",)
    if kind in {"collection_pdx", "collection_source"}:
        if template_key in {"pdx", "view"}:
            return ("collection",)
        if template_key in {"loc", "copy"}:
            return ("collection", "module")
    return ("module",)


def _output_target_root(template_key: str) -> str:
    if template_key == "view":
        return "build"
    return "output"


def _metadata_view(family: Any) -> dict[str, Any]:
    common_keys = sorted(METADATA_KEYS)
    family_keys = list(_strings(getattr(family, "metadata_keys", ())))
    payload: dict[str, Any] = {
        "keys": sorted({*common_keys, *family_keys}),
        "common_keys": common_keys,
        "family_keys": family_keys,
        "unknown_key_policy": dict(_UNKNOWN_METADATA_KEY_POLICY),
    }
    settings = _settings_view(family)
    if settings:
        payload["settings"] = settings
    return payload


def _localization_view(family: Any) -> dict[str, Any]:
    required_keys = _strings(getattr(family, "required_loc_keys", ()))
    raw_title_keys = getattr(family, "title_loc_keys", None)
    if not required_keys and raw_title_keys is None:
        return {}
    payload: dict[str, Any] = {}
    if required_keys:
        payload.update(
            {
                "required_keys": list(required_keys),
                "required_when": "loc_authored",
            }
        )
    if raw_title_keys is not None:
        payload["title_keys"] = list(
            _family_string_values(
                str(getattr(family, "family", "")),
                family,
                "title_loc_keys",
            )
        )
    return payload


def _assets_view(family: Any) -> dict[str, Any]:
    constraints = _asset_constraints(family)
    defaults = _default_assets(family)
    if not constraints and not defaults:
        return {}
    payload: dict[str, Any] = {}
    if constraints:
        payload["slots"] = constraints
    if defaults:
        payload["defaults"] = defaults
    return payload


def _settings_view(family: Any) -> dict[str, dict[str, Any]]:
    settings = {key: {"required": False} for key in _strings(getattr(family, "settings_keys", ()))}
    for key in _strings(getattr(family, "required_settings", ())):
        settings.setdefault(key, {})["required"] = True
    for key, values in _settings_values(family).items():
        settings.setdefault(key, {"required": False})["values"] = list(values)
    if hasattr(family, "routes"):
        settings_key = str(getattr(family, "settings_key", "subtype"))
        routes = getattr(family, "routes", {})
        default_route = getattr(family, "default_route", None)
        route_setting: dict[str, Any] = {
            "required": default_route is None,
            "values": sorted(routes),
        }
        if default_route is not None:
            route_setting["default"] = default_route
        settings[settings_key] = route_setting
    return {key: settings[key] for key in sorted(settings)}


def _slot_view(slot: Any) -> dict[str, Any]:
    view = {
        "name": str(getattr(slot, "name")),
        "match": str(getattr(slot, "match")),
        "required": bool(getattr(slot, "required", False)),
        "many": bool(getattr(slot, "many", False)),
        "regex": bool(getattr(slot, "regex", False)),
    }
    kind = getattr(slot, "kind", None)
    if isinstance(kind, str) and kind:
        view["kind"] = kind
    if bool(getattr(slot, "shared", False)):
        view["shared"] = True
    authoring_path = getattr(slot, "authoring_path", None)
    if isinstance(authoring_path, str) and authoring_path:
        view["authoring_path"] = authoring_path
    return view


def _strings(values: Any) -> tuple[str, ...]:
    if isinstance(values, str):
        return (values,)
    if not isinstance(values, Sequence):
        return ()
    return tuple(sorted({value for value in values if isinstance(value, str) and value}))


def _settings_values(family: Any) -> dict[str, tuple[str, ...]]:
    raw = getattr(family, "settings_values", {})
    if not isinstance(raw, Mapping):
        return {}
    settings: dict[str, tuple[str, ...]] = {}
    for key, raw_values in raw.items():
        if not isinstance(key, str) or not key:
            continue
        values = _strings(raw_values)
        if values:
            settings[key] = values
    return settings


def _asset_constraints(family: Any) -> dict[str, dict[str, object]]:
    raw = getattr(family, "asset_constraints", {})
    if not isinstance(raw, Mapping):
        return {}
    constraints: dict[str, dict[str, object]] = {}
    for slot, raw_constraint in raw.items():
        if not isinstance(slot, str) or not slot or not isinstance(raw_constraint, Mapping):
            continue
        constraint = _asset_constraint(raw_constraint)
        if constraint:
            constraints[slot] = constraint
    return {slot: constraints[slot] for slot in sorted(constraints)}


def _default_assets(family: Any) -> dict[str, dict[str, object]]:
    raw = getattr(family, "default_assets", {})
    family_id = str(getattr(family, "family", "")).strip()
    if not isinstance(raw, Mapping) or not family_id:
        return {}
    assets: dict[str, dict[str, object]] = {}
    for slot, raw_asset in raw.items():
        if not isinstance(slot, str) or not slot or not isinstance(raw_asset, Mapping):
            continue
        slot_name = slot.strip()
        asset_id = _default_asset_text(raw_asset.get("asset_id")) or f"{family_id}:{slot_name}/default"
        path = _default_asset_text(raw_asset.get("path")) or asset_id
        title = _default_asset_text(raw_asset.get("title")) or f"{family_id.replace('_', ' ').title()} {slot_name.replace('_', ' ')} default"
        source = _default_asset_text(raw_asset.get("source")) or "project"
        editable = raw_asset.get("editable")
        assets[slot_name] = {
            "slot": slot_name,
            "asset_id": asset_id,
            "title": title,
            "source": source,
            "path": path,
            "editable": editable if type(editable) is bool else True,
            "injected": False,
        }
    return {slot: assets[slot] for slot in sorted(assets)}


def _default_asset_text(value: object) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _asset_constraint(raw: Mapping[str, object]) -> dict[str, object]:
    constraint: dict[str, object] = {}
    formats = _asset_formats(raw.get("formats", raw.get("format", ())))
    if formats:
        constraint["formats"] = list(formats)
    width = _positive_int(raw.get("width"))
    height = _positive_int(raw.get("height"))
    if width is not None:
        constraint["width"] = width
    if height is not None:
        constraint["height"] = height
    return constraint


def _asset_formats(raw: object) -> tuple[str, ...]:
    if isinstance(raw, str):
        values = (raw,)
    elif isinstance(raw, Sequence):
        values = tuple(value for value in raw if isinstance(value, str))
    else:
        return ()
    return tuple(sorted({value.lower().lstrip(".") for value in values if value.strip()}))


def _positive_int(raw: object) -> int | None:
    if type(raw) is int and raw > 0:
        return raw
    return None
