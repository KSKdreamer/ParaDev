from __future__ import annotations

from types import SimpleNamespace

import pytest

from paradev.build import (
    DEFAULT_IDENTITY_REWRITER,
    BuildRegistry,
    FamilyPresentation,
    ModuleDiagramNodeAuthoring,
    ModuleDiagramNodeField,
    ModuleDiagramProvider,
    ModuleDiagramRelationship,
    ModuleDiagramSelectionDefault,
    RoutedSourceFamily,
    SimpleSourceFamily,
    Slot,
    SourceRoute,
    StaticCopyWriter,
    families_view,
)

_COMMON_METADATA_KEYS = [
    "after",
    "collection",
    "comment",
    "game_id",
    "inactive",
    "members",
    "owner",
    "priority",
    "requires",
    "settings",
    "tags",
    "title",
    "type",
]
_UNKNOWN_KEY_POLICY = {
    "code": "metadata.unknown_key",
    "loose_severity": "warning",
    "strict_severity": "error",
}


def test_registry_rejects_invalid_default_source_slots() -> None:
    with pytest.raises(
        ValueError,
        match="Build registry source_slots\\[0\\]\\.name must be a non-empty string",
    ):
        BuildRegistry(source_slots=(Slot("", "def.pdx"),))


def test_registry_rejects_invalid_default_collection_source_slots() -> None:
    with pytest.raises(
        ValueError,
        match="Build registry collection_source_slots\\[0\\]\\.match must be relative and stay under the source root",
    ):
        BuildRegistry(collection_source_slots=(Slot("def", "../outside.pdx"),))


@pytest.mark.parametrize(
    ("authoring_path", "message"),
    (
        ("../outside/{filename}", "must be relative"),
        ("gfx/{family}/{filename}", "unsupported fields: family"),
        ("gfx/{filename", "valid format placeholders"),
    ),
)
def test_registry_rejects_unsafe_resource_authoring_paths(
    authoring_path: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        BuildRegistry(
            source_slots=(
                Slot(
                    "asset",
                    "**/*.mesh",
                    kind="copy",
                    authoring_path=authoring_path,
                ),
            )
        )


def test_registry_exposes_safe_resource_authoring_paths() -> None:
    registry = BuildRegistry().add(
        SimpleSourceFamily(
            family="entity",
            source_slots=(
                Slot(
                    "asset",
                    "gfx/models/**/*.mesh",
                    kind="copy",
                    many=True,
                    authoring_path="gfx/models/{object_id}/{filename}",
                ),
            ),
        )
    )

    assert registry.to_view()["families"][0]["source_slots"] == [
        {
            "name": "asset",
            "match": "gfx/models/**/*.mesh",
            "required": False,
            "many": True,
            "regex": False,
            "kind": "copy",
            "authoring_path": "gfx/models/{object_id}/{filename}",
        }
    ]


def test_registry_requires_copy_ownership_for_resource_authoring_paths() -> None:
    with pytest.raises(ValueError, match="requires kind='copy'"):
        BuildRegistry(
            source_slots=(
                Slot(
                    "definition",
                    "def.txt",
                    kind="pdx",
                    authoring_path="{filename}",
                ),
            )
        )


def test_registry_registers_whole_plan_postprocessors_by_unique_id() -> None:
    class Postprocessor:
        postprocessor_id = "demo"

        def process(self, _ctx: object, artifacts: object) -> object:
            return artifacts

    postprocessor = Postprocessor()
    registry = BuildRegistry().add(postprocessor)

    assert registry.postprocessors == (postprocessor,)
    assert registry.to_view()["postprocessors"] == [
        {
            "postprocessor_id": "demo",
            "kind": "Postprocessor",
        }
    ]
    assert registry.to_view()["index"]["postprocessor_id"] == {"demo": [0]}
    assert registry.to_view()["index"]["postprocessor_kind"] == {"Postprocessor": [0]}
    with pytest.raises(ValueError, match="already registered"):
        registry.add(Postprocessor())


def test_registry_rejects_postprocessor_without_process_hook() -> None:
    class InvalidPostprocessor:
        postprocessor_id = "invalid"

    with pytest.raises(ValueError, match=r"must define process\(ctx, artifacts\)"):
        BuildRegistry().add(InvalidPostprocessor())


def test_registry_replaces_family_atomically_when_extension_requests_it() -> None:
    original = SimpleSourceFamily(family="idea", pdx_path_template="common/original/{object_id}.txt")
    replacement = SimpleSourceFamily(family="idea", pdx_path_template="common/replacement/{object_id}.txt")
    registry = BuildRegistry().add(original)

    registry.replace_family(replacement)

    assert registry.family("idea") is replacement
    with pytest.raises(ValueError, match="is not registered"):
        registry.replace_family(SimpleSourceFamily(family="missing"))


def test_registry_exposes_family_owned_identity_copy_capability() -> None:
    rewrite_family = SimpleSourceFamily(family="rewrite")
    preserve_family = SimpleSourceFamily(
        family="preserve",
        identity_rewriter=None,
    )
    registry = BuildRegistry().add(rewrite_family).add(preserve_family)

    assert registry.identity_rewriter_for("rewrite") is DEFAULT_IDENTITY_REWRITER
    assert registry.identity_rewriter_for("preserve") is None
    rows = {row["family"]: row for row in registry.to_view()["families"]}
    assert rows["rewrite"]["authoring"] == {
        "identity_copy": {
            "supported": True,
            "rewriter": "paradev.token-identity.v1",
        }
    }
    assert rows["preserve"]["authoring"] == {"identity_copy": {"supported": False}}


def test_registry_rejects_malformed_family_identity_rewriter() -> None:
    malformed = SimpleNamespace(
        identifier="broken",
        rewrite_path=lambda *_args: ".",
    )

    with pytest.raises(
        ValueError,
        match="identity_rewriter must define callable rewrites_content, rewrite_content",
    ):
        BuildRegistry().add(
            SimpleSourceFamily(
                family="broken",
                identity_rewriter=malformed,
            )
        )


def test_registry_resolves_open_diagram_providers_through_active_families() -> None:
    def project(_context: object) -> dict[str, object]:
        return {"nodes": []}

    def plan(
        _context: object,
        _positions: object,
        _edges: object,
    ) -> dict[str, object]:
        return {"drafts": []}

    provider = ModuleDiagramProvider(
        identifier="demo_tree",
        aliases=("demo",),
        families=("preferred", "fallback"),
        renderer="graph",
        title="Demo tree",
        project=project,
        plan=plan,
        authoring_kind="module",
        scope_authoring_kind="collection",
        initial_scope="project",
        selection_defaults=(
            ModuleDiagramSelectionDefault(
                field="parent",
                source="id",
                template="dependency = {value}",
            ),
        ),
    )
    registry = BuildRegistry().add(SimpleSourceFamily(family="fallback")).add(provider)

    resolved = registry.diagram_provider("demo", editable=True)

    assert resolved.family == "fallback"
    assert resolved.provider is provider
    assert registry.diagram_views_by_family() == {
        "fallback": {
            "id": "demo_tree",
            "aliases": ["demo"],
            "renderer": "graph",
            "title": "Demo tree",
            "editable": True,
            "authoring_kind": "module",
            "scope_authoring_kind": "collection",
            "initial_scope": "project",
            "selection_defaults": [
                {
                    "field": "parent",
                    "source": "id",
                    "template": "dependency = {value}",
                }
            ],
        }
    }
    family = registry.to_view()["families"][0]
    assert family["diagram"] == registry.diagram_views_by_family()["fallback"]
    assert registry.to_view()["index"]["diagram"] == {"demo_tree": [0]}
    assert registry.to_view()["index"]["diagram_renderer"] == {"graph": [0]}

    registry.add(SimpleSourceFamily(family="preferred"))

    assert registry.diagram_provider("demo_tree").family == "preferred"
    assert registry.diagram_views_by_family() == {"preferred": family["diagram"]}


def test_diagram_provider_rejects_unknown_initial_scope() -> None:
    with pytest.raises(
        ValueError,
        match="initial_scope must be 'project' or 'selected-entity'",
    ):
        ModuleDiagramProvider(
            identifier="demo",
            families=("demo",),
            renderer="graph",
            title="Demo",
            project=lambda _context: {},
            initial_scope="module",  # type: ignore[arg-type]
        )


def test_diagram_selection_defaults_validate_open_mapping_contract() -> None:
    assert ModuleDiagramSelectionDefault(
        field="y",
        source="y",
        offset=2,
    ).to_view() == {
        "field": "y",
        "source": "y",
        "offset": 2,
    }
    with pytest.raises(ValueError, match="exactly one plain"):
        ModuleDiagramSelectionDefault(
            field="parent",
            source="id",
            template="{value} {other}",
        )
    with pytest.raises(ValueError, match="finite number"):
        ModuleDiagramSelectionDefault(
            field="x",
            source="x",
            offset=float("nan"),
        )
    with pytest.raises(ValueError, match="must not target"):
        ModuleDiagramProvider(
            identifier="demo",
            families=("demo",),
            renderer="project",
            title="Demo",
            project=lambda _context: {},
            authoring_kind="module",
            selection_defaults=(
                ModuleDiagramSelectionDefault(field="x", source="x"),
                ModuleDiagramSelectionDefault(field="x", source="y"),
            ),
        )


def test_diagram_relationships_are_provider_owned_and_transport_neutral() -> None:
    relationship = ModuleDiagramRelationship(
        kind="any_parent",
        label="Any parent",
        visual_kind="dependency",
        selected_endpoint="target",
        owner_endpoint="target",
    )
    provider = ModuleDiagramProvider(
        identifier="demo",
        families=("demo",),
        renderer="graph",
        title="Demo",
        project=lambda _context: {},
        plan=lambda _context, _positions, _edges: {"drafts": []},
        relationships=(relationship,),
    )

    assert provider.to_view()["relationships"] == [
        {
            "kind": "any_parent",
            "label": "Any parent",
            "visual_kind": "dependency",
            "selected_endpoint": "target",
            "owner_endpoint": "target",
            "symmetric": False,
            "cardinality": "many",
        }
    ]
    with pytest.raises(ValueError, match="unique kinds"):
        ModuleDiagramProvider(
            identifier="duplicate",
            families=("demo",),
            renderer="graph",
            title="Duplicate",
            project=lambda _context: {},
            plan=lambda _context, _positions, _edges: {},
            relationships=(relationship, relationship),
        )
    with pytest.raises(ValueError, match="require an edit planner"):
        ModuleDiagramProvider(
            identifier="read_only",
            families=("demo",),
            renderer="graph",
            title="Read only",
            project=lambda _context: {},
            relationships=(relationship,),
        )
    with pytest.raises(ValueError, match="visual_kind"):
        ModuleDiagramRelationship(
            kind="bad",
            label="Bad",
            visual_kind="family-specific",
            selected_endpoint="source",
            owner_endpoint="source",
        )


def test_diagram_node_authoring_is_provider_owned_and_transport_neutral() -> None:
    authoring = ModuleDiagramNodeAuthoring(
        title="Add trait",
        description="Create a reviewed child trait.",
        fields=(
            ModuleDiagramNodeField(
                name="trait_id",
                label="Trait ID",
                required=True,
            ),
            ModuleDiagramNodeField(
                name="bonus_value",
                label="Bonus value",
                kind="number",
                default=0.05,
                advanced=True,
            ),
        ),
        selection_defaults=(
            ModuleDiagramSelectionDefault(
                field="parent_trait_id",
                source="trait_id",
            ),
            ModuleDiagramSelectionDefault(
                field="y",
                source="y",
                offset=1,
            ),
        ),
    )
    provider = ModuleDiagramProvider(
        identifier="demo",
        families=("demo",),
        renderer="project",
        title="Demo",
        project=lambda _context: {},
        node_plan=lambda _context, _intent: {"drafts": []},
        node_authoring=authoring,
        authoring_kind="diagram-node",
    )

    assert provider.to_view()["node_authoring"] == {
        "title": "Add trait",
        "description": "Create a reviewed child trait.",
        "fields": [
            {
                "name": "trait_id",
                "label": "Trait ID",
                "kind": "text",
                "required": True,
            },
            {
                "name": "bonus_value",
                "label": "Bonus value",
                "kind": "number",
                "required": False,
                "default": 0.05,
                "advanced": True,
            },
        ],
        "selection_defaults": [
            {"field": "parent_trait_id", "source": "trait_id"},
            {"field": "y", "source": "y", "offset": 1},
        ],
        "requires_selection": True,
    }
    optional_selection = ModuleDiagramNodeAuthoring(
        title="Add root trait",
        description="Create a root trait without selecting an existing node.",
        fields=(ModuleDiagramNodeField(name="trait_id", label="Trait ID"),),
        requires_selection=False,
    )
    assert optional_selection.to_view() == {
        "title": "Add root trait",
        "description": "Create a root trait without selecting an existing node.",
        "fields": [
            {
                "name": "trait_id",
                "label": "Trait ID",
                "kind": "text",
                "required": False,
            }
        ],
        "selection_defaults": [],
        "requires_selection": False,
    }
    with pytest.raises(ValueError, match="unique names"):
        ModuleDiagramNodeAuthoring(
            title="Add trait",
            description="Duplicate field contract.",
            fields=(
                ModuleDiagramNodeField(name="trait_id", label="Trait ID"),
                ModuleDiagramNodeField(name="trait_id", label="Duplicate"),
            ),
            selection_defaults=(
                ModuleDiagramSelectionDefault(
                    field="parent_trait_id",
                    source="trait_id",
                ),
            ),
        )
    with pytest.raises(TypeError, match="finite numeric defaults"):
        ModuleDiagramNodeField(
            name="bonus_value",
            label="Bonus value",
            kind="number",
            default=float("nan"),
        )
    with pytest.raises(ValueError, match="declared together"):
        ModuleDiagramProvider(
            identifier="incomplete",
            families=("demo",),
            renderer="project",
            title="Incomplete",
            project=lambda _context: {},
            node_plan=lambda _context, _intent: {},
        )
    with pytest.raises(ValueError, match="authoring_kind='diagram-node'"):
        ModuleDiagramProvider(
            identifier="wrong_kind",
            families=("demo",),
            renderer="project",
            title="Wrong kind",
            project=lambda _context: {},
            node_plan=lambda _context, _intent: {},
            node_authoring=authoring,
            authoring_kind="module",
        )


def test_registry_replaces_diagram_providers_atomically() -> None:
    provider = ModuleDiagramProvider(
        identifier="demo",
        families=("demo",),
        renderer="project",
        title="Demo",
        project=lambda _context: {},
    )
    replacement = ModuleDiagramProvider(
        identifier="demo",
        aliases=("replacement",),
        families=("demo",),
        renderer="project",
        title="Replacement",
        project=lambda _context: {},
        replaces_registered_provider=True,
    )
    registry = BuildRegistry().add(SimpleSourceFamily(family="demo")).add(provider)

    registry.replace_diagram_provider(replacement)

    assert registry.diagram_provider("replacement").provider is replacement
    with pytest.raises(ValueError, match="cannot be replaced"):
        registry.replace_diagram_provider(
            ModuleDiagramProvider(
                identifier="missing",
                families=("demo",),
                renderer="project",
                title="Missing",
                project=lambda _context: {},
            )
        )


def test_registry_inspects_compiler_generated_output_contracts() -> None:
    class EntityFamily:
        family = "entity"
        family_kind = "routed_source"
        settings_key = "asset_kind"
        routes = {"compiled_records": SourceRoute(copy_path_template="{source_path}")}
        source_slots = (
            Slot("record", "record.json"),
            Slot("assignment", "legacy/entities.json"),
        )
        generated_outputs = (
            {
                "artifact_type": "pdx",
                "description": "Compiler-generated entity definitions.",
                "owner_kinds": ("module",),
                "route": "compiled_records",
                "source_slots": ("record", "assignment"),
                "target_root": "output",
            },
        )

    view = BuildRegistry().add(EntityFamily()).to_view(artifact_type="pdx")

    assert view["families"][0]["outputs"] == [
        {
            "artifact_type": "copy",
            "template_key": "copy",
            "template": "{source_path}",
            "owner_kinds": ["module"],
            "target_root": "output",
            "route": "compiled_records",
            "route_setting": "settings.asset_kind",
        },
        {
            "artifact_type": "pdx",
            "generated": True,
            "owner_kinds": ["module"],
            "target_root": "output",
            "description": "Compiler-generated entity definitions.",
            "route": "compiled_records",
            "route_setting": "settings.asset_kind",
            "source_slots": ["record", "assignment"],
        },
    ]
    assert view["index"]["output_artifact_type"] == {"copy": [0], "pdx": [0]}


@pytest.mark.parametrize(
    ("generated_output", "message"),
    (
        (
            {
                "artifact_type": "pdx",
                "owner_kinds": ("module",),
                "route": "missing",
                "target_root": "output",
            },
            "route names unknown route 'missing'",
        ),
        (
            {
                "artifact_type": "pdx",
                "owner_kinds": ("workspace",),
                "route": "compiled_records",
                "target_root": "output",
            },
            "owner_kinds must contain only: collection, module, project",
        ),
        (
            {
                "artifact_type": "pdx",
                "owner_kinds": ("module",),
                "route": "compiled_records",
                "target_root": "output",
                "typo": True,
            },
            "uses unknown fields: typo",
        ),
    ),
)
def test_registry_rejects_invalid_generated_output_contracts(generated_output: dict[str, object], message: str) -> None:
    class EntityFamily:
        family = "entity"
        family_kind = "routed_source"
        settings_key = "asset_kind"
        routes = {"compiled_records": SourceRoute(copy_path_template="{source_path}")}
        generated_outputs = (generated_output,)

    with pytest.raises(ValueError, match=message):
        BuildRegistry().add(EntityFamily())


def test_registry_rejects_unknown_routed_source_default() -> None:
    with pytest.raises(
        ValueError,
        match="default_route must name one of: country_leader",
    ):
        BuildRegistry().add(
            RoutedSourceFamily(
                family="trait",
                routes={"country_leader": SourceRoute(pdx_path_template="common/country_leader/{object_id}.txt")},
                default_route="missing",
            )
        )


def test_families_view_wraps_registry_contract_with_authoring_paths(
    tmp_path,
) -> None:
    source_root = tmp_path / "src"
    source_root.mkdir()
    registry = BuildRegistry(source_slots=(Slot("def", "def.pdx", kind="pdx"),)).add(
        SimpleSourceFamily(
            family="modifier",
            pdx_path_template="common/modifiers/{object_id}.txt",
            metadata_keys=("scope",),
        )
    )
    registry.add(StaticCopyWriter())

    payload = families_view(
        registry,
        project_id="family_contract",
        profile="hoi4",
        project_root=tmp_path,
        source_roots=(source_root,),
        family="modifier",
        source_slot="def",
    )

    assert payload == {
        "schema": "paradev.build.families.v1",
        "project_id": "family_contract",
        "profile": "hoi4",
        "authoring": {
            "source_roots": [
                {
                    "path": str(source_root),
                    "relative_path": "src",
                    "default": True,
                }
            ],
            "module_path_template": "modules/{family}/{object_id}",
            "collection_path_template": "collections/{family}/{collection_id}",
        },
        "families": [
            {
                "family": "modifier",
                "kind": "simple_source",
                "presentation": {
                    "id": "modifier",
                    "title": "Modifier",
                    "group": "other",
                },
                "authoring": {
                    "identity_copy": {
                        "supported": True,
                        "rewriter": "paradev.token-identity.v1",
                    }
                },
                "metadata": {
                    "keys": sorted({*_COMMON_METADATA_KEYS, "scope"}),
                    "common_keys": _COMMON_METADATA_KEYS,
                    "family_keys": ["scope"],
                    "unknown_key_policy": _UNKNOWN_KEY_POLICY,
                },
                "stages": ["discover", "load", "normalize", "check", "emit"],
                "source_slots": [
                    {
                        "name": "def",
                        "match": "def.pdx",
                        "required": False,
                        "many": False,
                        "regex": False,
                        "kind": "pdx",
                    }
                ],
                "outputs": [
                    {
                        "artifact_type": "pdx",
                        "template_key": "pdx",
                        "template": "common/modifiers/{object_id}.txt",
                        "owner_kinds": ["module"],
                        "target_root": "output",
                    }
                ],
                "templates": {"pdx": "common/modifiers/{object_id}.txt"},
            }
        ],
        "writers": [{"artifact_type": "copy", "kind": "StaticCopyWriter"}],
        "postprocessors": [],
        "index": {
            "artifact_type": {"copy": [0]},
            "family": {"modifier": [0]},
            "kind": {"simple_source": [0]},
            "output_artifact_type": {"pdx": [0]},
            "presentation_group": {"other": [0]},
            "presentation_id": {"modifier": [0]},
            "source_slot": {"def": [0]},
        },
    }


def test_registry_family_visibility_is_explicit_for_hidden_families_and_defaults_public() -> None:
    registry = BuildRegistry().add(SimpleSourceFamily(family="public"))
    registry.add(SimpleSourceFamily(family="support", visible=False))

    families = {row["family"]: row for row in registry.to_view()["families"]}

    assert registry.visible_for("public") is True
    assert registry.visible_for("support") is False
    assert "visible" not in families["public"]
    assert families["support"]["visible"] is False


def test_registry_owns_family_presentation_and_resolves_declared_selectors() -> None:
    registry = BuildRegistry().add(
        SimpleSourceFamily(
            family="weather_magic",
            presentation=FamilyPresentation(
                id="weather-magic-systems",
                title="Weather Magic",
                group="events",
                aliases=("weather_magic_system",),
                title_key="modules.weatherMagic.title",
            ),
        )
    )

    assert registry.resolve_family("weather_magic") == "weather_magic"
    assert registry.resolve_family("weather-magic-systems") == "weather_magic"
    assert registry.resolve_family("weather_magic_system") == "weather_magic"
    assert registry.presentation_for("weather-magic-systems").to_view() == {
        "id": "weather-magic-systems",
        "title": "Weather Magic",
        "group": "events",
        "aliases": ["weather_magic_system"],
        "title_key": "modules.weatherMagic.title",
    }
    assert registry.to_view()["index"]["presentation_alias"] == {"weather_magic_system": [0]}


def test_registry_rejects_ambiguous_family_presentation_selectors() -> None:
    registry = BuildRegistry().add(
        SimpleSourceFamily(
            family="weather_magic",
            presentation=FamilyPresentation(
                id="weather-magic",
                title="Weather Magic",
            ),
        )
    )

    with pytest.raises(ValueError, match="already claimed"):
        registry.add(
            SimpleSourceFamily(
                family="storm_magic",
                presentation=FamilyPresentation(
                    id="weather-magic",
                    title="Storm Magic",
                ),
            )
        )


def test_registry_rejects_non_boolean_family_visibility() -> None:
    with pytest.raises(ValueError, match="visible must be a boolean"):
        BuildRegistry().add(SimpleSourceFamily(family="invalid", visible="no"))  # type: ignore[arg-type]


def test_registry_keeps_descriptor_publication_state_out_of_family_views() -> None:
    registry = BuildRegistry().add(SimpleSourceFamily(family="achievement"))
    registry.add_publication_replacements(
        "achievement",
        ("achievement_component", "achievement_asset_component"),
    )
    registry.add(SimpleSourceFamily(family="unrelated"))

    families = {row["family"]: row for row in registry.to_view()["families"]}

    assert registry.publication_replacements_for("achievement") == (
        "achievement_asset_component",
        "achievement_component",
    )
    assert "publication" not in families["achievement"]
    assert "replaces_families" not in families["achievement"]
    assert registry.publication_replacements_for("unrelated") == ()


def test_registry_rejects_compiler_owned_publication_state() -> None:
    with pytest.raises(
        ValueError,
        match="must keep publication replacement state in its extension descriptor",
    ):
        BuildRegistry().add(
            SimpleNamespace(
                family="achievement",
                retired_families=("achievement_component",),
            )
        )


def test_registry_rejects_unsafe_descriptor_publication_claims() -> None:
    self_replacement = BuildRegistry().add(SimpleSourceFamily(family="achievement"))
    with pytest.raises(ValueError, match="cannot include itself"):
        self_replacement.add_publication_replacements(
            "achievement",
            ("achievement",),
        )

    successor_first = BuildRegistry().add(SimpleSourceFamily(family="achievement"))
    successor_first.add_publication_replacements(
        "achievement",
        ("achievement_component",),
    )
    with pytest.raises(
        ValueError,
        match="is replaced for publication by active family 'achievement'",
    ):
        successor_first.add(SimpleSourceFamily(family="achievement_component"))

    predecessor_first = BuildRegistry().add(SimpleSourceFamily(family="achievement_component"))
    predecessor_first.add(SimpleSourceFamily(family="achievement"))
    with pytest.raises(
        ValueError,
        match="cannot name active families: achievement_component",
    ):
        predecessor_first.add_publication_replacements(
            "achievement",
            ("achievement_component",),
        )

    successor_first.add(SimpleSourceFamily(family="other"))
    with pytest.raises(
        ValueError,
        match="is already replaced by active family 'achievement'",
    ):
        successor_first.add_publication_replacements(
            "other",
            ("achievement_component",),
        )

    with pytest.raises(
        ValueError,
        match="already declares publication replacement state",
    ):
        successor_first.add_publication_replacements(
            "achievement",
            ("legacy_achievement",),
        )
