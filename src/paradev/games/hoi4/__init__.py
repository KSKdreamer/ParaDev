"""Hearts of Iron IV game profile scaffolding."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from paradev.build import (
    Artifact,
    BuildContext,
    BuildRegistry,
    Collection,
    CollectionPDXFamily,
    CollectionSourceFamily,
    DEFAULT_MODULE_SLOTS,
    Diagnostic,
    FamilyPresentation,
    JsonViewWriter,
    LocalizationEntry,
    LocalizationYMLWriter,
    ModDescriptorWriter,
    Module,
    PDXBlockSource,
    PDXTextWriter,
    RoutedSourceFamily,
    SimpleSourceFamily,
    Slot,
    SourceRoute,
    SpriteGFXWriter,
    StaticCopyWriter,
)
from paradev.pdx import PDXBlock, PDXEntry, PDXScalar

from .diagram_providers import HOI4_DIAGRAM_PROVIDERS
from .doctrine import (
    DOCTRINE_DIAGRAM_PLAN_SCHEMA,
    DOCTRINE_DIAGRAM_PROJECTION_SCHEMA,
    DOCTRINE_DIAGRAM_STATE_SCHEMA,
    DoctrineEdgeIntent,
    DoctrinePositionIntent,
    DoctrineSource,
    doctrine_diagram_projection,
    plan_doctrine_diagram_edits,
)
from .mio import (
    MIO_TRAIT_CREATION_PLAN_SCHEMA,
    MIO_TRAIT_DIAGRAM_PLAN_SCHEMA,
    MIO_TRAIT_DIAGRAM_PROJECTION_SCHEMA,
    MIO_TRAIT_PROJECTION_SCHEMA,
    MIOTraitCreationIntent,
    MIOTraitEdgeIntent,
    MIOTraitLocalizationSource,
    MIOTraitPositionIntent,
    MIOTraitSource,
    mio_trait_diagram_projection,
    mio_trait_projection,
    plan_mio_trait_creation,
    plan_mio_trait_diagram_edits,
)

_DECISION_CATEGORY_PDX_PATH_TEMPLATE = "common/decisions/categories/{collection_id}.txt"
_DEFAULT_MOD_VERSION = "0.1.0"
_DEFAULT_SUPPORTED_VERSION = "1.18.*"
_IDEA_SOURCE_SLOTS = (
    Slot("def", "def.txt", kind="pdx"),
    Slot("loc", "**/*.loc", many=True, kind="loc"),
    Slot("icon", "icon.png", kind="copy"),
    Slot("icon", r"^icon\.(png|dds|tga)$", regex=True, kind="copy"),
)
_MODIFIER_SOURCE_SLOTS = (
    Slot("def", "def.txt", required=True, kind="pdx"),
    Slot("loc", "**/*.loc", many=True, kind="loc"),
    Slot("assets", r"^(gfx/interface/modifiers/.+\.dds|interface/modifiers/.+\.gfx)$", many=True, regex=True, kind="copy"),
)


@dataclass(frozen=True, slots=True)
class _DecisionRecord:
    module_id: str
    collection_id: str | None
    root: str
    source_path: str
    category_id: str | None
    category_id_span: dict[str, int] | None = None
    entries: tuple[PDXEntry, ...] = ()


@dataclass(frozen=True, slots=True)
class _DecisionEntryRecord:
    module_id: str
    source_path: str
    decision_id: str
    decision_id_span: dict[str, int] | None = None


@dataclass(frozen=True, slots=True)
class _EventRecord:
    module_id: str
    collection_id: str | None
    source_path: str | None
    event_id: str | None
    event_id_span: dict[str, int] | None = None


@dataclass(frozen=True, slots=True)
class _IdeaRecord:
    module_id: str
    object_id: str
    source_path: str
    idea_id: str
    idea_id_span: dict[str, int] | None = None
    picture: str | None = None
    picture_span: dict[str, int] | None = None


class EventFamily(CollectionSourceFamily):
    """HOI4 event namespace family."""

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Return event namespace diagnostics."""

        return (
            *super().check(ctx, modules, collections),
            *_event_diagnostics(modules, collections),
        )


class IdeaFamily(SimpleSourceFamily):
    """HOI4 idea source family."""

    def localization_anchor(self, module: Module, _object_id: str) -> dict[str, object] | None:
        """Return the source anchor for idea localization diagnostics."""

        records = _idea_records(module)
        if not records:
            return None
        record = records[0]
        return {
            "object_id": record.object_id,
            "source_path": record.source_path,
            "span": record.idea_id_span,
        }

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Return idea script, localization, and icon diagnostics."""

        return (
            *super().check(ctx, modules, collections),
            *_idea_diagnostics(modules),
        )


class DecisionFamily(CollectionSourceFamily):
    """HOI4 decision category family."""

    def check(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Diagnostic, ...]:
        """Return decision category diagnostics."""

        return (
            *super().check(ctx, modules, collections),
            *_decision_diagnostics(modules),
            *_decision_category_descriptor_diagnostics(collections),
            *_decision_category_localization_diagnostics(collections),
        )

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit merged decision category artifacts plus module side artifacts."""

        side_artifacts = tuple(artifact for artifact in super().emit(ctx, modules, collections) if artifact.artifact_type != "pdx")
        return (
            *_decision_category_artifacts(collections),
            *_decision_artifacts(self.family, modules, collections, self.pdx_path_template),
            *side_artifacts,
        )


class ModDescriptorFamily:
    """HOI4 project descriptor and launcher preview family."""

    family = "mod_descriptor"
    family_kind = "project_metadata"
    visible = False
    presentation = FamilyPresentation(
        id="mod-descriptor",
        title="Mod Descriptor",
        group="other",
    )

    def emit(
        self,
        ctx: BuildContext,
        modules: tuple[Module, ...],
        collections: tuple[Collection, ...],
    ) -> tuple[Artifact, ...]:
        """Emit project-owned descriptor artifacts."""

        fields = _mod_descriptor_fields(ctx)
        artifacts = [
            Artifact(
                path="descriptor.mod",
                artifact_type="mod_descriptor",
                owner=f"project:{ctx.project_id}",
                metadata={**fields, "launcher_preview": False},
            )
        ]
        output_root = _metadata_text(ctx.metadata, "output_root")
        if output_root:
            artifacts.append(
                Artifact(
                    path=f"launcher/{ctx.project_id}.mod",
                    artifact_type="mod_descriptor",
                    owner=f"project:{ctx.project_id}",
                    target_root="build",
                    metadata={**fields, "path": output_root, "launcher_preview": True},
                )
            )
        return tuple(artifacts)


def build_registry() -> BuildRegistry:
    """Return the initial HOI4 build registry.

    Returns:
        Build registry with scaffold source-family compilers and artifact writers.
    """

    registry = (
        BuildRegistry(source_slots=DEFAULT_MODULE_SLOTS)
        .add(
            CollectionPDXFamily(
                family="focus",
                presentation=FamilyPresentation(
                    id="focuses",
                    title="Focuses",
                    group="country",
                    title_key="modules.focuses.title",
                ),
                pdx_path_template="common/national_focus/{collection_id}.txt",
                view_path_template="views/focus-tree/{collection_id}.json",
                module_pdx_path_template="common/national_focus/{object_id}.txt",
                loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
                copy_path_template="gfx/paradev/{object_id}/{source_path}",
            )
        )
        .add(
            EventFamily(
                family="event",
                presentation=FamilyPresentation(
                    id="events",
                    title="Events",
                    group="events",
                    title_key="modules.events.title",
                ),
                pdx_path_template="events/{collection_id}.txt",
                module_pdx_path_template="events/{object_id}.txt",
                loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
                copy_path_template="gfx/paradev/{object_id}/{source_path}",
            )
        )
        .add(
            DecisionFamily(
                family="decision",
                presentation=FamilyPresentation(
                    id="decisions",
                    title="Decisions",
                    group="country",
                    title_key="modules.decisions.title",
                ),
                pdx_path_template="common/decisions/{collection_id}.txt",
                loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
                copy_path_template="gfx/paradev/{object_id}/{source_path}",
            )
        )
        .add(
            IdeaFamily(
                family="idea",
                presentation=FamilyPresentation(
                    id="ideas",
                    title="Ideas",
                    group="country",
                    title_key="modules.ideas.title",
                ),
                pdx_path_template="common/ideas/{object_id}.txt",
                loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
                copy_path_template="gfx/interface/ideas/idea_{object_id}{source_suffix}",
                sprite_gfx_path_template="interface/paradev_idea.gfx",
                sprite_name_template="GFX_idea_{object_id}",
                sprite_slots=("icon",),
                source_slots=_IDEA_SOURCE_SLOTS,
                required_loc_keys=("{object_id}", "{object_id}_desc"),
                default_assets={
                    "icon": {
                        "asset_id": "hoi4:idea/default_icon",
                        "title": "Default HoI4 idea icon",
                        "source": "builtin",
                        "path": "hoi4:idea/default_icon",
                        "editable": True,
                    }
                },
            )
        )
        .add(
            CollectionSourceFamily(
                family="modifier",
                presentation=FamilyPresentation(
                    id="modifiers",
                    title="Modifiers",
                    group="shared",
                    title_key="modules.modifiers.title",
                ),
                pdx_path_template="common/modifiers/{collection_id}.txt",
                module_pdx_path_template="common/modifiers/{object_id}.txt",
                loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
                copy_path_template="{source_path}",
                source_slots=_MODIFIER_SOURCE_SLOTS,
            )
        )
        .add(
            SimpleSourceFamily(
                family="opinion_modifier",
                presentation=FamilyPresentation(
                    id="opinion-modifiers",
                    title="Opinion Modifiers",
                    group="country",
                    title_key="modules.opinionModifiers.title",
                ),
                pdx_path_template="common/opinion_modifiers/{object_id}.txt",
                loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
                copy_path_template="gfx/paradev/{object_id}/{source_path}",
            )
        )
        .add(
            RoutedSourceFamily(
                family="trait",
                presentation=FamilyPresentation(
                    id="traits",
                    title="Traits",
                    group="country",
                    title_key="modules.traits.title",
                ),
                routes={
                    "country_leader": SourceRoute(
                        pdx_path_template="common/country_leader/{object_id}.txt",
                        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
                        copy_path_template="gfx/paradev/{object_id}/{source_path}",
                    ),
                    "scientist": SourceRoute(
                        pdx_path_template="common/scientist_traits/{object_id}.txt",
                        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
                        copy_path_template="gfx/paradev/{object_id}/{source_path}",
                    ),
                    "unit_leader": SourceRoute(
                        pdx_path_template="common/unit_leader/{object_id}.txt",
                        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
                        copy_path_template="gfx/paradev/{object_id}/{source_path}",
                    ),
                },
            )
        )
        .add(ModDescriptorFamily())
        .add(JsonViewWriter())
        .add(LocalizationYMLWriter())
        .add(ModDescriptorWriter())
        .add(PDXTextWriter())
        .add(SpriteGFXWriter())
        .add(StaticCopyWriter())
    )
    for provider in HOI4_DIAGRAM_PROVIDERS:
        registry.add(provider)
    return registry


def _mod_descriptor_fields(ctx: BuildContext) -> dict[str, object]:
    fields: dict[str, object] = {
        "name": _metadata_text(ctx.metadata, "title") or ctx.project_id,
        "version": _mod_version_text(ctx.metadata),
        "supported_version": _metadata_text(ctx.metadata, "supported_version") or _DEFAULT_SUPPORTED_VERSION,
    }
    picture = _metadata_text(ctx.metadata, "picture")
    if picture:
        fields["picture"] = picture
    remote_file_id = _metadata_text(ctx.metadata, "remote_file_id")
    if remote_file_id:
        fields["remote_file_id"] = remote_file_id
    tags = _metadata_texts(ctx.metadata, "tags")
    if tags:
        fields["tags"] = tags
    replace_path = _metadata_texts(ctx.metadata, "replace_path") or _metadata_texts(ctx.metadata, "replace_paths")
    if replace_path:
        fields["replace_path"] = replace_path
    return fields


def _mod_version_text(metadata: Mapping[str, object]) -> str:
    version = _metadata_text(metadata, "mod_version") or _DEFAULT_MOD_VERSION
    if len(version) > 1 and version[0] in {"v", "V"} and version[1].isdigit():
        return version[1:]
    return version


def _idea_diagnostics(modules: tuple[Module, ...]) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    for module in modules:
        records = _idea_records(module)
        for record in records:
            if record.idea_id != record.object_id:
                diagnostics.append(
                    Diagnostic(
                        code="idea.id_mismatch",
                        message=f"Idea id {record.idea_id} must match module object id {record.object_id}.",
                        severity="error",
                        module_id=record.module_id,
                        source_path=record.source_path,
                        span=record.idea_id_span,
                    )
                )
            if _module_has_icon(module) and record.picture and record.picture != record.object_id:
                diagnostics.append(
                    Diagnostic(
                        code="idea.picture_mismatch",
                        message=f"Idea {record.idea_id} picture {record.picture} must match icon object id {record.object_id}.",
                        severity="error",
                        module_id=record.module_id,
                        source_path=record.source_path,
                        span=record.picture_span,
                    )
                )
    return tuple(diagnostics)


def _idea_records(module: Module) -> tuple[_IdeaRecord, ...]:
    bundle = getattr(module, "payload", None)
    pdx_sources = getattr(bundle, "pdx_sources", ())
    records: list[_IdeaRecord] = []
    object_id = _module_game_id(module)
    for source in pdx_sources:
        for ideas_entry in source.block.entries:
            if ideas_entry.key_str != "ideas" or not isinstance(ideas_entry.val, PDXBlock):
                continue
            for category_entry in ideas_entry.val.entries:
                if not isinstance(category_entry.val, PDXBlock):
                    continue
                for idea_entry in category_entry.val.entries:
                    if not idea_entry.key_str or not isinstance(idea_entry.val, PDXBlock):
                        continue
                    picture_entry = idea_entry.val.find("picture")
                    picture_value = picture_entry.val if picture_entry else None
                    records.append(
                        _IdeaRecord(
                            module_id=module.module_id,
                            object_id=object_id,
                            source_path=source.path,
                            idea_id=idea_entry.key_str,
                            idea_id_span=_text_span(idea_entry.key),
                            picture=_text_value(picture_value),
                            picture_span=_text_span(picture_value),
                        )
                    )
    return tuple(records)


def _module_game_id(module: Module) -> str:
    bundle = getattr(module, "payload", None)
    metadata_sources = (module.metadata, getattr(bundle, "metadata", {}))
    for key in ("game_id", "object_id"):
        for metadata in metadata_sources:
            value = _metadata_text(metadata, key)
            if value:
                return value
    return Path(str(module.root)).name


def _metadata_text(metadata: object, key: str) -> str | None:
    if not isinstance(metadata, Mapping):
        return None
    value = metadata.get(key)
    return value if isinstance(value, str) and value else None


def _metadata_texts(metadata: object, key: str) -> tuple[str, ...]:
    if not isinstance(metadata, Mapping):
        return ()
    value = metadata.get(key)
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())


def _module_has_icon(module: Module) -> bool:
    copy_sources = getattr(getattr(module, "payload", None), "copy_sources", ())
    return any(getattr(source, "slot", None) == "icon" for source in copy_sources)


def _decision_diagnostics(modules: tuple[Module, ...]) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    decision_records = _decision_records(modules)
    for record in decision_records:
        category_id = record.category_id
        collection_id = record.collection_id
        if not collection_id:
            diagnostics.append(
                Diagnostic(
                    code="decision.missing_collection",
                    message=f"Decision module {record.module_id} must set collection to the decision category id.",
                    severity="error",
                    module_id=record.module_id,
                    source_path="meta.yaml",
                )
            )
            continue
        if not category_id or category_id == collection_id:
            continue
        diagnostics.append(
            Diagnostic(
                code="decision.category_mismatch",
                message=f"Decision category {category_id} must match collection {collection_id}.",
                severity="error",
                module_id=record.module_id,
                source_path=record.source_path,
                span=record.category_id_span,
            )
        )
    diagnostics.extend(_duplicate_decision_diagnostics(decision_records))
    return tuple(diagnostics)


def _duplicate_decision_diagnostics(records: tuple[_DecisionRecord, ...]) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    seen: dict[str, str] = {}
    for record in records:
        for entry in _decision_entries(record):
            previous = seen.get(entry.decision_id)
            if previous:
                diagnostics.append(
                    Diagnostic(
                        code="decision.duplicate_id",
                        message=f"Decision id {entry.decision_id} is declared by {previous} and {entry.module_id}.",
                        severity="error",
                        module_id=entry.module_id,
                        source_path=entry.source_path,
                        span=entry.decision_id_span,
                    )
                )
                continue
            seen[entry.decision_id] = entry.module_id
    return tuple(diagnostics)


def _decision_entries(record: _DecisionRecord) -> tuple[_DecisionEntryRecord, ...]:
    return tuple(
        _DecisionEntryRecord(
            module_id=record.module_id,
            source_path=record.source_path,
            decision_id=entry.key_str,
            decision_id_span=_text_span(entry.key),
        )
        for entry in record.entries
        if entry.key_str
    )


def _decision_category_descriptor_diagnostics(collections: tuple[Collection, ...]) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    for collection in collections:
        if collection.family != "decision":
            continue
        for source in _collection_pdx_sources(collection):
            for entry in source.block.entries:
                category_id = entry.key_str
                if not category_id or category_id == collection.collection_id:
                    continue
                diagnostics.append(
                    Diagnostic(
                        code="decision.category_descriptor_mismatch",
                        message=(f"Decision category descriptor {category_id} " f"must match collection {collection.collection_id}."),
                        severity="error",
                        collection_id=collection.collection_id,
                        source_path=source.path,
                        span=_text_span(entry.key),
                    )
                )
    return tuple(diagnostics)


def _decision_category_artifacts(collections: tuple[Collection, ...]) -> tuple[Artifact, ...]:
    artifacts: list[Artifact] = []
    for collection in collections:
        if collection.family != "decision":
            continue
        bundle = getattr(collection, "payload", None)
        root = Path(str(getattr(bundle, "root", "")))
        for source in _collection_pdx_sources(collection):
            if not source.block.entries:
                continue
            artifacts.append(
                Artifact(
                    path=_DECISION_CATEGORY_PDX_PATH_TEMPLATE.format(collection_id=collection.collection_id),
                    artifact_type="pdx",
                    owner=f"collection:{collection.collection_id}",
                    inputs=(root / source.path,),
                    metadata={"source_path": source.path},
                    payload=source.block,
                )
            )
    return tuple(artifacts)


def _decision_category_localization_diagnostics(collections: tuple[Collection, ...]) -> tuple[Diagnostic, ...]:
    diagnostics: list[Diagnostic] = []
    for collection in collections:
        if collection.family != "decision":
            continue
        entries = _collection_loc_entries(collection)
        if not entries:
            continue
        languages = sorted({entry.language for entry in entries})
        keys = {(entry.language, entry.key) for entry in entries}
        for language in languages:
            source_path = next(entry.source_path for entry in entries if entry.language == language)
            for key in (collection.collection_id, f"{collection.collection_id}_desc"):
                if (language, key) in keys:
                    continue
                diagnostics.append(
                    Diagnostic(
                        code="decision.category_missing_localization",
                        message=f"Decision category {collection.collection_id} missing localization key {key!r} for {language}.",
                        severity="error",
                        collection_id=collection.collection_id,
                        slot="loc",
                        source_path=source_path,
                    )
                )
    return tuple(diagnostics)


def _collection_pdx_sources(collection: Collection) -> tuple[PDXBlockSource, ...]:
    return tuple(getattr(getattr(collection, "payload", None), "pdx_sources", ()))


def _collection_loc_entries(collection: Collection) -> tuple[LocalizationEntry, ...]:
    return tuple(getattr(getattr(collection, "payload", None), "loc_entries", ()))


def _decision_artifacts(
    family: str,
    modules: tuple[Module, ...],
    collections: tuple[Collection, ...],
    path_template: str,
) -> tuple[Artifact, ...]:
    module_map = {module.module_id: module for module in modules}
    records = _decision_records(modules)
    artifacts: list[Artifact] = []
    for collection in collections:
        if collection.family != family:
            continue
        collection_records = tuple(
            record for record in records if record.collection_id == collection.collection_id and record.module_id in collection.module_ids
        )
        entries = [entry.clone() for record in collection_records for entry in record.entries]
        if not entries:
            continue
        inputs = tuple(Path(record.root) / record.source_path for record in collection_records)
        module_ids = [module_id for module_id in collection.module_ids if module_id in module_map]
        artifacts.append(
            Artifact(
                path=path_template.format(collection_id=collection.collection_id),
                artifact_type="pdx",
                owner=f"collection:{collection.collection_id}",
                inputs=inputs,
                metadata={"module_ids": module_ids},
                payload=PDXBlock.from_entries((PDXEntry.kv(collection.collection_id, PDXBlock.from_entries(entries)),)),
            )
        )
    return tuple(artifacts)


def _decision_records(modules: tuple[Module, ...]) -> tuple[_DecisionRecord, ...]:
    records: list[_DecisionRecord] = []
    for module in modules:
        bundle = getattr(module, "payload", None)
        pdx_sources = getattr(bundle, "pdx_sources", ())
        root = str(getattr(bundle, "root", module.root))
        for source in pdx_sources:
            for entry in source.block.entries:
                category_id = entry.key_str
                if not category_id or not isinstance(entry.val, PDXBlock):
                    continue
                records.append(
                    _DecisionRecord(
                        module_id=module.module_id,
                        collection_id=module.collection_id,
                        root=root,
                        source_path=source.path,
                        category_id=category_id,
                        category_id_span=_text_span(entry.key),
                        entries=tuple(entry.val.entries),
                    )
                )
    return tuple(records)


def _event_diagnostics(modules: tuple[Module, ...], collections: tuple[Collection, ...]) -> tuple[Diagnostic, ...]:
    records = [record for module in modules for record in _event_records(module)]
    diagnostics: list[Diagnostic] = []
    seen: dict[str, str] = {}
    for record in records:
        event_id = record.event_id
        if not event_id:
            continue
        previous = seen.get(event_id)
        if previous:
            diagnostics.append(
                Diagnostic(
                    code="event.duplicate_id",
                    message=f"Event id {event_id} is declared by {previous} and {record.module_id}.",
                    severity="error",
                    module_id=record.module_id,
                    source_path=record.source_path,
                    span=record.event_id_span,
                )
            )
            continue
        seen[event_id] = record.module_id

    collection_ids = {collection.collection_id for collection in collections if collection.family == "event"}
    for record in records:
        event_id = record.event_id
        collection_id = record.collection_id
        if not event_id or not collection_id or collection_id not in collection_ids:
            continue
        namespace = event_id.split(".", 1)[0]
        if namespace == collection_id:
            continue
        diagnostics.append(
            Diagnostic(
                code="event.namespace_mismatch",
                message=f"Event id {event_id} must use namespace {collection_id}.",
                severity="error",
                module_id=record.module_id,
                source_path=record.source_path,
                span=record.event_id_span,
            )
        )
    return tuple(diagnostics)


def _event_records(module: Module) -> tuple[_EventRecord, ...]:
    bundle = getattr(module, "payload", None)
    pdx_sources = getattr(bundle, "pdx_sources", ())
    records: list[_EventRecord] = []
    for source in pdx_sources:
        for entry in source.block.entries:
            if entry.key_str not in {"country_event", "news_event"} or not isinstance(entry.val, PDXBlock):
                continue
            id_entry = entry.val.find("id")
            id_value = id_entry.val if id_entry else None
            event_id = _text_value(id_value)
            records.append(
                _EventRecord(
                    module_id=module.module_id,
                    collection_id=module.collection_id,
                    source_path=source.path,
                    event_id=event_id,
                    event_id_span=_text_span(id_value),
                )
            )
    return tuple(records)


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


def _language_folder(language: str) -> str:
    return language.removeprefix("l_")
