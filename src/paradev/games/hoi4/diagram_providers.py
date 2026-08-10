"""Registered HoI4 source-backed module-diagram providers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from heavenbase.utils import sha256hash

from paradev._module_diagram_contract import MAX_FOCUS_TREE_NODE_CREATION_OCCUPIED_PATHS
from paradev.build import (
    CollectionSourceBundle,
    ModuleDiagramContext,
    ModuleDiagramNodeAuthoring,
    ModuleDiagramNodeField,
    ModuleDiagramProvider,
    ModuleDiagramRelationship,
    ModuleDiagramSelectionDefault,
    ModuleSourceBundle,
)
from paradev.pdx import PDXBlock, PDXScalar

from ._diagram_source import stable_payload_hash
from .doctrine import (
    doctrine_diagram_projection,
    plan_doctrine_diagram_edits,
)
from .focus_tree import (
    focus_tree_diagram_projection,
    plan_focus_tree_diagram_edits,
    plan_focus_tree_node_creation,
)
from .mio import (
    mio_trait_diagram_projection,
    plan_mio_trait_creation,
    plan_mio_trait_diagram_edits,
)
from .technology import (
    plan_technology_diagram_edits,
    technology_diagram_projection,
)


def _project_technology(
    context: ModuleDiagramContext,
) -> Mapping[str, object]:
    return technology_diagram_projection(_single_slot_text_sources(context, slot="def"))


def _plan_technology(
    context: ModuleDiagramContext,
    position_intents: Sequence[Mapping[str, object]],
    edge_intents: Sequence[Mapping[str, object]],
) -> Mapping[str, object]:
    return plan_technology_diagram_edits(
        _single_slot_text_sources(context, slot="def"),
        position_intents=position_intents,
        edge_intents=edge_intents,
    )


def _project_focus_tree(
    context: ModuleDiagramContext,
) -> Mapping[str, object]:
    sources, modular = _focus_tree_sources(context)
    projection = focus_tree_diagram_projection(sources)
    if modular is not None:
        projection = _modular_focus_tree_projection(
            projection,
            context=modular,
        )
    projection = _focus_tree_localization(
        projection,
        modules=context.modules,
    )
    if modular is None:
        projection = _focus_tree_images(
            context,
            projection,
        )
    return projection


def _plan_focus_tree(
    context: ModuleDiagramContext,
    position_intents: Sequence[Mapping[str, object]],
    edge_intents: Sequence[Mapping[str, object]],
) -> Mapping[str, object]:
    sources, modular = _focus_tree_sources(context)
    positions = [dict(row) for row in position_intents]
    edges = [dict(row) for row in edge_intents]
    if modular is not None:
        positions, edges = _modular_focus_tree_intents(
            positions,
            edges,
            context=modular,
        )
    plan = plan_focus_tree_diagram_edits(
        sources,
        position_intents=positions,
        edge_intents=edges,
    )
    if modular is not None:
        return _modular_focus_tree_edit_plan(plan, context=modular)
    return plan


def _plan_focus_tree_node(
    context: ModuleDiagramContext,
    intent: Mapping[str, object],
) -> Mapping[str, object]:
    """Plan aggregate Focus creation from guarded provider resources."""

    sources = _single_slot_text_sources(context, slot="def")
    projection = focus_tree_diagram_projection(sources)
    tree_id = intent.get("tree_id")
    matching_trees = [row for row in projection.get("trees", []) if isinstance(row, Mapping) and row.get("id") == tree_id]
    source_revision = matching_trees[0].get("source_revision") if len(matching_trees) == 1 else ""
    source_path = matching_trees[0].get("source_path") if len(matching_trees) == 1 else ""
    localization_path = f"{str(source_path).rsplit('/', 1)[0]}/main.loc" if isinstance(source_path, str) and "/" in source_path else ""
    localization_sources: list[dict[str, str]] = []
    occupied_paths: set[str] = set()
    for module in context.modules:
        for relative_path in sorted(module.source_slots.get("loc", ())):
            source = context.read_module_text(module, relative_path)
            localization_sources.append({"path": source.path, "text": source.text})
        occupied_paths.update(
            context.module_source_inventory(
                module,
                maximum=MAX_FOCUS_TREE_NODE_CREATION_OCCUPIED_PATHS,
            )
        )
        if len(occupied_paths) > MAX_FOCUS_TREE_NODE_CREATION_OCCUPIED_PATHS:
            raise ValueError("Focus-tree authoring inventory exceeds the " f"{MAX_FOCUS_TREE_NODE_CREATION_OCCUPIED_PATHS}-entry safety limit.")
    matching_localizations = [row for row in localization_sources if row["path"] == localization_path]
    localization_revision = f"sha256:{sha256hash(matching_localizations[0]['text'])}" if len(matching_localizations) == 1 else ""
    return plan_focus_tree_node_creation(
        sources,
        localization_sources=localization_sources,
        intent={
            **intent,
            "source_revision": source_revision,
            "localization_source_revision": localization_revision,
        },
        occupied_paths=sorted(occupied_paths),
    )


_FOCUS_NODE_AUTHORING = ModuleDiagramNodeAuthoring(
    title="Add focus",
    description=("Create one localized focus in the selected tree. Selecting a focus " "prefills its tree, position, and parent relationships."),
    fields=(
        ModuleDiagramNodeField(
            name="tree_id",
            label="Focus tree ID",
            required=True,
            description="Existing focus-tree identifier that owns the new focus.",
        ),
        ModuleDiagramNodeField(
            name="focus_id",
            label="Focus ID",
            required=True,
            description="Stable unquoted game identifier, for example C08_NEW_DIRECTION.",
        ),
        ModuleDiagramNodeField(name="title", label="Name", required=True),
        ModuleDiagramNodeField(
            name="description",
            label="Description",
            kind="textarea",
            required=True,
        ),
        ModuleDiagramNodeField(name="x", label="X position", kind="number", default=0),
        ModuleDiagramNodeField(name="y", label="Y position", kind="number", default=0),
        ModuleDiagramNodeField(
            name="relative_position_id",
            label="Position parent",
            description="Optional focus ID used as the relative-position anchor.",
            advanced=True,
        ),
        ModuleDiagramNodeField(
            name="prerequisite_id",
            label="Prerequisite",
            description="Optional focus ID required before this focus.",
            advanced=True,
        ),
        ModuleDiagramNodeField(
            name="icon_key",
            label="Icon sprite",
            default="GFX_goal_unknown",
            advanced=True,
        ),
    ),
    selection_defaults=(
        ModuleDiagramSelectionDefault(field="tree_id", source="tree_id"),
        ModuleDiagramSelectionDefault(field="relative_position_id", source="id"),
        ModuleDiagramSelectionDefault(field="prerequisite_id", source="id"),
        ModuleDiagramSelectionDefault(field="x", source="x"),
        ModuleDiagramSelectionDefault(field="y", source="y", offset=1),
    ),
    requires_selection=False,
)


def _project_doctrine(
    context: ModuleDiagramContext,
) -> Mapping[str, object]:
    return doctrine_diagram_projection(_doctrine_sources(context))


def _plan_doctrine(
    context: ModuleDiagramContext,
    position_intents: Sequence[Mapping[str, object]],
    edge_intents: Sequence[Mapping[str, object]],
) -> Mapping[str, object]:
    return plan_doctrine_diagram_edits(
        _doctrine_sources(context),
        position_intents=position_intents,
        edge_intents=edge_intents,
    )


def _project_mio(
    context: ModuleDiagramContext,
) -> Mapping[str, object]:
    sources, source_modules = _mio_sources(context)
    projection = mio_trait_diagram_projection(sources)
    return _mio_enrichment(
        projection,
        modules=context.modules,
        source_modules=source_modules,
    )


def _plan_mio(
    context: ModuleDiagramContext,
    position_intents: Sequence[Mapping[str, object]],
    edge_intents: Sequence[Mapping[str, object]],
) -> Mapping[str, object]:
    sources, _source_modules = _mio_sources(context)
    return plan_mio_trait_diagram_edits(
        sources,
        position_intents=position_intents,
        edge_intents=edge_intents,
    )


def _plan_mio_node(
    context: ModuleDiagramContext,
    intent: Mapping[str, object],
) -> Mapping[str, object]:
    sources, source_modules = _mio_sources(context)
    localization_sources: list[dict[str, str]] = []
    for module in context.modules:
        for relative_path in sorted(module.source_slots.get("loc", ())):
            source = context.read_module_text(module, relative_path)
            localization_sources.append({"path": source.path, "text": source.text})
    source_path = intent.get("source_path")
    owner = source_modules.get(source_path) if isinstance(source_path, str) else None
    owner_localizations = tuple(owner.source_slots.get("loc", ())) if owner is not None else ()
    localization_path = context.module_source_path(owner, owner_localizations[0]) if owner is not None and len(owner_localizations) == 1 else ""
    return plan_mio_trait_creation(
        sources,
        localization_sources=localization_sources,
        localization_path=localization_path,
        intent=intent,
    )


TECHNOLOGY_DIAGRAM_PROVIDER = ModuleDiagramProvider(
    identifier="technology",
    aliases=("technologies",),
    families=("technology",),
    renderer="technology",
    title="Technology tree",
    project=_project_technology,
    plan=_plan_technology,
    authoring_kind="module",
    selection_defaults=(
        ModuleDiagramSelectionDefault(field="folder", source="folder"),
        ModuleDiagramSelectionDefault(field="x", source="x"),
        ModuleDiagramSelectionDefault(field="y", source="y", offset=2),
        ModuleDiagramSelectionDefault(
            field="dependencies",
            source="id",
            template="dependencies = {\n\t\t\t{value} = 1\n\t\t}",
        ),
    ),
    relationships=(
        ModuleDiagramRelationship(
            kind="dependency",
            label="Prerequisite",
            visual_kind="dependency",
            selected_endpoint="target",
            owner_endpoint="target",
        ),
        ModuleDiagramRelationship(
            kind="path",
            label="Unlock path",
            visual_kind="path",
            selected_endpoint="source",
            owner_endpoint="source",
        ),
    ),
)
FOCUS_TREE_DIAGRAM_PROVIDER = ModuleDiagramProvider(
    identifier="focus_tree",
    aliases=("focus_trees", "focus", "focuses"),
    families=("focus_tree", "focus"),
    renderer="focus-tree",
    title="Focus tree",
    project=_project_focus_tree,
    plan=_plan_focus_tree,
    node_plan=_plan_focus_tree_node,
    node_authoring=_FOCUS_NODE_AUTHORING,
    authoring_kind="diagram-node",
    scope_authoring_kind="collection",
    relationships=(
        ModuleDiagramRelationship(
            kind="prerequisite",
            label="Prerequisite",
            visual_kind="dependency",
            selected_endpoint="target",
            owner_endpoint="target",
        ),
        ModuleDiagramRelationship(
            kind="mutually_exclusive",
            label="Mutually exclusive",
            visual_kind="reference",
            selected_endpoint="source",
            owner_endpoint="source",
            symmetric=True,
        ),
    ),
)
DOCTRINE_DIAGRAM_PROVIDER = ModuleDiagramProvider(
    identifier="doctrine",
    aliases=("doctrines",),
    families=("doctrine",),
    renderer="doctrine",
    title="Doctrine tree",
    project=_project_doctrine,
    plan=_plan_doctrine,
    authoring_kind="module",
    selection_defaults=(
        ModuleDiagramSelectionDefault(field="diagram_x", source="x"),
        ModuleDiagramSelectionDefault(
            field="diagram_y",
            source="y",
            offset=2,
        ),
        ModuleDiagramSelectionDefault(
            field="diagram_paths",
            source="id",
            template="\n  - {value}",
        ),
    ),
    relationships=(
        ModuleDiagramRelationship(
            kind="path",
            label="Doctrine path",
            visual_kind="path",
            selected_endpoint="source",
            owner_endpoint="source",
        ),
        ModuleDiagramRelationship(
            kind="mutually_exclusive",
            label="Mutually exclusive",
            visual_kind="reference",
            selected_endpoint="source",
            owner_endpoint="source",
            symmetric=True,
        ),
    ),
)
MIO_DIAGRAM_PROVIDER = ModuleDiagramProvider(
    identifier="military_industrial_organization",
    aliases=("mio",),
    families=("military_industrial_organization",),
    renderer="mio-trait",
    title="Military Industrial Organization tree",
    project=_project_mio,
    plan=_plan_mio,
    node_plan=_plan_mio_node,
    node_authoring=ModuleDiagramNodeAuthoring(
        title="Add MIO trait",
        description=(
            "Create one localized trait in the selected organization. " "The reviewed source and parent relationship are inherited " "from the selected trait."
        ),
        fields=(
            ModuleDiagramNodeField(
                name="trait_id",
                label="Trait ID",
                required=True,
                description=("Stable unquoted game identifier, for example " "generic_mio_trait_precision_tools."),
            ),
            ModuleDiagramNodeField(
                name="title",
                label="Title",
                required=True,
                description="Reader-facing localized trait name.",
            ),
            ModuleDiagramNodeField(
                name="icon",
                label="Icon sprite",
                default="GFX_generic_mio_trait_icon_reliability",
                description="Existing HoI4 MIO trait sprite key.",
                advanced=True,
            ),
            ModuleDiagramNodeField(
                name="bonus_key",
                label="Equipment bonus",
                default="reliability",
                description="HoI4 equipment bonus modifier key.",
                advanced=True,
            ),
            ModuleDiagramNodeField(
                name="bonus_value",
                label="Bonus value",
                kind="number",
                default=0.05,
                description="Decimal modifier; use 0.05 for 5%.",
                advanced=True,
            ),
            ModuleDiagramNodeField(
                name="language",
                label="Localization language",
                default="en",
                description="HoI4 language id or short alias.",
                advanced=True,
            ),
        ),
        selection_defaults=(
            ModuleDiagramSelectionDefault(
                field="organization_id",
                source="organization_id",
            ),
            ModuleDiagramSelectionDefault(
                field="parent_trait_id",
                source="trait_id",
            ),
            ModuleDiagramSelectionDefault(
                field="source_path",
                source="source_path",
            ),
            ModuleDiagramSelectionDefault(
                field="source_revision",
                source="source_revision",
            ),
            ModuleDiagramSelectionDefault(field="x", source="x"),
            ModuleDiagramSelectionDefault(
                field="y",
                source="y",
                offset=1,
            ),
        ),
    ),
    authoring_kind="diagram-node",
    initial_scope="project",
    relationships=(
        ModuleDiagramRelationship(
            kind="relative_position",
            label="Relative-position parent",
            visual_kind="tree",
            selected_endpoint="target",
            owner_endpoint="target",
            cardinality="one",
        ),
        ModuleDiagramRelationship(
            kind="any_parent",
            label="Any parent",
            visual_kind="dependency",
            selected_endpoint="target",
            owner_endpoint="target",
        ),
        ModuleDiagramRelationship(
            kind="all_parent",
            label="All parents",
            visual_kind="dependency",
            selected_endpoint="target",
            owner_endpoint="target",
        ),
        ModuleDiagramRelationship(
            kind="mutually_exclusive",
            label="Mutually exclusive",
            visual_kind="reference",
            selected_endpoint="source",
            owner_endpoint="target",
            symmetric=True,
        ),
    ),
    show_when_source_hidden=True,
)
HOI4_DIAGRAM_PROVIDERS = (
    DOCTRINE_DIAGRAM_PROVIDER,
    FOCUS_TREE_DIAGRAM_PROVIDER,
    MIO_DIAGRAM_PROVIDER,
    TECHNOLOGY_DIAGRAM_PROVIDER,
)


def _single_slot_text_sources(
    context: ModuleDiagramContext,
    *,
    slot: str,
) -> tuple[dict[str, str], ...]:
    rows: list[dict[str, str]] = []
    for module in context.modules:
        paths = tuple(module.source_slots.get(slot, ()))
        if len(paths) != 1:
            raise ValueError(f"Module {module.module_id!r} must own exactly one canonical " f"{slot!r} source for diagram editing; found {len(paths)}.")
        source = context.read_module_text(module, paths[0])
        rows.append({"path": source.path, "text": source.text})
    return tuple(rows)


def _focus_tree_sources(
    context: ModuleDiagramContext,
) -> tuple[tuple[dict[str, str], ...], dict[str, object] | None]:
    if (
        context.family == "focus"
        and getattr(
            context.registered_family,
            "member_container",
            None,
        )
        == "focus_tree"
    ):
        return _modular_focus_tree_sources(context)
    return _single_slot_text_sources(context, slot="def"), None


def _modular_focus_tree_sources(
    context: ModuleDiagramContext,
) -> tuple[tuple[dict[str, str], ...], dict[str, object]]:
    modules_by_id = {str(module.module_id): module for module in context.modules if isinstance(module.module_id, str) and module.module_id}
    sources: list[dict[str, str]] = []
    nodes: dict[str, dict[str, object]] = {}
    module_sources: dict[str, dict[str, object]] = {}
    trees: dict[str, dict[str, object]] = {}
    assigned: set[str] = set()
    for collection in context.collections():
        bundle = collection.payload
        if not isinstance(bundle, CollectionSourceBundle):
            raise TypeError(f"Focus collection {collection.collection_id!r} has no " "normalized source bundle.")
        if len(bundle.pdx_sources) != 1:
            raise ValueError(f"Focus collection {collection.collection_id!r} must own " "exactly one def source.")
        source = bundle.pdx_sources[0]
        block = source.block.clone()
        wrappers = [entry for entry in block.entries if entry.key_str == "focus_tree" and isinstance(entry.val, PDXBlock)]
        if len(wrappers) != 1:
            raise ValueError(f"Focus collection {collection.collection_id!r} must define " "exactly one focus_tree block.")
        wrapper = wrappers[0]
        assert isinstance(wrapper.val, PDXBlock)
        tree_id_entry = wrapper.val.find("id")
        tree_id = str(tree_id_entry.val.val) if tree_id_entry is not None and isinstance(tree_id_entry.val, PDXScalar) else ""
        if not tree_id:
            raise ValueError(f"Focus collection {collection.collection_id!r} must define " "focus_tree.id.")
        member_ids = list(collection.module_ids)
        member_ids.extend(
            module_id
            for module_id, module in sorted(modules_by_id.items())
            if module.metadata.get("collection") == collection.collection_id and module_id not in member_ids
        )
        for module_id in member_ids:
            module = modules_by_id.get(module_id)
            if module is None:
                raise ValueError(f"Focus collection {collection.collection_id!r} references " f"missing module {module_id!r}.")
            assigned.add(module_id)
            if len(module.pdx_sources) != 1:
                raise ValueError(f"Focus module {module_id!r} must own exactly one def source.")
            module_source = module.pdx_sources[0]
            focus_entries = [entry for entry in module_source.block.entries if entry.key_str == "focus" and isinstance(entry.val, PDXBlock)]
            if len(focus_entries) != 1:
                raise ValueError(f"Focus module {module_id!r} must define exactly one focus block.")
            focus_entry = focus_entries[0]
            assert isinstance(focus_entry.val, PDXBlock)
            focus_id_entry = focus_entry.val.find("id")
            focus_id = str(focus_id_entry.val.val) if focus_id_entry is not None and isinstance(focus_id_entry.val, PDXScalar) else ""
            if not focus_id:
                raise ValueError(f"Focus module {module_id!r} must define focus.id.")
            if focus_id in nodes:
                raise ValueError(f"Focus id {focus_id!r} is owned by more than one module.")
            definition = context.read_module_text(
                module,
                module_source.path,
            )
            preview_paths = tuple(module.source_slots.get("preview", ()))
            image_path: str | None = None
            if preview_paths:
                if len(preview_paths) != 1:
                    raise ValueError(f"Focus module {module_id!r} owns more than one preview image.")
                image_path = context.module_source_path(
                    module,
                    preview_paths[0],
                )
            span = focus_id_entry.val.anno.get("span") if focus_id_entry is not None and isinstance(focus_id_entry.val, PDXScalar) else None
            revision = f"sha256:{sha256hash(definition.text)}"
            nodes[focus_id] = {
                "module_id": module_id,
                "collection_id": collection.collection_id,
                "tree_id": tree_id,
                "source_path": definition.path,
                "source_revision": revision,
                **({"source_span": dict(span)} if isinstance(span, Mapping) else {}),
                **({"image_path": image_path} if image_path is not None else {}),
            }
            module_sources[focus_id] = {
                "module_id": module_id,
                "tree_id": tree_id,
                "path": definition.path,
                "text": definition.text,
                "sha256": sha256hash(definition.text),
                "source_revision": revision,
            }
            wrapper.val.entries.append(focus_entry.clone())
        source_path = context.collection_source_path(bundle, source.path)
        virtual_text = block.to_str()
        virtual_revision = f"sha256:{sha256hash(virtual_text)}"
        sources.append({"path": source_path, "text": virtual_text})
        trees[tree_id] = {
            "collection_id": collection.collection_id,
            "source_path": source_path,
            "source_revision": virtual_revision,
        }
    unassigned = sorted(set(modules_by_id) - assigned)
    if unassigned:
        raise ValueError("Every modular focus must belong to one discovered focus " f"collection; unassigned: {', '.join(unassigned[:5])}.")
    return (
        tuple(sources),
        {
            "nodes": nodes,
            "module_sources": module_sources,
            "trees": trees,
        },
    )


def _modular_focus_tree_projection(
    projection: Mapping[str, object],
    *,
    context: Mapping[str, object],
) -> dict[str, object]:
    node_sources = context["nodes"] if isinstance(context.get("nodes"), Mapping) else {}
    tree_sources = context["trees"] if isinstance(context.get("trees"), Mapping) else {}
    payload = dict(projection)
    projected_nodes: list[object] = []
    for node in projection.get("nodes", []):
        if not isinstance(node, Mapping):
            projected_nodes.append(node)
            continue
        row = dict(node)
        source = node_sources.get(row.get("id"))
        if isinstance(source, Mapping):
            row.update(source)
        projected_nodes.append(row)
    projected_trees: list[object] = []
    for tree in projection.get("trees", []):
        if not isinstance(tree, Mapping):
            projected_trees.append(tree)
            continue
        row = dict(tree)
        source = tree_sources.get(row.get("id"))
        if isinstance(source, Mapping):
            row.update(source)
        projected_trees.append(row)
    payload["source_kind"] = "focus_collection_modules"
    payload["nodes"] = projected_nodes
    payload["trees"] = projected_trees
    return payload


def _modular_focus_tree_intents(
    positions: Sequence[Mapping[str, object]],
    edges: Sequence[Mapping[str, object]],
    *,
    context: Mapping[str, object],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    node_rows = context["nodes"] if isinstance(context.get("nodes"), Mapping) else {}
    tree_rows = context["trees"] if isinstance(context.get("trees"), Mapping) else {}

    def virtual_revision(focus_id: object) -> str | None:
        node = node_rows.get(focus_id)
        tree_id = node.get("tree_id") if isinstance(node, Mapping) else None
        tree = tree_rows.get(tree_id)
        revision = tree.get("source_revision") if isinstance(tree, Mapping) else None
        return revision if isinstance(revision, str) else None

    translated_positions: list[dict[str, object]] = []
    for position in positions:
        row = dict(position)
        focus_id = row.get("focus_id")
        node = node_rows.get(focus_id)
        actual_revision = node.get("source_revision") if isinstance(node, Mapping) else None
        if row.get("source_revision") == actual_revision:
            revision = virtual_revision(focus_id)
            if revision is not None:
                row["source_revision"] = revision
        translated_positions.append(row)

    translated_edges: list[dict[str, object]] = []
    for edge in edges:
        row = dict(edge)
        source_id = row.get("source_id")
        target_id = row.get("target_id")
        source = node_rows.get(source_id)
        target = node_rows.get(target_id)
        source_tree = source.get("tree_id") if isinstance(source, Mapping) else None
        target_tree = target.get("tree_id") if isinstance(target, Mapping) else None
        endpoint_revisions = {node.get("source_revision") for node in (source, target) if isinstance(node, Mapping)}
        if source_tree == target_tree and row.get("source_revision") in endpoint_revisions:
            revision = virtual_revision(source_id)
            if revision is not None:
                row["source_revision"] = revision
        translated_edges.append(row)
    return translated_positions, translated_edges


def _modular_focus_tree_edit_plan(
    plan: Mapping[str, object],
    *,
    context: Mapping[str, object],
) -> dict[str, object]:
    sources_by_focus = context["module_sources"] if isinstance(context.get("module_sources"), Mapping) else {}
    payload = dict(plan)
    drafts: list[dict[str, object]] = []
    for virtual_draft in plan.get("drafts", []):
        if not isinstance(virtual_draft, Mapping):
            continue
        text = virtual_draft.get("text")
        if not isinstance(text, str):
            continue
        block = PDXBlock.from_str(text)
        wrappers = [entry for entry in block.entries if entry.key_str == "focus_tree" and isinstance(entry.val, PDXBlock)]
        if len(wrappers) != 1:
            raise ValueError("Modular focus edit draft lost its focus_tree wrapper.")
        wrapper = wrappers[0]
        assert isinstance(wrapper.val, PDXBlock)
        for focus_entry in wrapper.val.find_all("focus"):
            if not isinstance(focus_entry.val, PDXBlock):
                continue
            id_entry = focus_entry.val.find("id")
            focus_id = str(id_entry.val.val) if id_entry is not None and isinstance(id_entry.val, PDXScalar) else ""
            source = sources_by_focus.get(focus_id)
            if not isinstance(source, Mapping):
                raise TypeError(f"Modular focus edit produced unknown focus {focus_id!r}.")
            current_text = source.get("text")
            source_path = source.get("path")
            expected_sha256 = source.get("sha256")
            if not isinstance(current_text, str) or not isinstance(source_path, str) or not isinstance(expected_sha256, str):
                raise TypeError(f"Modular focus source {focus_id!r} is incomplete.")
            updated_text = PDXBlock.from_entries([focus_entry.clone()]).to_str().rstrip() + "\n"
            if updated_text == current_text:
                continue
            digest = sha256hash(updated_text)
            drafts.append(
                {
                    "path": source_path,
                    "expected_source_revision": f"sha256:{expected_sha256}",
                    "expected_sha256": expected_sha256,
                    "text": updated_text,
                    "sha256": digest,
                    "source_revision": f"sha256:{digest}",
                }
            )
    payload["source_replacements"] = []
    payload["drafts"] = sorted(
        drafts,
        key=lambda row: str(row["path"]),
    )
    if payload.get("status") != "blocked":
        payload["status"] = "planned" if drafts else "unchanged"
    summary = payload.get("summary")
    if isinstance(summary, Mapping):
        payload["summary"] = {
            **summary,
            "replacement_count": len(drafts),
            "draft_count": len(drafts),
        }
    payload.pop("plan_hash", None)
    payload["plan_hash"] = stable_payload_hash(payload)
    return payload


def _focus_tree_localization(
    projection: Mapping[str, object],
    *,
    modules: Sequence[ModuleSourceBundle],
) -> dict[str, object]:
    node_rows = projection.get("nodes")
    if not isinstance(node_rows, list):
        return dict(projection)
    node_ids = sorted(str(row.get("id")) for row in node_rows if isinstance(row, Mapping) and isinstance(row.get("id"), str))
    entries_by_key: dict[str, dict[str, str]] = {}
    for module in sorted(
        modules,
        key=lambda row: str(row.module_id or row.root),
    ):
        for entry in sorted(
            module.loc_entries,
            key=lambda row: (row.source_path, row.language, row.key),
        ):
            if entry.text.strip():
                entries_by_key.setdefault(entry.key, {}).setdefault(
                    entry.language,
                    entry.text.strip(),
                )

    normalized_ids: dict[str, list[str]] = {}
    for node_id in node_ids:
        normalized_ids.setdefault(
            _focus_localization_key(node_id),
            [],
        ).append(node_id)

    localized_nodes: list[object] = []
    for node in node_rows:
        if not isinstance(node, Mapping):
            localized_nodes.append(node)
            continue
        row = dict(node)
        node_id = row.get("id")
        if isinstance(node_id, str):
            keys = [node_id]
            normalized_id = _focus_localization_key(node_id)
            if normalized_id != node_id and normalized_ids.get(normalized_id) == [node_id]:
                keys.append(normalized_id)
            titles = _localized_values(entries_by_key, keys)
            descriptions = _localized_values(
                entries_by_key,
                [f"{key}_desc" for key in keys],
            )
            row["name_key"] = next(
                (key for key in keys if entries_by_key.get(key)),
                node_id,
            )
            if titles:
                row["localized_titles"] = titles
            if descriptions:
                row["localized_descriptions"] = descriptions
        localized_nodes.append(row)
    payload = dict(projection)
    payload["nodes"] = localized_nodes
    return payload


def _focus_tree_images(
    context: ModuleDiagramContext,
    projection: Mapping[str, object],
) -> dict[str, object]:
    node_rows = projection.get("nodes")
    if not isinstance(node_rows, list):
        return dict(projection)
    previews_by_source: dict[str, dict[str, str]] = {}
    for module in context.modules:
        definitions = tuple(module.source_slots.get("def", ()))
        if len(definitions) != 1:
            continue
        definition = context.module_source_path(module, definitions[0])
        previews: dict[str, str] = {}
        for relative_path in module.source_slots.get(
            "node_previews",
            (),
        ):
            parts = relative_path.replace("\\", "/").split("/")
            name = parts[-1]
            if len(parts) != 2 or parts[0] != "icons" or not name.endswith(".png"):
                raise ValueError("Focus node previews must use icons/<focus_id>.png: " f"{relative_path}.")
            focus_id = name.removesuffix(".png")
            if focus_id in previews:
                raise ValueError(f"Focus tree module owns duplicate previews for {focus_id!r}.")
            previews[focus_id] = context.module_source_path(
                module,
                relative_path,
            )
        previews_by_source[definition] = previews
    enriched: list[object] = []
    for node in node_rows:
        if not isinstance(node, Mapping):
            enriched.append(node)
            continue
        row = dict(node)
        node_id = row.get("id")
        source_path = row.get("source_path")
        if isinstance(node_id, str) and isinstance(source_path, str):
            image_path = previews_by_source.get(source_path, {}).get(node_id)
            if image_path is not None:
                row["image_path"] = image_path
        enriched.append(row)
    payload = dict(projection)
    payload["nodes"] = enriched
    return payload


def _doctrine_sources(
    context: ModuleDiagramContext,
) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for module in sorted(
        context.modules,
        key=lambda row: (str(row.module_id or ""), str(row.root)),
    ):
        if not isinstance(module.module_id, str) or not module.module_id:
            raise ValueError("Every doctrine diagram source bundle must have a canonical module id.")
        family, separator, object_id = module.module_id.partition("/")
        if separator != "/" or family != context.family or not object_id:
            raise ValueError(f"Doctrine diagram received invalid module {module.module_id!r}.")
        definitions = tuple(module.source_slots.get("def", ()))
        if len(definitions) != 1:
            raise ValueError(f"Doctrine module {module.module_id!r} must own exactly one " f"canonical 'def' source; found {len(definitions)}.")
        definition = context.read_module_text(
            module,
            definitions[0],
        )
        diagram_path = ".paradev/diagram.yaml"
        diagram = context.read_optional_module_text(module, diagram_path)
        rows.append(
            {
                "object_id": object_id,
                "module_id": module.module_id,
                "definition_path": definition.path,
                "definition_text": definition.text,
                "diagram_path": (diagram.path if diagram is not None else context.module_source_path(module, diagram_path)),
                "diagram_text": (diagram.text if diagram is not None else None),
            }
        )
    return tuple(rows)


def _mio_sources(
    context: ModuleDiagramContext,
) -> tuple[
    tuple[dict[str, str], ...],
    dict[str, ModuleSourceBundle],
]:
    rows: list[dict[str, str]] = []
    source_modules: dict[str, ModuleSourceBundle] = {}
    for module in sorted(
        context.modules,
        key=lambda row: (str(row.module_id or ""), str(row.root)),
    ):
        if not isinstance(module.module_id, str) or not module.module_id:
            raise ValueError("Every MIO diagram source bundle must have a canonical module id.")
        paths = tuple(sorted(module.source_slots.get("pdx", ())))
        if not paths:
            raise ValueError(f"MIO module {module.module_id!r} must declare at least one " "'pdx' source.")
        for relative_path in paths:
            if not relative_path.replace("\\", "/").endswith(".txt"):
                raise ValueError(
                    f"MIO module {module.module_id!r} declares an invalid " f"'pdx' source {relative_path!r}; exact project-owned " ".txt sources are required."
                )
            source = context.read_module_text(module, relative_path)
            if source.path in source_modules:
                previous = source_modules[source.path]
                raise ValueError(f"MIO source {source.path!r} is declared by both " f"{previous.module_id!r} and {module.module_id!r}.")
            source_modules[source.path] = module
            rows.append({"path": source.path, "text": source.text})
    rows.sort(key=lambda row: row["path"])
    return tuple(rows), source_modules


def _mio_enrichment(
    projection: Mapping[str, object],
    *,
    modules: Sequence[ModuleSourceBundle],
    source_modules: Mapping[str, ModuleSourceBundle],
) -> dict[str, object]:
    localized: dict[str, dict[str, str]] = {}
    localization_sources: dict[
        tuple[str, str],
        list[tuple[str, str]],
    ] = {}
    localization_conflicts: set[tuple[str, str]] = set()
    module_ids: list[str] = []
    for module in sorted(
        modules,
        key=lambda row: (str(row.module_id or ""), str(row.root)),
    ):
        module_id = module.module_id
        if not isinstance(module_id, str) or not module_id:
            raise ValueError("Every MIO diagram source bundle must have a canonical module id.")
        module_ids.append(module_id)
        for entry in sorted(
            module.loc_entries,
            key=lambda row: (
                row.key,
                row.language,
                row.source_path,
                row.text,
            ),
        ):
            text = entry.text.strip()
            if not text:
                continue
            key = (entry.key, entry.language)
            existing = localized.setdefault(entry.key, {}).get(entry.language)
            localization_sources.setdefault(key, []).append((module_id, entry.source_path))
            if existing is None:
                localized[entry.key][entry.language] = text
            elif existing != text:
                localization_conflicts.add(key)

    def enrich(rows: object) -> list[object]:
        if not isinstance(rows, list):
            return []
        enriched: list[object] = []
        for value in rows:
            if not isinstance(value, Mapping):
                enriched.append(value)
                continue
            row = dict(value)
            source_path = row.get("source_path")
            if not isinstance(source_path, str):
                raise TypeError("MIO projection row has no exact source_path.")
            module = source_modules.get(source_path)
            if module is None or not isinstance(module.module_id, str):
                raise ValueError(f"MIO projection source {source_path!r} has no reviewed " "module owner.")
            row["module_id"] = module.module_id
            name_key = row.get("name_key")
            if isinstance(name_key, str):
                titles = localized.get(name_key)
                if titles:
                    row["localized_titles"] = dict(sorted(titles.items()))
            enriched.append(row)
        return enriched

    payload = dict(projection)
    organizations = enrich(projection.get("organizations"))
    nodes = enrich(projection.get("nodes"))
    payload["organizations"] = organizations
    payload["nodes"] = nodes
    payload["traits"] = [dict(row) if isinstance(row, Mapping) else row for row in nodes]
    payload["module_ids"] = sorted(set(module_ids))
    diagnostics = [dict(row) for row in projection.get("diagnostics", []) if isinstance(row, Mapping)]
    for key, language in sorted(localization_conflicts):
        diagnostics.append(
            {
                "code": "mio.localization_conflict",
                "message": (f"MIO localization key {key!r} has conflicting " f"{language!r} values across modules."),
                "severity": "error",
                "localization_key": key,
                "language": language,
                "sources": [
                    {
                        "module_id": module_id,
                        "source_path": source_path,
                    }
                    for module_id, source_path in sorted(localization_sources[(key, language)])
                ],
            }
        )
    payload["diagnostics"] = diagnostics
    payload["editable"] = bool(nodes) and not any(row.get("severity") == "error" for row in diagnostics)
    summary = projection.get("summary")
    if isinstance(summary, Mapping):
        payload["summary"] = {
            **summary,
            "module_count": len(set(module_ids)),
            "localization_conflict_count": len(localization_conflicts),
        }
    return payload


def _focus_localization_key(focus_id: str) -> str:
    return "".join(character if character.isascii() and (character.isalnum() or character == "_") else "_" for character in focus_id)


def _localized_values(
    entries_by_key: Mapping[str, Mapping[str, str]],
    keys: Sequence[str],
) -> dict[str, str]:
    values: dict[str, str] = {}
    for key in keys:
        for language, text in sorted(entries_by_key.get(key, {}).items()):
            values.setdefault(language, text)
    return values


__all__ = [
    "DOCTRINE_DIAGRAM_PROVIDER",
    "FOCUS_TREE_DIAGRAM_PROVIDER",
    "HOI4_DIAGRAM_PROVIDERS",
    "MIO_DIAGRAM_PROVIDER",
    "TECHNOLOGY_DIAGRAM_PROVIDER",
]
