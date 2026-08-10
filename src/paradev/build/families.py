"""Generic build family helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path
from string import Formatter
from typing import ClassVar

from paradev.pdx import PDXBlock, PDXEntry, PDXScalar

from .artifacts import SpriteType
from .authoring import DEFAULT_IDENTITY_REWRITER, ModuleIdentityRewriter
from .loaders import CollectionSourceBundle, LocalizationEntry, ModuleSourceBundle
from .plan import BuildContext, FamilyNormalizeResult
from .presentation import FamilyPresentation
from .records import Artifact, Collection, Diagnostic, Module
from .slots import Slot

SettingNormalizer = Callable[[object], object]


@dataclass(frozen=True, slots=True)
class _FocusRecord:
    module_id: str
    source_path: str | None
    focus_id: str | None
    focus_id_span: dict[str, int] | None = None
    prerequisites: tuple["_FocusReference", ...] = ()


@dataclass(frozen=True, slots=True)
class _FocusReference:
    focus_id: str
    span: dict[str, int] | None = None


@dataclass(frozen=True, slots=True)
class _LocalizationAnchor:
    object_id: str
    source_path: str | None
    span: dict[str, int] | None = None


@dataclass(frozen=True, slots=True)
class SimpleSourceFamily:
    """Generic family that emits PDX and copy artifacts from loaded source bundles."""

    family_kind: ClassVar[str] = "simple_source"
    family: str
    pdx_path_template: str | None = None
    loc_path_template: str | None = None
    copy_path_template: str | None = None
    sprite_gfx_path_template: str | None = None
    sprite_name_template: str | None = None
    sprite_slots: tuple[str, ...] = ()
    source_slots: tuple[Slot, ...] = ()
    metadata_keys: tuple[str, ...] = ()
    settings_keys: tuple[str, ...] = ()
    settings_values: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    required_settings: tuple[str, ...] = ()
    required_loc_keys: tuple[str, ...] = ()
    title_loc_keys: tuple[str, ...] | None = None
    identity_rewriter: ModuleIdentityRewriter | None = DEFAULT_IDENTITY_REWRITER
    asset_constraints: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    default_assets: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    settings_normalizers: Mapping[str, SettingNormalizer] = field(default_factory=dict)
    visible: bool = True
    presentation: FamilyPresentation | None = None

    def normalize(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> FamilyNormalizeResult:
        """Return modules with normalized family settings."""

        return _settings_normalize_result(self, modules)

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Return diagnostics for declared settings contracts."""

        return (
            *_settings_contract_diagnostics(self, modules),
            *_localization_contract_diagnostics(self, modules),
            *_asset_contract_diagnostics(self, modules),
            *_sprite_contract_diagnostics(self, modules),
        )

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit artifacts for loaded modules."""

        return _module_artifacts(
            modules,
            pdx_path_template=self.pdx_path_template,
            loc_path_template=self.loc_path_template,
            copy_path_template=self.copy_path_template,
            sprite_gfx_path_template=self.sprite_gfx_path_template,
            sprite_name_template=self.sprite_name_template,
            sprite_slots=self.sprite_slots,
            project_id=ctx.project_id,
            family=self.family,
        )


@dataclass(frozen=True, slots=True)
class SourceRoute:
    """Configure artifact emission for one routed source-family variant.

    Args:
        pdx_path_template: Optional PDX artifact path template.
        loc_path_template: Optional localization artifact path template.
        copy_path_template: Optional copied-asset path template.
        emits_artifacts: Whether the route emits generic artifacts. Set this
            explicitly to `False` only for a route with no artifact templates.
    """

    pdx_path_template: str | None = None
    loc_path_template: str | None = None
    copy_path_template: str | None = None
    emits_artifacts: bool = True


@dataclass(frozen=True, slots=True)
class RoutedSourceFamily:
    """Generic family that selects artifact templates from a module settings route."""

    family_kind: ClassVar[str] = "routed_source"
    family: str
    routes: Mapping[str, SourceRoute]
    settings_key: str = "subtype"
    default_route: str | None = None
    source_slots: tuple[Slot, ...] = ()
    metadata_keys: tuple[str, ...] = ()
    settings_keys: tuple[str, ...] = ()
    settings_values: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    required_settings: tuple[str, ...] = ()
    required_loc_keys: tuple[str, ...] = ()
    title_loc_keys: tuple[str, ...] | None = None
    identity_rewriter: ModuleIdentityRewriter | None = DEFAULT_IDENTITY_REWRITER
    asset_constraints: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    default_assets: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    settings_normalizers: Mapping[str, SettingNormalizer] = field(default_factory=dict)
    sprite_gfx_path_template: str | None = None
    sprite_name_template: str | None = None
    sprite_slots: tuple[str, ...] = ()
    visible: bool = True
    presentation: FamilyPresentation | None = None

    def normalize(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> FamilyNormalizeResult:
        """Return modules with normalized family settings."""

        return _settings_normalize_result(self, modules)

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Return diagnostics for modules without a supported route."""

        route_names = _route_names(self.routes)
        diagnostics: list[Diagnostic] = []
        for module in modules:
            route_name = _module_route(module, self.settings_key) or self.default_route
            if not route_name:
                diagnostics.append(
                    Diagnostic(
                        code="family.missing_route",
                        message=f"Module {module.module_id} must set settings.{self.settings_key} to one of: {', '.join(route_names)}.",
                        severity="error",
                        module_id=module.module_id,
                        source_path="meta.yaml",
                    )
                )
                continue
            if route_name not in self.routes:
                diagnostics.append(
                    Diagnostic(
                        code="family.unsupported_route",
                        message=f"Module {module.module_id} settings.{self.settings_key} {route_name!r} must be one of: {', '.join(route_names)}.",
                        severity="error",
                        module_id=module.module_id,
                        source_path="meta.yaml",
                    )
                )
        diagnostics.extend(_settings_contract_diagnostics(self, modules, exclude=(self.settings_key,)))
        diagnostics.extend(_localization_contract_diagnostics(self, modules))
        diagnostics.extend(_asset_contract_diagnostics(self, modules))
        diagnostics.extend(_sprite_contract_diagnostics(self, modules))
        return tuple(diagnostics)

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit artifacts through the selected route templates."""

        return tuple(
            _routed_module_artifacts(
                modules,
                routes=self.routes,
                settings_key=self.settings_key,
                default_route=self.default_route,
                sprite_gfx_path_template=self.sprite_gfx_path_template,
                sprite_name_template=self.sprite_name_template,
                sprite_slots=self.sprite_slots,
                project_id=ctx.project_id,
                family=self.family,
            )
        )


@dataclass(frozen=True, slots=True)
class CollectionPDXFamily:
    """Family that emits collection-owned PDX artifacts and optional module artifacts."""

    family_kind: ClassVar[str] = "collection_pdx"
    family: str
    pdx_path_template: str
    view_path_template: str | None = None
    module_pdx_path_template: str | None = None
    loc_path_template: str | None = None
    copy_path_template: str | None = None
    source_slots: tuple[Slot, ...] = ()
    collection_source_slots: tuple[Slot, ...] = ()
    metadata_keys: tuple[str, ...] = ()
    settings_keys: tuple[str, ...] = ()
    settings_values: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    required_settings: tuple[str, ...] = ()
    required_loc_keys: tuple[str, ...] = ()
    title_loc_keys: tuple[str, ...] | None = None
    identity_rewriter: ModuleIdentityRewriter | None = DEFAULT_IDENTITY_REWRITER
    asset_constraints: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    default_assets: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    settings_normalizers: Mapping[str, SettingNormalizer] = field(default_factory=dict)
    member_container: str | None = None
    aggregate_member_localization: bool = False
    visible: bool = True
    presentation: FamilyPresentation | None = None

    def normalize(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> FamilyNormalizeResult:
        """Return modules with normalized family settings."""

        return _settings_normalize_result(self, modules)

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Return collection-level diagnostics for focus-like PDX modules."""

        return (
            *_settings_contract_diagnostics(self, modules),
            *_collection_settings_contract_diagnostics(self, collections),
            *_localization_contract_diagnostics(self, modules),
            *_collection_localization_contract_diagnostics(self, collections),
            *_asset_contract_diagnostics(self, modules),
            *_collection_asset_contract_diagnostics(self, collections),
            *_focus_collection_diagnostics(self.family, modules, collections),
        )

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit one PDX artifact per matching collection plus optional module outputs."""

        return tuple(
            _collection_artifacts(
                self.family,
                modules,
                collections,
                pdx_path_template=self.pdx_path_template,
                module_pdx_path_template=self.module_pdx_path_template,
                loc_path_template=self.loc_path_template,
                copy_path_template=self.copy_path_template,
                view_path_template=self.view_path_template,
                view_metadata=_focus_tree_view_metadata,
                include_collection_pdx=self.member_container is not None,
                member_container=self.member_container,
                aggregate_member_localization=self.aggregate_member_localization,
            )
        )


@dataclass(frozen=True, slots=True)
class CollectionSourceFamily:
    """Generic family that emits collection-owned PDX artifacts plus module artifacts."""

    family_kind: ClassVar[str] = "collection_source"
    family: str
    pdx_path_template: str
    module_pdx_path_template: str | None = None
    loc_path_template: str | None = None
    copy_path_template: str | None = None
    source_slots: tuple[Slot, ...] = ()
    collection_source_slots: tuple[Slot, ...] = ()
    metadata_keys: tuple[str, ...] = ()
    settings_keys: tuple[str, ...] = ()
    settings_values: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    required_settings: tuple[str, ...] = ()
    required_loc_keys: tuple[str, ...] = ()
    title_loc_keys: tuple[str, ...] | None = None
    identity_rewriter: ModuleIdentityRewriter | None = DEFAULT_IDENTITY_REWRITER
    asset_constraints: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    default_assets: Mapping[str, Mapping[str, object]] = field(default_factory=dict)
    settings_normalizers: Mapping[str, SettingNormalizer] = field(default_factory=dict)
    aggregate_member_localization: bool = False
    visible: bool = True
    presentation: FamilyPresentation | None = None

    def normalize(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> FamilyNormalizeResult:
        """Return modules with normalized family settings."""

        return _settings_normalize_result(self, modules)

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Return diagnostics for declared settings contracts."""

        return (
            *_settings_contract_diagnostics(self, modules),
            *_collection_settings_contract_diagnostics(self, collections),
            *_localization_contract_diagnostics(self, modules),
            *_collection_localization_contract_diagnostics(self, collections),
            *_asset_contract_diagnostics(self, modules),
            *_collection_asset_contract_diagnostics(self, collections),
        )

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit collection-owned PDX artifacts and module-owned side artifacts."""

        return tuple(
            _collection_artifacts(
                self.family,
                modules,
                collections,
                pdx_path_template=self.pdx_path_template,
                module_pdx_path_template=self.module_pdx_path_template,
                loc_path_template=self.loc_path_template,
                copy_path_template=self.copy_path_template,
                include_collection_pdx=True,
                aggregate_member_localization=self.aggregate_member_localization,
            )
        )


def _collection_artifacts(
    family: str,
    modules: tuple[Module, ...],
    collections: tuple[Collection, ...],
    *,
    pdx_path_template: str,
    module_pdx_path_template: str | None = None,
    loc_path_template: str | None = None,
    copy_path_template: str | None = None,
    view_path_template: str | None = None,
    view_metadata: Callable[[str, Collection, tuple[Module, ...]], Mapping[str, object]] | None = None,
    include_collection_pdx: bool = False,
    member_container: str | None = None,
    aggregate_member_localization: bool = False,
) -> list[Artifact]:
    artifacts: list[Artifact] = []
    module_map = {module.module_id: module for module in modules}
    uncollected = _uncollected_modules(modules, collections)
    collected = tuple(module for module in modules if module not in uncollected)
    for collection in collections:
        if collection.family != family:
            continue
        members = tuple(module_map[module_id] for module_id in collection.module_ids if module_id in module_map)
        entries = []
        inputs: list[Path] = []
        descriptor_inputs: list[str] = []
        if include_collection_pdx:
            collection_bundle = _collection_bundle(collection)
            for source in collection_bundle.pdx_sources:
                entries.extend(entry.clone() for entry in source.block.entries)
                inputs.append(Path(collection_bundle.root) / source.path)
                descriptor_inputs.append(source.path)
        for module in members:
            bundle = _module_bundle(module)
            for source in bundle.pdx_sources:
                member_entries = [entry.clone() for entry in source.block.entries]
                if member_container:
                    container = _collection_member_container(
                        entries,
                        member_container=member_container,
                        collection_id=collection.collection_id,
                    )
                    container.entries.extend(member_entries)
                else:
                    entries.extend(member_entries)
                inputs.append(Path(bundle.root) / source.path)
        if entries:
            artifacts.append(
                Artifact(
                    path=_render_collection_path(pdx_path_template, collection),
                    artifact_type="pdx",
                    owner=f"collection:{collection.collection_id}",
                    inputs=tuple(inputs),
                    metadata=_collection_artifact_metadata(collection, descriptor_inputs),
                    payload=PDXBlock.from_entries(entries),
                )
            )
            if view_path_template and view_metadata:
                artifacts.append(
                    Artifact(
                        path=_render_collection_path(view_path_template, collection),
                        artifact_type="view",
                        owner=f"collection:{collection.collection_id}",
                        inputs=tuple(inputs),
                        target_root="build",
                        metadata=view_metadata(family, collection, members),
                    )
                )
        if aggregate_member_localization:
            artifacts.extend(
                _aggregate_collection_loc_artifacts(
                    collection,
                    members,
                    loc_path_template=loc_path_template,
                )
            )
        else:
            artifacts.extend(_collection_loc_artifacts(collection, loc_path_template=loc_path_template))
        artifacts.extend(_collection_copy_artifacts(collection, copy_path_template=copy_path_template))
    artifacts.extend(
        _module_artifacts(
            uncollected,
            pdx_path_template=module_pdx_path_template,
            loc_path_template=loc_path_template,
            copy_path_template=copy_path_template,
        )
    )
    artifacts.extend(
        _module_artifacts(
            collected,
            loc_path_template=None if aggregate_member_localization else loc_path_template,
            copy_path_template=copy_path_template,
        )
    )
    return artifacts


def _collection_member_container(
    entries: list[PDXEntry],
    *,
    member_container: str,
    collection_id: str,
) -> PDXBlock:
    matches = [entry.val for entry in entries if entry.key_str == member_container and isinstance(entry.val, PDXBlock)]
    if len(matches) != 1:
        raise ValueError(f"Collection {collection_id!r} must define exactly one " f"{member_container!r} block before member modules can be compiled.")
    return matches[0]


def _collection_copy_artifacts(collection: Collection, *, copy_path_template: str | None = None) -> list[Artifact]:
    if not copy_path_template:
        return []
    bundle = _collection_bundle(collection)
    artifacts: list[Artifact] = []
    for source in bundle.copy_sources:
        artifacts.append(
            Artifact(
                path=_render_collection_path(copy_path_template, collection, source.path, source_slot=source.slot),
                artifact_type="copy",
                owner=f"collection:{collection.collection_id}",
                inputs=(Path(bundle.root) / source.path,),
                metadata=source.to_dict(),
            )
        )
    return artifacts


def _collection_loc_artifacts(collection: Collection, *, loc_path_template: str | None = None) -> list[Artifact]:
    if not loc_path_template:
        return []
    bundle = _collection_bundle(collection)
    artifacts: list[Artifact] = []
    for language, entries in _collection_loc_groups(bundle).items():
        source_paths = tuple(sorted({Path(bundle.root) / entry.source_path for entry in entries}))
        source_slot = _source_slot(bundle.source_slots, entries[0].source_path)
        artifacts.append(
            Artifact(
                path=_render_collection_path(
                    loc_path_template,
                    collection,
                    entries[0].source_path,
                    language=language,
                    source_slot=source_slot,
                ),
                artifact_type="loc",
                owner=f"collection:{collection.collection_id}",
                inputs=source_paths,
                metadata={"language": language},
                payload=entries,
            )
        )
    return artifacts


def _aggregate_collection_loc_artifacts(
    collection: Collection,
    members: tuple[Module, ...],
    *,
    loc_path_template: str | None = None,
) -> list[Artifact]:
    """Emit collection and member localization as one collection-owned file."""

    if not loc_path_template:
        return []
    collection_bundle = _collection_bundle(collection)
    roots_and_entries = [
        (Path(collection_bundle.root), collection_bundle.loc_entries),
        *((Path(bundle.root), bundle.loc_entries) for bundle in (_module_bundle(module) for module in members)),
    ]
    entries_by_language: dict[str, list[LocalizationEntry]] = {}
    inputs_by_language: dict[str, list[Path]] = {}
    for root, entries in roots_and_entries:
        for entry in entries:
            entries_by_language.setdefault(entry.language, []).append(entry)
            source = root / entry.source_path
            inputs = inputs_by_language.setdefault(entry.language, [])
            if source not in inputs:
                inputs.append(source)
    for entries in entries_by_language.values():
        entries.sort(key=lambda entry: entry.key)
    return [
        Artifact(
            path=_render_collection_path(
                loc_path_template,
                collection,
                entries[0].source_path,
                language=language,
                source_slot="loc",
            ),
            artifact_type="loc",
            owner=f"collection:{collection.collection_id}",
            inputs=tuple(inputs_by_language[language]),
            metadata={"language": language},
            payload=tuple(entries),
        )
        for language, entries in sorted(entries_by_language.items())
        if entries
    ]


def _module_artifacts(
    modules: tuple[Module, ...],
    *,
    pdx_path_template: str | None = None,
    loc_path_template: str | None = None,
    copy_path_template: str | None = None,
    sprite_gfx_path_template: str | None = None,
    sprite_name_template: str | None = None,
    sprite_slots: tuple[str, ...] = (),
    project_id: str | None = None,
    family: str | None = None,
) -> list[Artifact]:
    artifacts: list[Artifact] = []
    sprite_sources: list[tuple[Module, ModuleSourceBundle, object, str]] = []
    for module in sorted(modules, key=lambda item: item.module_id):
        bundle = _module_bundle(module)
        if pdx_path_template:
            for source in bundle.pdx_sources:
                artifacts.append(
                    Artifact(
                        path=_render_path(
                            pdx_path_template,
                            module,
                            bundle,
                            source.path,
                            source_slot=source.slot,
                        ),
                        artifact_type="pdx",
                        owner=f"module:{module.module_id}",
                        inputs=(Path(bundle.root) / source.path,),
                        payload=source.block,
                    )
                )
        if copy_path_template:
            for source in bundle.copy_sources:
                copy_path = _render_path(
                    copy_path_template,
                    module,
                    bundle,
                    source.path,
                    source_slot=source.slot,
                )
                artifacts.append(
                    Artifact(
                        path=copy_path,
                        artifact_type="copy",
                        owner=f"module:{module.module_id}",
                        inputs=(Path(bundle.root) / source.path,),
                        metadata=source.to_dict(),
                    )
                )
                if _is_sprite_source(source, sprite_slots):
                    sprite_sources.append((module, bundle, source, copy_path))
        if loc_path_template:
            for language, entries in _loc_groups(bundle).items():
                source_paths = tuple(sorted({Path(bundle.root) / entry.source_path for entry in entries}))
                source_slot = _source_slot(bundle.source_slots, entries[0].source_path)
                artifacts.append(
                    Artifact(
                        path=_render_path(
                            loc_path_template,
                            module,
                            bundle,
                            entries[0].source_path,
                            language=language,
                            source_slot=source_slot,
                        ),
                        artifact_type="loc",
                        owner=f"module:{module.module_id}",
                        inputs=source_paths,
                        metadata={"language": language},
                        payload=entries,
                    )
                )
    if sprite_gfx_path_template and sprite_name_template and sprite_sources:
        artifact_family = family or sprite_sources[0][0].family
        artifact_project = project_id or "project"
        artifacts.extend(
            _sprite_gfx_artifacts(
                sprite_sources,
                path_template=sprite_gfx_path_template,
                name_template=sprite_name_template,
                project_id=artifact_project,
                family=artifact_family,
            )
        )
    return artifacts


def _routed_module_artifacts(
    modules: tuple[Module, ...],
    *,
    routes: Mapping[str, SourceRoute],
    settings_key: str,
    default_route: str | None = None,
    sprite_gfx_path_template: str | None = None,
    sprite_name_template: str | None = None,
    sprite_slots: tuple[str, ...] = (),
    project_id: str | None = None,
    family: str | None = None,
) -> list[Artifact]:
    artifacts: list[Artifact] = []
    sprite_sources: list[tuple[Module, ModuleSourceBundle, object, str]] = []
    for module in sorted(modules, key=lambda item: item.module_id):
        route = routes.get(_module_route(module, settings_key) or default_route or "")
        if route is None:
            continue
        if getattr(route, "emits_artifacts", True) is False:
            continue
        bundle = _module_bundle(module)
        if route.pdx_path_template:
            for source in bundle.pdx_sources:
                artifacts.append(
                    Artifact(
                        path=_render_path(
                            route.pdx_path_template,
                            module,
                            bundle,
                            source.path,
                            source_slot=source.slot,
                        ),
                        artifact_type="pdx",
                        owner=f"module:{module.module_id}",
                        inputs=(Path(bundle.root) / source.path,),
                        payload=source.block,
                    )
                )
        if route.copy_path_template:
            for source in bundle.copy_sources:
                copy_path = _render_path(
                    route.copy_path_template,
                    module,
                    bundle,
                    source.path,
                    source_slot=source.slot,
                )
                artifacts.append(
                    Artifact(
                        path=copy_path,
                        artifact_type="copy",
                        owner=f"module:{module.module_id}",
                        inputs=(Path(bundle.root) / source.path,),
                        metadata=source.to_dict(),
                    )
                )
                if _is_sprite_source(source, sprite_slots):
                    sprite_sources.append((module, bundle, source, copy_path))
        if route.loc_path_template:
            for language, entries in _loc_groups(bundle).items():
                source_paths = tuple(sorted({Path(bundle.root) / entry.source_path for entry in entries}))
                source_slot = _source_slot(bundle.source_slots, entries[0].source_path)
                artifacts.append(
                    Artifact(
                        path=_render_path(
                            route.loc_path_template,
                            module,
                            bundle,
                            entries[0].source_path,
                            language=language,
                            source_slot=source_slot,
                        ),
                        artifact_type="loc",
                        owner=f"module:{module.module_id}",
                        inputs=source_paths,
                        metadata={"language": language},
                        payload=entries,
                    )
                )
    if sprite_gfx_path_template and sprite_name_template and sprite_sources:
        artifact_family = family or sprite_sources[0][0].family
        artifact_project = project_id or "project"
        artifacts.extend(
            _sprite_gfx_artifacts(
                sprite_sources,
                path_template=sprite_gfx_path_template,
                name_template=sprite_name_template,
                project_id=artifact_project,
                family=artifact_family,
            )
        )
    return artifacts


def _is_sprite_source(source: object, sprite_slots: tuple[str, ...]) -> bool:
    if not sprite_slots:
        return False
    slot = getattr(source, "slot", None)
    return isinstance(slot, str) and slot in sprite_slots


def _sprite_gfx_artifacts(
    sprite_sources: list[tuple[Module, ModuleSourceBundle, object, str]],
    *,
    path_template: str,
    name_template: str,
    project_id: str,
    family: str,
) -> list[Artifact]:
    grouped: dict[str, list[tuple[Module, ModuleSourceBundle, object, str]]] = {}
    for module, bundle, source, texturefile in sprite_sources:
        path = _render_sprite_gfx_path(
            path_template,
            project_id=project_id,
            family=family,
            module=module,
            bundle=bundle,
            source=source,
        )
        grouped.setdefault(path, []).append((module, bundle, source, texturefile))

    artifacts: list[Artifact] = []
    module_scoped_path = _module_scoped_sprite_gfx_path(path_template)
    for path, sources in grouped.items():
        module_ids = {module.module_id for module, _bundle, _source, _texturefile in sources}
        owner = f"module:{next(iter(module_ids))}" if module_scoped_path and len(module_ids) == 1 else f"project:{project_id}"
        artifacts.append(
            Artifact(
                path=path,
                artifact_type="sprite_gfx",
                owner=owner,
                inputs=tuple(Path(bundle.root) / source.path for _module, bundle, source, _texturefile in sources),
                metadata={"family": family, "sprite_count": len(sources)},
                payload=tuple(_sprite_type(module, bundle, source, texturefile, name_template) for module, bundle, source, texturefile in sources),
            )
        )
    return artifacts


def _module_scoped_sprite_gfx_path(template: str) -> bool:
    aggregate_fields = {"family", "project_id"}
    return any(field_name not in aggregate_fields for _literal, field_name, _format, _conversion in Formatter().parse(template) if field_name)


def _render_sprite_gfx_path(
    template: str,
    *,
    project_id: str,
    family: str,
    module: Module,
    bundle: ModuleSourceBundle,
    source: object,
) -> str:
    source_path = str(getattr(source, "path", ""))
    source_file = Path(source_path)
    source_slot = str(getattr(source, "slot", "")) or ""
    return template.format(
        project_id=project_id,
        family=family,
        module_id=module.module_id,
        object_id=_module_object_id(module, bundle),
        source_path=source_path,
        source_name=source_file.name,
        source_stem=source_file.stem,
        source_suffix=source_file.suffix,
        source_slot=source_slot,
        slot=source_slot,
    )


def _sprite_type(
    module: Module,
    bundle: ModuleSourceBundle,
    source: object,
    texturefile: str,
    sprite_name_template: str,
) -> SpriteType:
    return SpriteType(
        name=_render_sprite_name(sprite_name_template, module, bundle, source),
        texturefile=texturefile,
    )


def _render_sprite_name(template: str, module: Module, bundle: ModuleSourceBundle, source: object) -> str:
    source_path = str(getattr(source, "path", ""))
    source_file = Path(source_path)
    source_slot = str(getattr(source, "slot", "")) or ""
    return template.format(
        family=module.family,
        module_id=module.module_id,
        object_id=_module_object_id(module, bundle),
        source_path=source_path,
        source_name=source_file.name,
        source_stem=source_file.stem,
        source_suffix=source_file.suffix,
        source_slot=source_slot,
        slot=source_slot,
    )


def _uncollected_modules(modules: tuple[Module, ...], collections: tuple[Collection, ...]) -> tuple[Module, ...]:
    collected = {module_id for collection in collections if collection.family in {module.family for module in modules} for module_id in collection.module_ids}
    return tuple(module for module in modules if module.module_id not in collected)


def _focus_collection_diagnostics(family: str, modules: tuple[Module, ...], collections: tuple[Collection, ...]) -> tuple[Diagnostic, ...]:
    module_map = {module.module_id: module for module in modules}
    focus_records = [_focus_record(module) for module in modules]
    focus_ids = {record.focus_id for record in focus_records if record.focus_id}
    diagnostics: list[Diagnostic] = []

    for collection in collections:
        if collection.family != family:
            continue
        seen: dict[str, str] = {}
        for module_id in collection.module_ids:
            module = module_map.get(module_id)
            if module is None:
                continue
            record = _focus_record(module)
            focus_id = record.focus_id
            if not focus_id:
                continue
            previous = seen.get(focus_id)
            if previous:
                diagnostics.append(
                    Diagnostic(
                        code="focus.duplicate_id",
                        message=f"Focus id {focus_id} is declared by {previous} and {module.module_id}.",
                        severity="error",
                        module_id=module.module_id,
                        source_path=record.source_path,
                        span=record.focus_id_span,
                    )
                )
                continue
            seen[focus_id] = module.module_id

    for record in focus_records:
        focus_id = record.focus_id
        for prerequisite in record.prerequisites:
            if prerequisite.focus_id not in focus_ids:
                diagnostics.append(
                    Diagnostic(
                        code="focus.missing_prerequisite",
                        message=f"Focus {focus_id} prerequisite {prerequisite.focus_id} does not resolve to a project focus.",
                        severity="error",
                        module_id=record.module_id,
                        source_path=record.source_path,
                        span=prerequisite.span,
                    )
                )
        diagnostics.extend(_focus_localization_diagnostics(module_map, record))
    return tuple(diagnostics)


def _focus_localization_diagnostics(module_map: dict[str, Module], record: _FocusRecord) -> tuple[Diagnostic, ...]:
    focus_id = record.focus_id
    if not focus_id:
        return ()
    bundle = _module_bundle(module_map[record.module_id])
    if not bundle.loc_entries:
        return ()
    diagnostics: list[Diagnostic] = []
    languages = sorted({entry.language for entry in bundle.loc_entries})
    keys = {(entry.language, entry.key) for entry in bundle.loc_entries}
    for language in languages:
        for key in (focus_id, f"{focus_id}_desc"):
            if (language, key) in keys:
                continue
            diagnostics.append(
                Diagnostic(
                    code="focus.missing_localization",
                    message=f"Focus {focus_id} missing localization key {key!r} for {language}.",
                    severity="error",
                    module_id=record.module_id,
                    slot="loc",
                    source_path=record.source_path,
                    span=record.focus_id_span,
                )
            )
    return tuple(diagnostics)


def _focus_record(module: Module) -> _FocusRecord:
    bundle = _module_bundle(module)
    for source in bundle.pdx_sources:
        for entry in source.block.entries:
            if entry.key_str != "focus" or not isinstance(entry.val, PDXBlock):
                continue
            focus_entry = entry.val.find("id")
            focus_value = focus_entry.val if focus_entry else None
            focus_id = _text_value(focus_value)
            return _FocusRecord(
                module_id=module.module_id,
                source_path=source.path,
                focus_id=focus_id,
                focus_id_span=_text_span(focus_value),
                prerequisites=_focus_prerequisites(entry.val),
            )
    return _FocusRecord(module_id=module.module_id, source_path=None, focus_id=None)


def _focus_prerequisites(block: PDXBlock) -> tuple[_FocusReference, ...]:
    prerequisites: list[_FocusReference] = []
    for entry in block.find_all("prerequisite"):
        if not isinstance(entry.val, PDXBlock):
            continue
        for focus_entry in entry.val.find_all("focus"):
            value = _text_value(focus_entry.val)
            if value:
                prerequisites.append(_FocusReference(focus_id=value, span=_text_span(focus_entry.val)))
    return tuple(prerequisites)


def _localization_contract_diagnostics(family: object, modules: tuple[Module, ...]) -> tuple[Diagnostic, ...]:
    key_templates = _required_loc_keys(family)
    if not key_templates:
        return ()
    diagnostics: list[Diagnostic] = []
    family_name = str(getattr(family, "family", "module"))
    for module in modules:
        bundle = _module_bundle(module)
        if not bundle.loc_entries:
            continue
        object_id = _module_object_id(module, bundle)
        anchor = _localization_anchor(family, module, object_id)
        languages = sorted({entry.language for entry in bundle.loc_entries})
        keys = {(entry.language, entry.key) for entry in bundle.loc_entries}
        for language in languages:
            for key in _render_module_required_loc_keys(key_templates, module, object_id):
                if (language, key) in keys:
                    continue
                diagnostics.append(
                    Diagnostic(
                        code=f"{family_name}.missing_localization",
                        message=(f"{_family_label(family_name)} {anchor.object_id} " f"missing localization key {key!r} for {language}."),
                        severity="error",
                        module_id=module.module_id,
                        slot="loc",
                        source_path=anchor.source_path,
                        span=anchor.span,
                    )
                )
    return tuple(diagnostics)


def _collection_localization_contract_diagnostics(family: object, collections: tuple[Collection, ...]) -> tuple[Diagnostic, ...]:
    key_templates = _required_loc_keys(family)
    if not key_templates:
        return ()
    diagnostics: list[Diagnostic] = []
    family_name = str(getattr(family, "family", "collection"))
    for collection in collections:
        if collection.family != family_name:
            continue
        bundle = _collection_bundle(collection)
        if not bundle.loc_entries:
            continue
        for language, entries in _collection_loc_groups(bundle).items():
            keys = {entry.key for entry in entries}
            source_path = entries[0].source_path
            source_slot = _source_slot(bundle.source_slots, source_path)
            for key in _render_collection_required_loc_keys(key_templates, collection):
                if key in keys:
                    continue
                diagnostics.append(
                    Diagnostic(
                        code=f"{family_name}.missing_localization",
                        message=f"{_family_label(family_name)} {collection.collection_id} missing localization key {key!r} for {language}.",
                        severity="error",
                        collection_id=collection.collection_id,
                        slot=source_slot,
                        source_path=source_path,
                    )
                )
    return tuple(diagnostics)


def _render_module_required_loc_keys(key_templates: tuple[str, ...], module: Module, object_id: str) -> tuple[str, ...]:
    return _render_required_loc_keys(
        key_templates,
        family=module.family,
        module_id=module.module_id,
        collection_id=module.collection_id or "",
        object_id=object_id,
    )


def _render_collection_required_loc_keys(key_templates: tuple[str, ...], collection: Collection) -> tuple[str, ...]:
    return _render_required_loc_keys(
        key_templates,
        family=collection.family,
        module_id="",
        collection_id=collection.collection_id,
        object_id=collection.collection_id,
    )


def _render_required_loc_keys(
    key_templates: tuple[str, ...],
    *,
    family: str,
    module_id: str,
    collection_id: str,
    object_id: str,
) -> tuple[str, ...]:
    return tuple(
        template.format(
            family=family,
            module_id=module_id,
            collection_id=collection_id,
            object_id=object_id,
        )
        for template in key_templates
    )


def _localization_anchor(family: object, module: Module, object_id: str) -> _LocalizationAnchor:
    anchor = _family_localization_anchor(family, module, object_id)
    if anchor is not None:
        return anchor
    bundle = _module_bundle(module)
    source_path = bundle.pdx_sources[0].path if bundle.pdx_sources else bundle.loc_entries[0].source_path
    return _LocalizationAnchor(object_id=object_id, source_path=source_path)


def _family_localization_anchor(family: object, module: Module, object_id: str) -> _LocalizationAnchor | None:
    raw_anchor = getattr(family, "localization_anchor", None)
    if not callable(raw_anchor):
        return None
    raw = raw_anchor(module, object_id)
    if isinstance(raw, _LocalizationAnchor):
        return raw
    if not isinstance(raw, Mapping):
        return None
    raw_object_id = raw.get("object_id")
    raw_source_path = raw.get("source_path")
    raw_span = raw.get("span")
    return _LocalizationAnchor(
        object_id=raw_object_id if isinstance(raw_object_id, str) and raw_object_id else object_id,
        source_path=raw_source_path if isinstance(raw_source_path, str) and raw_source_path else None,
        span=raw_span if isinstance(raw_span, dict) else None,
    )


def _family_label(family: str) -> str:
    return family.replace("_", " ").capitalize()


def _asset_contract_diagnostics(family: object, modules: tuple[Module, ...]) -> tuple[Diagnostic, ...]:
    constraints = _asset_constraints(family)
    if not constraints:
        return ()
    diagnostics: list[Diagnostic] = []
    family_name = str(getattr(family, "family", "module"))
    label = _family_label(family_name)
    for module in modules:
        bundle = _module_bundle(module)
        for source in bundle.copy_sources:
            constraint = constraints.get(source.slot)
            if not constraint:
                continue
            diagnostics.extend(_asset_format_diagnostics(family_name, label, source, constraint, module_id=module.module_id))
            diagnostics.extend(_asset_dimension_diagnostics(family_name, label, source, constraint, module_id=module.module_id))
    return tuple(diagnostics)


def _collection_asset_contract_diagnostics(family: object, collections: tuple[Collection, ...]) -> tuple[Diagnostic, ...]:
    constraints = _asset_constraints(family)
    if not constraints:
        return ()
    diagnostics: list[Diagnostic] = []
    family_name = str(getattr(family, "family", "collection"))
    label = _family_label(family_name)
    for collection in collections:
        if collection.family != family_name:
            continue
        bundle = _collection_bundle(collection)
        for source in bundle.copy_sources:
            constraint = constraints.get(source.slot)
            if not constraint:
                continue
            diagnostics.extend(
                _asset_format_diagnostics(
                    family_name,
                    label,
                    source,
                    constraint,
                    collection_id=collection.collection_id,
                )
            )
            diagnostics.extend(
                _asset_dimension_diagnostics(
                    family_name,
                    label,
                    source,
                    constraint,
                    collection_id=collection.collection_id,
                )
            )
    return tuple(diagnostics)


def _sprite_contract_diagnostics(family: object, modules: tuple[Module, ...]) -> tuple[Diagnostic, ...]:
    sprite_name_template = getattr(family, "sprite_name_template", None)
    sprite_slots = tuple(getattr(family, "sprite_slots", ()))
    if not isinstance(sprite_name_template, str) or not sprite_name_template or not sprite_slots:
        return ()
    family_name = str(getattr(family, "family", "module"))
    seen: dict[str, str] = {}
    diagnostics: list[Diagnostic] = []
    for module in sorted(modules, key=lambda item: item.module_id):
        bundle = _module_bundle(module)
        for source in bundle.copy_sources:
            if not _is_sprite_source(source, sprite_slots):
                continue
            sprite_name = _render_sprite_name(sprite_name_template, module, bundle, source)
            previous = seen.get(sprite_name)
            if previous is None:
                seen[sprite_name] = module.module_id
                continue
            diagnostics.append(
                Diagnostic(
                    code=f"{family_name}.duplicate_sprite_name",
                    message=f"Sprite name {sprite_name} is declared by {previous} and {module.module_id}.",
                    severity="error",
                    module_id=module.module_id,
                    slot=str(getattr(source, "slot", "")) or None,
                    source_path=str(getattr(source, "path", "")) or None,
                )
            )
    return tuple(diagnostics)


def _asset_format_diagnostics(
    family_name: str,
    label: str,
    source: object,
    constraint: Mapping[str, object],
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
) -> tuple[Diagnostic, ...]:
    formats = constraint.get("formats")
    if not isinstance(formats, tuple) or not formats:
        return ()
    source_format = getattr(source, "format", None)
    if source_format in formats:
        return ()
    path = str(getattr(source, "path", ""))
    slot = str(getattr(source, "slot", ""))
    if not isinstance(source_format, str) or not source_format:
        return (
            Diagnostic(
                code=f"{family_name}.asset_metadata_missing",
                message=f"{label} asset {path} for slot {slot} must expose image format metadata.",
                severity="error",
                module_id=module_id,
                collection_id=collection_id,
                slot=slot,
                source_path=path,
            ),
        )
    return (
        Diagnostic(
            code=f"{family_name}.asset_format",
            message=f"{label} asset {path} for slot {slot} format {source_format!r} must be one of: {', '.join(formats)}.",
            severity="error",
            module_id=module_id,
            collection_id=collection_id,
            slot=slot,
            source_path=path,
        ),
    )


def _asset_dimension_diagnostics(
    family_name: str,
    label: str,
    source: object,
    constraint: Mapping[str, object],
    *,
    module_id: str | None = None,
    collection_id: str | None = None,
) -> tuple[Diagnostic, ...]:
    expected_width = constraint.get("width")
    expected_height = constraint.get("height")
    if not isinstance(expected_width, int) and not isinstance(expected_height, int):
        return ()
    width = getattr(source, "width", None)
    height = getattr(source, "height", None)
    path = str(getattr(source, "path", ""))
    slot = str(getattr(source, "slot", ""))
    if not isinstance(width, int) or not isinstance(height, int):
        return (
            Diagnostic(
                code=f"{family_name}.asset_metadata_missing",
                message=f"{label} asset {path} for slot {slot} must expose image dimension metadata.",
                severity="error",
                module_id=module_id,
                collection_id=collection_id,
                slot=slot,
                source_path=path,
            ),
        )
    width_matches = not isinstance(expected_width, int) or width == expected_width
    height_matches = not isinstance(expected_height, int) or height == expected_height
    if width_matches and height_matches:
        return ()
    expected = _dimension_label(expected_width, expected_height)
    return (
        Diagnostic(
            code=f"{family_name}.asset_dimensions",
            message=f"{label} asset {path} for slot {slot} dimensions {width}x{height} must be {expected}.",
            severity="error",
            module_id=module_id,
            collection_id=collection_id,
            slot=slot,
            source_path=path,
        ),
    )


def _dimension_label(width: object, height: object) -> str:
    return f"{width if isinstance(width, int) else '*'}x{height if isinstance(height, int) else '*'}"


def _focus_tree_view_metadata(family: str, collection: Collection, modules: tuple[Module, ...]) -> dict[str, object]:
    nodes = []
    for order, module in enumerate(modules):
        record = _focus_record(module)
        if not record.focus_id:
            continue
        nodes.append(
            {
                "focus_id": record.focus_id,
                "module_id": record.module_id,
                "source_path": record.source_path,
                "span": record.focus_id_span,
                "order": order,
                "prerequisites": [prerequisite.focus_id for prerequisite in record.prerequisites],
            }
        )
    return {
        "schema": "focus-tree.view.v1",
        "collection_id": collection.collection_id,
        "family": family,
        "nodes": nodes,
    }


def _text_value(value: object) -> str | None:
    if isinstance(value, PDXScalar) and value.val is not None:
        return str(value.val)
    if isinstance(value, str):
        return value
    return None


def _text_span(value: object) -> dict[str, int] | None:
    if not isinstance(value, PDXScalar):
        return None
    span = value.anno.get("span")
    if not isinstance(span, dict):
        return None
    line = span.get("line")
    column = span.get("column")
    if isinstance(line, int) and isinstance(column, int):
        return {"line": line, "column": column}
    return None


def _module_bundle(module: Module) -> ModuleSourceBundle:
    if isinstance(module.payload, ModuleSourceBundle):
        return module.payload
    raise ValueError(f"Module {module.module_id!r} must carry a ModuleSourceBundle payload.")


def _collection_bundle(collection: Collection) -> CollectionSourceBundle:
    if isinstance(collection.payload, CollectionSourceBundle):
        return collection.payload
    return CollectionSourceBundle(
        root="",
        metadata=dict(collection.metadata),
        collection_id=collection.collection_id,
        family=collection.family,
    )


def _collection_metadata_source_path(collection: Collection) -> str:
    bundle = _collection_bundle(collection)
    if bundle.root:
        root = Path(bundle.root)
        for filename in ("meta.yaml", "collection.yaml"):
            if (root / filename).is_file():
                return filename
    return "meta.yaml"


def _collection_artifact_metadata(collection: Collection, descriptor_inputs: Sequence[str]) -> dict[str, object]:
    metadata: dict[str, object] = {"module_ids": list(collection.module_ids)}
    if descriptor_inputs:
        metadata["descriptor_inputs"] = list(descriptor_inputs)
    return metadata


def _module_object_id(module: Module, bundle: ModuleSourceBundle) -> str:
    return _metadata_text(bundle, "game_id") or _metadata_text(bundle, "object_id") or module.module_id.rsplit("/", 1)[-1] or Path(bundle.root).name


def _render_path(
    template: str,
    module: Module,
    bundle: ModuleSourceBundle,
    source_path: str,
    *,
    language: str | None = None,
    source_slot: str | None = None,
) -> str:
    source = Path(source_path)
    object_id = _module_object_id(module, bundle)
    slot = source_slot or ""
    return template.format(
        family=module.family,
        module_id=module.module_id,
        object_id=object_id,
        source_path=source_path,
        source_name=source.name,
        source_stem=source.stem,
        source_suffix=source.suffix,
        source_slot=slot,
        slot=slot,
        language=language or "",
        language_folder=_language_folder(language),
    )


def _render_collection_path(
    template: str,
    collection: Collection,
    source_path: str = "",
    *,
    language: str | None = None,
    source_slot: str | None = None,
) -> str:
    source = Path(source_path)
    slot = source_slot or ""
    return template.format(
        family=collection.family,
        collection_id=collection.collection_id,
        object_id=collection.collection_id,
        source_path=source_path,
        source_name=source.name,
        source_stem=source.stem,
        source_suffix=source.suffix,
        source_slot=slot,
        slot=slot,
        language=language or "",
        language_folder=_language_folder(language),
    )


def _source_slot(source_slots: Mapping[str, Sequence[str | Path]], source_path: str | Path) -> str | None:
    normalized = str(source_path).replace("\\", "/")
    for slot in sorted(source_slots):
        for path in source_slots[slot]:
            if normalized == str(path).replace("\\", "/"):
                return slot
    return None


def _metadata_text(bundle: ModuleSourceBundle, key: str) -> str | None:
    value = bundle.metadata.get(key)
    return value if isinstance(value, str) and value else None


def _loc_groups(bundle: ModuleSourceBundle) -> dict[str, tuple[LocalizationEntry, ...]]:
    languages = sorted({entry.language for entry in bundle.loc_entries})
    return {language: tuple(entry for entry in bundle.loc_entries if entry.language == language) for language in languages}


def _collection_loc_groups(
    bundle: CollectionSourceBundle,
) -> dict[str, tuple[LocalizationEntry, ...]]:
    languages = sorted({entry.language for entry in bundle.loc_entries})
    return {language: tuple(entry for entry in bundle.loc_entries if entry.language == language) for language in languages}


def _language_folder(language: str | None) -> str:
    if not language:
        return ""
    return language.removeprefix("l_")


def _settings_contract_diagnostics(
    family: object,
    modules: tuple[Module, ...],
    *,
    exclude: tuple[str, ...] = (),
) -> tuple[Diagnostic, ...]:
    settings_values = _settings_values(family)
    required_settings = _required_settings(family)
    if not settings_values and not required_settings:
        return ()
    excluded = set(exclude)
    diagnostics: list[Diagnostic] = []
    for module in modules:
        settings = module.metadata.get("settings")
        settings_map = settings if isinstance(settings, Mapping) else {}
        for key in required_settings:
            if key in excluded:
                continue
            value = settings_map.get(key)
            if isinstance(value, str) and value:
                continue
            diagnostics.append(
                Diagnostic(
                    code="family.missing_setting",
                    message=f"Module {module.module_id} must set settings.{key}.",
                    severity="error",
                    module_id=module.module_id,
                    source_path="meta.yaml",
                )
            )
        if not isinstance(settings, Mapping):
            continue
        for key, values in settings_values.items():
            if key in excluded or key not in settings:
                continue
            value = settings[key]
            if isinstance(value, str) and value in values:
                continue
            diagnostics.append(
                Diagnostic(
                    code="family.unsupported_setting",
                    message=(f"Module {module.module_id} settings.{key} {value!r} " f"must be one of: {', '.join(values)}."),
                    severity="error",
                    module_id=module.module_id,
                    source_path="meta.yaml",
                )
            )
    return tuple(diagnostics)


def _collection_settings_contract_diagnostics(family: object, collections: tuple[Collection, ...]) -> tuple[Diagnostic, ...]:
    settings_values = _settings_values(family)
    if not settings_values:
        return ()
    family_name = str(getattr(family, "family", "collection"))
    diagnostics: list[Diagnostic] = []
    for collection in collections:
        if collection.family != family_name:
            continue
        settings = collection.metadata.get("settings")
        if not isinstance(settings, Mapping):
            continue
        for key, values in settings_values.items():
            if key not in settings:
                continue
            value = settings[key]
            if isinstance(value, str) and value in values:
                continue
            diagnostics.append(
                Diagnostic(
                    code="family.unsupported_setting",
                    message=(f"Collection {collection.collection_id} settings.{key} {value!r} " f"must be one of: {', '.join(values)}."),
                    severity="error",
                    collection_id=collection.collection_id,
                    source_path=_collection_metadata_source_path(collection),
                )
            )
    return tuple(diagnostics)


def _settings_normalize_result(family: object, modules: tuple[Module, ...]) -> FamilyNormalizeResult:
    normalizers = _settings_normalizers(family)
    if not normalizers:
        return FamilyNormalizeResult(modules=modules)
    normalized: list[Module] = []
    diagnostics: list[Diagnostic] = []
    for module in modules:
        settings = module.metadata.get("settings")
        if not isinstance(settings, Mapping):
            normalized.append(module)
            continue
        metadata = dict(module.metadata)
        normalized_settings = dict(settings)
        changed = False
        for key, normalizer in normalizers.items():
            if key not in normalized_settings:
                continue
            try:
                value = normalizer(normalized_settings[key])
            except ValueError as error:
                message = str(error)
            except Exception as error:
                message = f"{type(error).__name__}: {error}"
            else:
                if value == normalized_settings[key]:
                    continue
                normalized_settings[key] = value
                changed = True
                continue
            diagnostics.append(
                Diagnostic(
                    code="family.invalid_setting",
                    message=f"Module {module.module_id} settings.{key} cannot be normalized: {message}.",
                    severity="error",
                    module_id=module.module_id,
                    source_path="meta.yaml",
                )
            )
            continue
        if changed:
            metadata["settings"] = normalized_settings
            normalized.append(_module_with_metadata(module, metadata))
        else:
            normalized.append(module)
    return FamilyNormalizeResult(modules=tuple(normalized), diagnostics=tuple(diagnostics))


def _module_with_metadata(module: Module, metadata: Mapping[str, object]) -> Module:
    module_metadata = dict(metadata)
    payload = module.payload
    if isinstance(payload, ModuleSourceBundle):
        payload = replace(payload, metadata=dict(module_metadata))
    return replace(module, metadata=module_metadata, payload=payload)


def _module_route(module: Module, settings_key: str) -> str | None:
    settings = module.metadata.get("settings")
    if not isinstance(settings, Mapping):
        return None
    value = settings.get(settings_key)
    return value.strip() if isinstance(value, str) and value.strip() else None


def _route_names(routes: Mapping[str, SourceRoute]) -> tuple[str, ...]:
    return tuple(sorted(routes))


def _settings_values(family: object) -> dict[str, tuple[str, ...]]:
    raw = getattr(family, "settings_values", {})
    if not isinstance(raw, Mapping):
        return {}
    values: dict[str, tuple[str, ...]] = {}
    for key, raw_values in raw.items():
        if not isinstance(key, str) or not key:
            continue
        if isinstance(raw_values, str):
            allowed = (raw_values,)
        elif isinstance(raw_values, Sequence):
            allowed = tuple(sorted({value for value in raw_values if isinstance(value, str) and value}))
        else:
            allowed = ()
        if allowed:
            values[key] = allowed
    return values


def _required_settings(family: object) -> tuple[str, ...]:
    raw = getattr(family, "required_settings", ())
    if isinstance(raw, str):
        return (raw,)
    if not isinstance(raw, Sequence):
        return ()
    return tuple(sorted({value for value in raw if isinstance(value, str) and value}))


def _required_loc_keys(family: object) -> tuple[str, ...]:
    raw = getattr(family, "required_loc_keys", ())
    if isinstance(raw, str):
        return (raw,)
    if not isinstance(raw, Sequence):
        return ()
    return tuple(value for value in raw if isinstance(value, str) and value)


def _asset_constraints(family: object) -> dict[str, Mapping[str, object]]:
    raw = getattr(family, "asset_constraints", {})
    if not isinstance(raw, Mapping):
        return {}
    constraints: dict[str, Mapping[str, object]] = {}
    for slot, raw_constraint in raw.items():
        if not isinstance(slot, str) or not slot or not isinstance(raw_constraint, Mapping):
            continue
        constraint = _asset_constraint(raw_constraint)
        if constraint:
            constraints[slot] = constraint
    return constraints


def _asset_constraint(raw: Mapping[str, object]) -> dict[str, object]:
    constraint: dict[str, object] = {}
    formats = _asset_formats(raw.get("formats", raw.get("format", ())))
    if formats:
        constraint["formats"] = formats
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


def _settings_normalizers(family: object) -> dict[str, SettingNormalizer]:
    raw = getattr(family, "settings_normalizers", {})
    if not isinstance(raw, Mapping):
        return {}
    return {key: normalizer for key, normalizer in sorted(raw.items()) if isinstance(key, str) and key and callable(normalizer)}
