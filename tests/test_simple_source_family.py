from __future__ import annotations

import hashlib
from pathlib import Path
from struct import pack

from heavenbase.utils import sha256hash
import pytest

from paradev.build import (
    BuildRegistry,
    CollectionPDXFamily,
    CollectionSourceBundle,
    CollectionSourceFamily,
    Diagnostic,
    LocalizationYMLWriter,
    PDXTextWriter,
    RoutedSourceFamily,
    SimpleSourceFamily,
    Slot,
    SourceRoute,
    SpriteGFXWriter,
    StaticCopyWriter,
    load_collection_sources,
    load_module_sources,
    manifest_payloads,
    match_slots,
    plan_build,
    write_artifacts,
)
from paradev.pdx import PDXBlock


def test_simple_source_family_emits_pdx_and_copy_artifacts_from_source_bundle(tmp_path: Path) -> None:
    root = tmp_path / "GER_sample"
    (root / "copy").mkdir(parents=True)
    (root / "meta.yaml").write_text("type: focus\n", encoding="utf-8")
    (root / "def.pdx").write_text("focus = { id = GER_sample }", encoding="utf-8")
    payload = b"sample image bytes"
    (root / "copy/icon.png").write_bytes(payload)
    matched = match_slots(
        root,
        (
            Slot("def", "def.pdx", required=True),
            Slot("copy", "copy/*", many=True),
        ),
        module_id="focus/GER_sample",
    )
    bundle = load_module_sources(root, matched.source_slots, module_id="focus/GER_sample", inferred_type="focus")
    module = bundle.to_module()
    registry = (
        BuildRegistry()
        .add(
            SimpleSourceFamily(
                family="focus",
                pdx_path_template="common/simple/{object_id}.txt",
                copy_path_template="gfx/simple/{object_id}/{source_name}",
            )
        )
        .add(PDXTextWriter())
        .add(StaticCopyWriter())
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,))
    written = write_artifacts(result, registry, tmp_path / "out")

    assert [artifact.path for artifact in result.artifacts] == [
        "common/simple/GER_sample.txt",
        "gfx/simple/GER_sample/icon.png",
    ]
    assert "payload" not in module.to_dict()
    assert (tmp_path / "out/common/simple/GER_sample.txt").read_text(encoding="utf-8") == bundle.pdx_sources[0].block.to_str()
    assert (tmp_path / "out/gfx/simple/GER_sample/icon.png").read_bytes() == payload
    assert set(written) == {"common/simple/GER_sample.txt", "gfx/simple/GER_sample/icon.png"}


def test_simple_source_family_copy_template_can_use_source_suffix(tmp_path: Path) -> None:
    root = tmp_path / "GER_idea"
    root.mkdir()
    payload = b"sample dds bytes"
    (root / "meta.yaml").write_text("type: idea\n", encoding="utf-8")
    (root / "icon.dds").write_bytes(payload)
    matched = match_slots(
        root,
        (Slot("icon", r"^icon\.(png|dds|tga)$", regex=True, kind="copy"),),
        module_id="idea/GER_idea",
    )
    bundle = load_module_sources(
        root,
        matched.source_slots,
        module_id="idea/GER_idea",
        inferred_type="idea",
        slots=(Slot("icon", r"^icon\.(png|dds|tga)$", regex=True, kind="copy"),),
    )
    registry = (
        BuildRegistry().add(SimpleSourceFamily(family="idea", copy_path_template="gfx/interface/ideas/idea_{object_id}{source_suffix}")).add(StaticCopyWriter())
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(bundle.to_module(),))
    written = write_artifacts(result, registry, tmp_path / "out")

    assert [artifact.path for artifact in result.artifacts] == ["gfx/interface/ideas/idea_GER_idea.dds"]
    assert written == {"gfx/interface/ideas/idea_GER_idea.dds": tmp_path / "out/gfx/interface/ideas/idea_GER_idea.dds"}
    assert (tmp_path / "out/gfx/interface/ideas/idea_GER_idea.dds").read_bytes() == payload


def test_simple_source_family_templates_can_use_source_slot(tmp_path: Path) -> None:
    root = tmp_path / "GER_asset"
    root.mkdir()
    payload = b"sample texture bytes"
    (root / "meta.yaml").write_text("type: asset\n", encoding="utf-8")
    (root / "portrait.png").write_bytes(payload)
    matched = match_slots(root, (Slot("portrait", "portrait.png", kind="copy"),), module_id="asset/GER_asset")
    bundle = load_module_sources(
        root,
        matched.source_slots,
        module_id="asset/GER_asset",
        inferred_type="asset",
        slots=(Slot("portrait", "portrait.png", kind="copy"),),
    )
    registry = BuildRegistry().add(
        SimpleSourceFamily(
            family="asset",
            copy_path_template="gfx/{source_slot}/{object_id}{source_suffix}",
        )
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(bundle.to_module(),))

    assert [artifact.path for artifact in result.artifacts] == ["gfx/portrait/GER_asset.png"]


def test_simple_source_family_emits_aggregate_sprite_gfx_for_declared_sprite_slots(tmp_path: Path) -> None:
    modules = []
    for name in ("GER_beta", "GER_alpha"):
        root = tmp_path / name
        root.mkdir()
        (root / "meta.yaml").write_text("type: idea\n", encoding="utf-8")
        (root / "icon.dds").write_bytes(f"{name} dds bytes".encode("utf-8"))
        matched = match_slots(
            root,
            (Slot("icon", r"^icon\.(png|dds|tga)$", regex=True, kind="copy"),),
            module_id=f"idea/{name}",
        )
        bundle = load_module_sources(
            root,
            matched.source_slots,
            module_id=f"idea/{name}",
            inferred_type="idea",
            slots=(Slot("icon", r"^icon\.(png|dds|tga)$", regex=True, kind="copy"),),
        )
        modules.append(bundle.to_module())
    registry = (
        BuildRegistry()
        .add(
            SimpleSourceFamily(
                family="idea",
                copy_path_template="gfx/interface/ideas/idea_{object_id}{source_suffix}",
                sprite_gfx_path_template="interface/paradev_{family}.gfx",
                sprite_name_template="GFX_idea_{object_id}",
                sprite_slots=("icon",),
            )
        )
        .add(StaticCopyWriter())
        .add(SpriteGFXWriter())
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=tuple(modules))
    written = write_artifacts(result, registry, tmp_path / "out")

    assert [artifact.path for artifact in result.artifacts] == [
        "gfx/interface/ideas/idea_GER_alpha.dds",
        "gfx/interface/ideas/idea_GER_beta.dds",
        "interface/paradev_idea.gfx",
    ]
    assert result.artifacts[2].artifact_type == "sprite_gfx"
    assert result.artifacts[2].owner == "project:minimal_hoi4"
    assert result.artifacts[2].inputs == (
        tmp_path / "GER_alpha/icon.dds",
        tmp_path / "GER_beta/icon.dds",
    )
    assert result.artifacts[2].metadata == {"family": "idea", "sprite_count": 2}
    assert "payload" not in result.artifacts[2].to_dict()
    source_map = manifest_payloads(result)["source-map.json"]["source_map"]
    assert [{key: source[key] for key in ("module_id", "family", "slot")} for source in source_map[2]["sources"]] == [
        {"module_id": "idea/GER_alpha", "family": "idea", "slot": "icon"},
        {"module_id": "idea/GER_beta", "family": "idea", "slot": "icon"},
    ]
    assert [Path(source["path"]).name for source in source_map[2]["sources"]] == ["icon.dds", "icon.dds"]
    assert written["interface/paradev_idea.gfx"] == tmp_path / "out/interface/paradev_idea.gfx"
    assert (tmp_path / "out/interface/paradev_idea.gfx").read_text(encoding="utf-8") == (
        "spriteTypes = {\n"
        "\tSpriteType = {\n"
        '\t\tname = "GFX_idea_GER_alpha"\n'
        '\t\ttexturefile = "gfx/interface/ideas/idea_GER_alpha.dds"\n'
        "\t}\n"
        "\tSpriteType = {\n"
        '\t\tname = "GFX_idea_GER_beta"\n'
        '\t\ttexturefile = "gfx/interface/ideas/idea_GER_beta.dds"\n'
        "\t}\n"
        "}\n"
    )


def test_simple_source_family_emits_module_scoped_sprite_gfx_paths(tmp_path: Path) -> None:
    modules = []
    for name in ("SP_beta", "SP_alpha"):
        root = tmp_path / name
        root.mkdir()
        (root / "meta.yaml").write_text("type: special_project\n", encoding="utf-8")
        (root / "icon.dds").write_bytes(f"{name} dds bytes".encode("utf-8"))
        slots = (Slot("icon", r"^icon\.(png|dds|tga)$", regex=True, kind="copy"),)
        matched = match_slots(root, slots, module_id=f"special_project/{name}")
        bundle = load_module_sources(
            root,
            matched.source_slots,
            module_id=f"special_project/{name}",
            inferred_type="special_project",
            slots=slots,
        )
        modules.append(bundle.to_module())
    registry = (
        BuildRegistry()
        .add(
            SimpleSourceFamily(
                family="special_project",
                copy_path_template="gfx/interface/special_project/project_icons/{object_id}{source_suffix}",
                sprite_gfx_path_template="interface/special_projects/{object_id}.gfx",
                sprite_name_template="GFX_{object_id}",
                sprite_slots=("icon",),
            )
        )
        .add(StaticCopyWriter())
        .add(SpriteGFXWriter())
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=tuple(modules))
    written = write_artifacts(result, registry, tmp_path / "out")

    assert [artifact.path for artifact in result.artifacts] == [
        "gfx/interface/special_project/project_icons/SP_alpha.dds",
        "gfx/interface/special_project/project_icons/SP_beta.dds",
        "interface/special_projects/SP_alpha.gfx",
        "interface/special_projects/SP_beta.gfx",
    ]
    assert [artifact.owner for artifact in result.artifacts[2:]] == [
        "module:special_project/SP_alpha",
        "module:special_project/SP_beta",
    ]
    assert written["interface/special_projects/SP_alpha.gfx"] == tmp_path / "out/interface/special_projects/SP_alpha.gfx"
    assert 'name = "GFX_SP_alpha"' in (tmp_path / "out/interface/special_projects/SP_alpha.gfx").read_text(encoding="utf-8")


def test_simple_source_family_reports_duplicate_sprite_names(tmp_path: Path) -> None:
    modules = []
    for name in ("GER_alpha", "GER_beta"):
        root = tmp_path / name
        root.mkdir()
        (root / "meta.yaml").write_text("type: idea\n", encoding="utf-8")
        (root / "icon.dds").write_bytes(f"{name} dds bytes".encode("utf-8"))
        matched = match_slots(
            root,
            (Slot("icon", r"^icon\.(png|dds|tga)$", regex=True, kind="copy"),),
            module_id=f"idea/{name}",
        )
        bundle = load_module_sources(
            root,
            matched.source_slots,
            module_id=f"idea/{name}",
            inferred_type="idea",
            slots=(Slot("icon", r"^icon\.(png|dds|tga)$", regex=True, kind="copy"),),
        )
        modules.append(bundle.to_module())
    registry = (
        BuildRegistry()
        .add(
            SimpleSourceFamily(
                family="idea",
                copy_path_template="gfx/interface/ideas/idea_{object_id}{source_suffix}",
                sprite_gfx_path_template="interface/paradev_{family}.gfx",
                sprite_name_template="GFX_idea_shared",
                sprite_slots=("icon",),
            )
        )
        .add(StaticCopyWriter())
        .add(SpriteGFXWriter())
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=tuple(modules))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="idea.duplicate_sprite_name",
            message="Sprite name GFX_idea_shared is declared by idea/GER_alpha and idea/GER_beta.",
            severity="error",
            family="idea",
            module_id="idea/GER_beta",
            slot="icon",
            source_path="icon.dds",
        ),
    )


def test_simple_source_family_copy_artifact_includes_image_metadata(tmp_path: Path) -> None:
    root = tmp_path / "GER_idea"
    root.mkdir()
    payload = b"\x89PNG\r\n\x1a\n" + pack(">I4sIIBBBBBI", 13, b"IHDR", 40, 30, 8, 6, 0, 0, 0, 0)
    (root / "meta.yaml").write_text("type: idea\n", encoding="utf-8")
    (root / "icon.png").write_bytes(payload)
    matched = match_slots(
        root,
        (Slot("icon", r"^icon\.(png|dds|tga)$", regex=True, kind="copy"),),
        module_id="idea/GER_idea",
    )
    bundle = load_module_sources(
        root,
        matched.source_slots,
        module_id="idea/GER_idea",
        inferred_type="idea",
        slots=(Slot("icon", r"^icon\.(png|dds|tga)$", regex=True, kind="copy"),),
    )
    registry = BuildRegistry().add(SimpleSourceFamily(family="idea", copy_path_template="gfx/interface/ideas/idea_{object_id}{source_suffix}"))

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(bundle.to_module(),))

    assert result.artifacts[0].metadata == {
        "slot": "icon",
        "path": "icon.png",
        "output_path": "icon.png",
        "sha256": sha256hash(payload),
        "content_sha256": hashlib.sha256(payload).hexdigest(),
        "size": len(payload),
        "media_type": "image/png",
        "format": "png",
        "width": 40,
        "height": 30,
    }


def test_simple_source_family_reports_asset_constraint_diagnostics(tmp_path: Path) -> None:
    root = tmp_path / "GER_idea"
    root.mkdir()
    payload = b"\x89PNG\r\n\x1a\n" + pack(">I4sIIBBBBBI", 13, b"IHDR", 40, 30, 8, 6, 0, 0, 0, 0)
    (root / "meta.yaml").write_text("type: idea\n", encoding="utf-8")
    (root / "icon.png").write_bytes(payload)
    matched = match_slots(
        root,
        (Slot("icon", r"^icon\.(png|dds|tga)$", regex=True, kind="copy"),),
        module_id="idea/GER_idea",
    )
    bundle = load_module_sources(
        root,
        matched.source_slots,
        module_id="idea/GER_idea",
        inferred_type="idea",
        slots=(Slot("icon", r"^icon\.(png|dds|tga)$", regex=True, kind="copy"),),
    )
    registry = BuildRegistry().add(
        SimpleSourceFamily(
            family="idea",
            asset_constraints={"icon": {"formats": ("dds",), "width": 64, "height": 64}},
            copy_path_template="gfx/interface/ideas/idea_{object_id}{source_suffix}",
        )
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(bundle.to_module(),))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="idea.asset_format",
            message="Idea asset icon.png for slot icon format 'png' must be one of: dds.",
            severity="error",
            family="idea",
            module_id="idea/GER_idea",
            slot="icon",
            source_path="icon.png",
        ),
        Diagnostic(
            code="idea.asset_dimensions",
            message="Idea asset icon.png for slot icon dimensions 40x30 must be 64x64.",
            severity="error",
            family="idea",
            module_id="idea/GER_idea",
            slot="icon",
            source_path="icon.png",
        ),
    )


def test_simple_source_family_reports_missing_required_localization_keys(tmp_path: Path) -> None:
    root = tmp_path / "MODIFIER_SAMPLE"
    root.mkdir()
    (root / "meta.yaml").write_text("type: modifier\n", encoding="utf-8")
    (root / "def.pdx").write_text("MODIFIER_SAMPLE = { stability_factor = 0.05 }", encoding="utf-8")
    (root / "main.loc").write_text("en:\n  MODIFIER_SAMPLE: Sample Modifier\n", encoding="utf-8")
    matched = match_slots(
        root,
        (
            Slot("def", "def.pdx", kind="pdx"),
            Slot("loc", "*.loc", many=True, kind="loc"),
        ),
        module_id="modifier/MODIFIER_SAMPLE",
    )
    bundle = load_module_sources(
        root,
        matched.source_slots,
        module_id="modifier/MODIFIER_SAMPLE",
        inferred_type="modifier",
    )
    registry = BuildRegistry().add(
        SimpleSourceFamily(
            family="modifier",
            pdx_path_template="common/modifiers/{object_id}.txt",
            loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
            required_loc_keys=("{object_id}", "{object_id}_desc"),
        )
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(bundle.to_module(),))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="modifier.missing_localization",
            message="Modifier MODIFIER_SAMPLE missing localization key 'MODIFIER_SAMPLE_desc' for l_english.",
            severity="error",
            family="modifier",
            module_id="modifier/MODIFIER_SAMPLE",
            slot="loc",
            source_path="def.pdx",
        ),
    )


def test_collection_pdx_family_emits_collection_owned_artifact_from_member_modules(tmp_path: Path) -> None:
    first_root = tmp_path / "GER_rhineland"
    second_root = tmp_path / "GER_sample"
    first_root.mkdir()
    second_root.mkdir()
    (first_root / "meta.yaml").write_text("type: focus\ncollection: GER_main\n", encoding="utf-8")
    (second_root / "meta.yaml").write_text("type: focus\ncollection: GER_main\nafter: [focus:GER_rhineland]\n", encoding="utf-8")
    (first_root / "def.pdx").write_text("focus = { id = GER_rhineland }", encoding="utf-8")
    (second_root / "def.pdx").write_text("focus = { id = GER_sample }", encoding="utf-8")
    first = load_module_sources(
        first_root,
        match_slots(first_root, (Slot("def", "def.pdx"),), module_id="focus/GER_rhineland").source_slots,
        module_id="focus/GER_rhineland",
        inferred_type="focus",
    ).to_module()
    second = load_module_sources(
        second_root,
        match_slots(second_root, (Slot("def", "def.pdx"),), module_id="focus/GER_sample").source_slots,
        module_id="focus/GER_sample",
        inferred_type="focus",
    ).to_module()
    registry = BuildRegistry().add(CollectionPDXFamily(family="focus", pdx_path_template="common/national_focus/{collection_id}.txt")).add(PDXTextWriter())

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(second, first))
    written = write_artifacts(result, registry, tmp_path / "out")

    assert [artifact.path for artifact in result.artifacts] == ["common/national_focus/GER_main.txt"]
    assert result.artifacts[0].owner == "collection:GER_main"
    assert [str(path) for path in result.artifacts[0].inputs] == [
        str(first_root / "def.pdx"),
        str(second_root / "def.pdx"),
    ]
    assert written == {"common/national_focus/GER_main.txt": tmp_path / "out/common/national_focus/GER_main.txt"}
    assert (tmp_path / "out/common/national_focus/GER_main.txt").read_text(encoding="utf-8") == (
        "focus = {\n\tid = GER_rhineland\n}\nfocus = {\n\tid = GER_sample\n}\n"
    )


def test_collection_source_family_emits_collection_pdx_without_focus_diagnostics(tmp_path: Path) -> None:
    first_root = tmp_path / "GER_news_1"
    second_root = tmp_path / "GER_news_2"
    first_root.mkdir()
    second_root.mkdir()
    (first_root / "meta.yaml").write_text("type: event\ncollection: germany\n", encoding="utf-8")
    (second_root / "meta.yaml").write_text("type: event\ncollection: germany\n", encoding="utf-8")
    (first_root / "def.pdx").write_text("country_event = { id = germany.1 }", encoding="utf-8")
    (second_root / "def.pdx").write_text("country_event = { id = germany.2 }", encoding="utf-8")
    first = load_module_sources(
        first_root,
        {"def": ("def.pdx",)},
        module_id="event/GER_news_1",
        inferred_type="event",
    ).to_module()
    second = load_module_sources(
        second_root,
        {"def": ("def.pdx",)},
        module_id="event/GER_news_2",
        inferred_type="event",
    ).to_module()
    registry = BuildRegistry().add(CollectionSourceFamily(family="event", pdx_path_template="events/{collection_id}.txt")).add(PDXTextWriter())

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(second, first))
    written = write_artifacts(result, registry, tmp_path / "out")

    assert result.blocked is False
    assert result.diagnostics == ()
    assert [artifact.path for artifact in result.artifacts] == ["events/germany.txt"]
    assert result.artifacts[0].owner == "collection:germany"
    assert result.artifacts[0].metadata == {
        "family": "event",
        "collection_id": "germany",
        "module_ids": ["event/GER_news_1", "event/GER_news_2"],
    }
    assert written == {"events/germany.txt": tmp_path / "out/events/germany.txt"}
    assert (tmp_path / "out/events/germany.txt").read_text(encoding="utf-8") == (
        "country_event = {\n\tid = germany.1\n}\ncountry_event = {\n\tid = germany.2\n}\n"
    )


def test_collection_source_family_includes_descriptor_pdx_in_collection_artifact(tmp_path: Path) -> None:
    collection_root = tmp_path / "collections/event/germany"
    module_root = tmp_path / "modules/event/GER_news"
    collection_root.mkdir(parents=True)
    module_root.mkdir(parents=True)
    (collection_root / "category.txt").write_text("add_namespace = germany", encoding="utf-8")
    (module_root / "meta.yaml").write_text("type: event\ncollection: germany\n", encoding="utf-8")
    (module_root / "def.pdx").write_text("country_event = { id = germany.1 }", encoding="utf-8")
    collection_bundle = load_collection_sources(
        collection_root,
        family="event",
        collection_id="germany",
        source_slots={"category": ("category.txt",)},
        slots=(Slot("category", "category.txt", kind="pdx"),),
    )
    module = load_module_sources(
        module_root,
        {"def": ("def.pdx",)},
        module_id="event/GER_news",
        inferred_type="event",
    ).to_module()
    registry = BuildRegistry().add(CollectionSourceFamily(family="event", pdx_path_template="events/{collection_id}.txt")).add(PDXTextWriter())

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,), collections=(collection_bundle.collection,))
    artifact = result.artifacts[0]

    assert isinstance(collection_bundle.collection.payload, CollectionSourceBundle)
    assert artifact.inputs == (collection_root / "category.txt", module_root / "def.pdx")
    assert artifact.payload.to_str() == "add_namespace = germany\ncountry_event = {\n\tid = germany.1\n}\n"
    assert artifact.metadata == {
        "family": "event",
        "collection_id": "germany",
        "module_ids": ["event/GER_news"],
        "descriptor_inputs": ["category.txt"],
    }


def test_collection_source_family_emits_collection_localization_artifacts(tmp_path: Path) -> None:
    collection_root = tmp_path / "collections/event/germany"
    module_root = tmp_path / "modules/event/GER_news"
    collection_root.mkdir(parents=True)
    module_root.mkdir(parents=True)
    (collection_root / "strings.yml").write_text("en:\n  germany: Germany Events\n", encoding="utf-8")
    (module_root / "meta.yaml").write_text("type: event\ncollection: germany\n", encoding="utf-8")
    (module_root / "def.pdx").write_text("country_event = { id = germany.1 }", encoding="utf-8")
    collection_bundle = load_collection_sources(
        collection_root,
        family="event",
        collection_id="germany",
        source_slots={"strings": ("strings.yml",)},
        slots=(Slot("strings", "strings.yml", kind="loc"),),
    )
    module = load_module_sources(
        module_root,
        {"def": ("def.pdx",)},
        module_id="event/GER_news",
        inferred_type="event",
    ).to_module()
    registry = (
        BuildRegistry()
        .add(
            CollectionSourceFamily(
                family="event",
                pdx_path_template="events/{collection_id}.txt",
                loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
            )
        )
        .add(PDXTextWriter())
        .add(LocalizationYMLWriter())
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,), collections=(collection_bundle.collection,))
    written = write_artifacts(result, registry, tmp_path / "out")

    assert [artifact.path for artifact in result.artifacts] == ["events/germany.txt", "localisation/english/germany_l_english.yml"]
    assert result.artifacts[1].owner == "collection:germany"
    assert result.artifacts[1].inputs == (collection_root / "strings.yml",)
    assert result.artifacts[1].metadata == {
        "family": "event",
        "collection_id": "germany",
        "language": "l_english",
    }
    assert written["localisation/english/germany_l_english.yml"] == tmp_path / "out/localisation/english/germany_l_english.yml"
    assert (tmp_path / "out/localisation/english/germany_l_english.yml").read_text(encoding="utf-8-sig") == 'l_english:\n germany:0 "Germany Events"\n'


def test_collection_source_family_reports_missing_collection_required_localization_keys(tmp_path: Path) -> None:
    collection_root = tmp_path / "collections/event/germany"
    module_root = tmp_path / "modules/event/GER_news"
    collection_root.mkdir(parents=True)
    module_root.mkdir(parents=True)
    (collection_root / "strings.yml").write_text("en:\n  germany: Germany Events\n", encoding="utf-8")
    (module_root / "meta.yaml").write_text("type: event\ncollection: germany\n", encoding="utf-8")
    (module_root / "def.pdx").write_text("country_event = { id = germany.1 }", encoding="utf-8")
    collection_bundle = load_collection_sources(
        collection_root,
        family="event",
        collection_id="germany",
        source_slots={"strings": ("strings.yml",)},
        slots=(Slot("strings", "strings.yml", kind="loc"),),
    )
    module = load_module_sources(
        module_root,
        {"def": ("def.pdx",)},
        module_id="event/GER_news",
        inferred_type="event",
    ).to_module()
    registry = BuildRegistry().add(
        CollectionSourceFamily(
            family="event",
            pdx_path_template="events/{collection_id}.txt",
            loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
            required_loc_keys=("{collection_id}", "{collection_id}_desc"),
        )
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,), collections=(collection_bundle.collection,))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="event.missing_localization",
            message="Event germany missing localization key 'germany_desc' for l_english.",
            severity="error",
            family="event",
            collection_id="germany",
            slot="strings",
            source_path="strings.yml",
        ),
    )


def test_collection_source_family_emits_collection_copy_artifacts(tmp_path: Path) -> None:
    collection_root = tmp_path / "collections/event/germany"
    module_root = tmp_path / "modules/event/GER_news"
    (collection_root / "media").mkdir(parents=True)
    module_root.mkdir(parents=True)
    payload = b"collection image"
    (collection_root / "media/banner.png").write_bytes(payload)
    (module_root / "meta.yaml").write_text("type: event\ncollection: germany\n", encoding="utf-8")
    (module_root / "def.pdx").write_text("country_event = { id = germany.1 }", encoding="utf-8")
    collection_bundle = load_collection_sources(
        collection_root,
        family="event",
        collection_id="germany",
        source_slots={"media": ("media/banner.png",)},
        slots=(Slot("media", "media/*", many=True, kind="copy"),),
    )
    module = load_module_sources(
        module_root,
        {"def": ("def.pdx",)},
        module_id="event/GER_news",
        inferred_type="event",
    ).to_module()
    registry = (
        BuildRegistry()
        .add(
            CollectionSourceFamily(
                family="event",
                pdx_path_template="events/{collection_id}.txt",
                copy_path_template="gfx/events/{object_id}/{source_name}",
            )
        )
        .add(PDXTextWriter())
        .add(StaticCopyWriter())
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,), collections=(collection_bundle.collection,))
    written = write_artifacts(result, registry, tmp_path / "out")

    assert [artifact.path for artifact in result.artifacts] == ["events/germany.txt", "gfx/events/germany/banner.png"]
    assert result.artifacts[1].owner == "collection:germany"
    assert result.artifacts[1].inputs == (collection_root / "media/banner.png",)
    assert result.artifacts[1].metadata == {
        "family": "event",
        "collection_id": "germany",
        "slot": "media",
        "path": "media/banner.png",
        "output_path": "media/banner.png",
        "sha256": sha256hash(payload),
        "content_sha256": hashlib.sha256(payload).hexdigest(),
        "size": 16,
    }
    assert written["gfx/events/germany/banner.png"] == tmp_path / "out/gfx/events/germany/banner.png"
    assert (tmp_path / "out/gfx/events/germany/banner.png").read_bytes() == payload


def test_collection_source_family_emits_descriptor_artifacts_without_member_modules(tmp_path: Path) -> None:
    collection_root = tmp_path / "collections/event/germany"
    (collection_root / "media").mkdir(parents=True)
    payload = b"collection image"
    (collection_root / "category.txt").write_text("add_namespace = germany", encoding="utf-8")
    (collection_root / "strings.yml").write_text("en:\n  germany: Germany Events\n", encoding="utf-8")
    (collection_root / "media/banner.png").write_bytes(payload)
    collection_bundle = load_collection_sources(
        collection_root,
        family="event",
        collection_id="germany",
        source_slots={
            "category": ("category.txt",),
            "strings": ("strings.yml",),
            "media": ("media/banner.png",),
        },
        slots=(
            Slot("category", "category.txt", kind="pdx"),
            Slot("strings", "strings.yml", kind="loc"),
            Slot("media", "media/*", many=True, kind="copy"),
        ),
    )
    registry = (
        BuildRegistry()
        .add(
            CollectionSourceFamily(
                family="event",
                pdx_path_template="events/{collection_id}.txt",
                loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
                copy_path_template="gfx/events/{object_id}/{source_name}",
            )
        )
        .add(PDXTextWriter())
        .add(LocalizationYMLWriter())
        .add(StaticCopyWriter())
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, collections=(collection_bundle.collection,))
    written = write_artifacts(result, registry, tmp_path / "out")

    assert result.collections[0].module_ids == ()
    assert [artifact.path for artifact in result.artifacts] == [
        "events/germany.txt",
        "localisation/english/germany_l_english.yml",
        "gfx/events/germany/banner.png",
    ]
    assert result.artifacts[0].owner == "collection:germany"
    assert result.artifacts[0].inputs == (collection_root / "category.txt",)
    assert result.artifacts[0].metadata == {
        "family": "event",
        "collection_id": "germany",
        "module_ids": [],
        "descriptor_inputs": ["category.txt"],
    }
    assert result.artifacts[0].payload.to_str() == "add_namespace = germany\n"
    assert written["events/germany.txt"] == tmp_path / "out/events/germany.txt"
    assert written["localisation/english/germany_l_english.yml"] == tmp_path / "out/localisation/english/germany_l_english.yml"
    assert written["gfx/events/germany/banner.png"] == tmp_path / "out/gfx/events/germany/banner.png"
    assert (tmp_path / "out/events/germany.txt").read_text(encoding="utf-8") == "add_namespace = germany\n"
    assert (tmp_path / "out/gfx/events/germany/banner.png").read_bytes() == payload


def test_collection_source_family_emits_descriptor_loc_and_copy_without_pdx(tmp_path: Path) -> None:
    collection_root = tmp_path / "collections/event/germany"
    (collection_root / "media").mkdir(parents=True)
    payload = b"collection image"
    (collection_root / "strings.yml").write_text("en:\n  germany: Germany Events\n", encoding="utf-8")
    (collection_root / "media/banner.png").write_bytes(payload)
    collection_bundle = load_collection_sources(
        collection_root,
        family="event",
        collection_id="germany",
        source_slots={
            "strings": ("strings.yml",),
            "media": ("media/banner.png",),
        },
        slots=(
            Slot("strings", "strings.yml", kind="loc"),
            Slot("media", "media/*", many=True, kind="copy"),
        ),
    )
    registry = (
        BuildRegistry()
        .add(
            CollectionSourceFamily(
                family="event",
                pdx_path_template="events/{collection_id}.txt",
                loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
                copy_path_template="gfx/events/{object_id}/{source_name}",
            )
        )
        .add(PDXTextWriter())
        .add(LocalizationYMLWriter())
        .add(StaticCopyWriter())
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, collections=(collection_bundle.collection,))
    written = write_artifacts(result, registry, tmp_path / "out")

    assert result.collections[0].module_ids == ()
    assert [artifact.path for artifact in result.artifacts] == [
        "localisation/english/germany_l_english.yml",
        "gfx/events/germany/banner.png",
    ]
    assert result.artifacts[0].owner == "collection:germany"
    assert result.artifacts[0].inputs == (collection_root / "strings.yml",)
    assert result.artifacts[1].owner == "collection:germany"
    assert result.artifacts[1].inputs == (collection_root / "media/banner.png",)
    assert written["localisation/english/germany_l_english.yml"] == tmp_path / "out/localisation/english/germany_l_english.yml"
    assert written["gfx/events/germany/banner.png"] == tmp_path / "out/gfx/events/germany/banner.png"
    assert (tmp_path / "out/gfx/events/germany/banner.png").read_bytes() == payload


def test_collection_source_family_reports_collection_asset_constraint_diagnostics(tmp_path: Path) -> None:
    collection_root = tmp_path / "collections/event/germany"
    module_root = tmp_path / "modules/event/GER_news"
    (collection_root / "media").mkdir(parents=True)
    module_root.mkdir(parents=True)
    payload = b"\x89PNG\r\n\x1a\n" + pack(">I4sIIBBBBBI", 13, b"IHDR", 40, 30, 8, 6, 0, 0, 0, 0)
    (collection_root / "media/banner.png").write_bytes(payload)
    (module_root / "meta.yaml").write_text("type: event\ncollection: germany\n", encoding="utf-8")
    (module_root / "def.pdx").write_text("country_event = { id = germany.1 }", encoding="utf-8")
    collection_bundle = load_collection_sources(
        collection_root,
        family="event",
        collection_id="germany",
        source_slots={"media": ("media/banner.png",)},
        slots=(Slot("media", "media/*", many=True, kind="copy"),),
    )
    module = load_module_sources(
        module_root,
        {"def": ("def.pdx",)},
        module_id="event/GER_news",
        inferred_type="event",
    ).to_module()
    registry = BuildRegistry().add(
        CollectionSourceFamily(
            family="event",
            pdx_path_template="events/{collection_id}.txt",
            copy_path_template="gfx/events/{object_id}/{source_name}",
            asset_constraints={"media": {"formats": ("dds",), "width": 64, "height": 64}},
        )
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,), collections=(collection_bundle.collection,))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="event.asset_format",
            message="Event asset media/banner.png for slot media format 'png' must be one of: dds.",
            severity="error",
            family="event",
            collection_id="germany",
            slot="media",
            source_path="media/banner.png",
        ),
        Diagnostic(
            code="event.asset_dimensions",
            message="Event asset media/banner.png for slot media dimensions 40x30 must be 64x64.",
            severity="error",
            family="event",
            collection_id="germany",
            slot="media",
            source_path="media/banner.png",
        ),
    )


def test_collection_source_family_templates_can_use_source_slot(tmp_path: Path) -> None:
    collection_root = tmp_path / "collections/event/germany"
    module_root = tmp_path / "modules/event/GER_news"
    (collection_root / "media").mkdir(parents=True)
    module_root.mkdir(parents=True)
    (collection_root / "media/banner.png").write_bytes(b"collection image")
    (module_root / "meta.yaml").write_text("type: event\ncollection: germany\n", encoding="utf-8")
    (module_root / "def.pdx").write_text("country_event = { id = germany.1 }", encoding="utf-8")
    collection_bundle = load_collection_sources(
        collection_root,
        family="event",
        collection_id="germany",
        source_slots={"media": ("media/banner.png",)},
        slots=(Slot("media", "media/*", many=True, kind="copy"),),
    )
    module = load_module_sources(
        module_root,
        {"def": ("def.pdx",)},
        module_id="event/GER_news",
        inferred_type="event",
    ).to_module()
    registry = BuildRegistry().add(
        CollectionSourceFamily(
            family="event",
            pdx_path_template="events/{collection_id}.txt",
            copy_path_template="gfx/events/{slot}/{object_id}/{source_name}",
        )
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,), collections=(collection_bundle.collection,))

    assert [artifact.path for artifact in result.artifacts] == ["events/germany.txt", "gfx/events/media/germany/banner.png"]


def test_collection_pdx_family_can_plan_focus_tree_view_artifact(tmp_path: Path) -> None:
    first = _focus_module(
        tmp_path,
        root_name="GER_rhineland",
        module_id="focus/GER_rhineland",
        text="focus = {\n\tid = GER_rhineland\n}",
    )
    second = _focus_module(
        tmp_path,
        root_name="GER_sample",
        module_id="focus/GER_sample",
        text="focus = {\n\tid = GER_sample\n\tprerequisite = { focus = GER_rhineland }\n}",
    )
    registry = BuildRegistry().add(
        CollectionPDXFamily(
            family="focus",
            pdx_path_template="common/national_focus/{collection_id}.txt",
            view_path_template="views/focus-tree/{collection_id}.json",
        )
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(second, first))

    assert [artifact.path for artifact in result.artifacts] == [
        "common/national_focus/GER_main.txt",
        "views/focus-tree/GER_main.json",
    ]
    assert result.artifacts[1].artifact_type == "view"
    assert result.artifacts[1].owner == "collection:GER_main"
    assert result.artifacts[1].inputs == result.artifacts[0].inputs
    assert result.artifacts[1].metadata == {
        "schema": "focus-tree.view.v1",
        "collection_id": "GER_main",
        "family": "focus",
        "nodes": [
            {
                "focus_id": "GER_rhineland",
                "module_id": "focus/GER_rhineland",
                "source_path": "def.pdx",
                "span": {"line": 2, "column": 7},
                "order": 0,
                "prerequisites": [],
            },
            {
                "focus_id": "GER_sample",
                "module_id": "focus/GER_sample",
                "source_path": "def.pdx",
                "span": {"line": 2, "column": 7},
                "order": 1,
                "prerequisites": ["GER_rhineland"],
            },
        ],
    }


def test_collection_pdx_family_can_nest_member_entries_in_collection_wrapper(
    tmp_path: Path,
) -> None:
    module = _focus_module(
        tmp_path,
        root_name="GER_rhineland",
        module_id="focus/GER_rhineland",
        text="focus = {\n\tid = GER_rhineland\n}",
    )
    collection_root = tmp_path / "collection"
    collection_root.mkdir()
    (collection_root / "meta.yaml").write_text(
        "members:\n  - GER_rhineland\n",
        encoding="utf-8",
    )
    (collection_root / "def.pdx").write_text(
        "focus_tree = {\n\tid = GER_main\n\tdefault = no\n}\n",
        encoding="utf-8",
    )
    collection = load_collection_sources(
        collection_root,
        family="focus",
        collection_id="GER_main",
        source_slots={"def": ("def.pdx",)},
        slots=(Slot("def", "def.pdx", kind="pdx"),),
    ).collection
    registry = BuildRegistry().add(
        CollectionPDXFamily(
            family="focus",
            pdx_path_template="common/national_focus/{collection_id}.txt",
            member_container="focus_tree",
        )
    )

    result = plan_build(
        project_id="minimal_hoi4",
        registry=registry,
        modules=(module,),
        collections=(collection,),
    )

    assert result.blocked is False
    payload = result.artifacts[0].payload
    focus_tree = payload.find("focus_tree")
    assert focus_tree is not None
    assert isinstance(focus_tree.val, PDXBlock)
    assert [entry.key_str for entry in focus_tree.val.entries] == [
        "id",
        "default",
        "focus",
    ]


def test_collection_pdx_family_can_aggregate_member_localization(tmp_path: Path) -> None:
    modules = []
    for object_id, title in (
        ("GER_rhineland", "Rhineland"),
        ("GER_four_year_plan", "Four Year Plan"),
    ):
        root = tmp_path / object_id
        root.mkdir()
        (root / "meta.yaml").write_text("collection: GER_main\n", encoding="utf-8")
        (root / "def.pdx").write_text(f"focus = {{ id = {object_id} }}\n", encoding="utf-8")
        (root / "main.loc").write_text(
            f"[en.{object_id}]\n{title}\n\n[en.{object_id}_desc]\n{title} description\n",
            encoding="utf-8",
        )
        bundle = load_module_sources(
            root,
            {"def": ("def.pdx",), "loc": ("main.loc",)},
            module_id=f"focus/{object_id}",
            inferred_type="focus",
        )
        modules.append(bundle.to_module())
    registry = BuildRegistry().add(
        CollectionPDXFamily(
            family="focus",
            pdx_path_template="common/national_focus/{collection_id}.txt",
            loc_path_template="localisation/{language_folder}/FOCUS_TREE_{collection_id}_{language}.yml",
            aggregate_member_localization=True,
        )
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=tuple(modules))

    localization = next(artifact for artifact in result.artifacts if artifact.artifact_type == "loc")
    assert localization.path == "localisation/english/FOCUS_TREE_GER_main_l_english.yml"
    assert localization.owner == "collection:GER_main"
    assert [entry.key for entry in localization.payload] == [
        "GER_four_year_plan",
        "GER_four_year_plan_desc",
        "GER_rhineland",
        "GER_rhineland_desc",
    ]
    assert len(localization.inputs) == 2


def test_collection_pdx_family_reports_duplicate_focus_ids(tmp_path: Path) -> None:
    first = _focus_module(
        tmp_path,
        root_name="GER_first",
        module_id="focus/GER_first",
        text="focus = {\n\tid = GER_duplicate\n}",
    )
    second = _focus_module(
        tmp_path,
        root_name="GER_second",
        module_id="focus/GER_second",
        text="focus = {\n\tid = GER_duplicate\n}",
    )
    registry = BuildRegistry().add(CollectionPDXFamily(family="focus", pdx_path_template="common/national_focus/{collection_id}.txt"))

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(first, second))

    assert result.blocked is True
    assert result.diagnostics[0].code == "focus.duplicate_id"
    assert result.diagnostics[0].module_id == "focus/GER_second"
    assert result.diagnostics[0].source_path == "def.pdx"
    assert result.diagnostics[0].span == {"line": 2, "column": 7}
    assert result.diagnostics[0].message == "Focus id GER_duplicate is declared by focus/GER_first and focus/GER_second."


def test_collection_pdx_family_reports_missing_project_local_prerequisites(tmp_path: Path) -> None:
    module = _focus_module(
        tmp_path,
        root_name="GER_sample",
        module_id="focus/GER_sample",
        text="focus = {\n\tid = GER_sample\n\tprerequisite = { focus = GER_missing }\n}",
    )
    registry = BuildRegistry().add(CollectionPDXFamily(family="focus", pdx_path_template="common/national_focus/{collection_id}.txt"))

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,))

    assert result.blocked is True
    assert result.diagnostics[0].code == "focus.missing_prerequisite"
    assert result.diagnostics[0].module_id == "focus/GER_sample"
    assert result.diagnostics[0].source_path == "def.pdx"
    assert result.diagnostics[0].span == {"line": 3, "column": 27}
    assert result.diagnostics[0].message == "Focus GER_sample prerequisite GER_missing does not resolve to a project focus."


def test_collection_pdx_family_reports_missing_focus_localization_keys(tmp_path: Path) -> None:
    root = tmp_path / "GER_sample"
    root.mkdir()
    (root / "meta.yaml").write_text("type: focus\ncollection: GER_main\n", encoding="utf-8")
    (root / "def.pdx").write_text("focus = {\n\tid = GER_sample\n}", encoding="utf-8")
    (root / "main.loc").write_text("en:\n  GER_sample: Sample Focus\n", encoding="utf-8")
    bundle = load_module_sources(
        root,
        {"def": ("def.pdx",), "loc": ("main.loc",)},
        module_id="focus/GER_sample",
        inferred_type="focus",
    )
    registry = BuildRegistry().add(CollectionPDXFamily(family="focus", pdx_path_template="common/national_focus/{collection_id}.txt"))

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(bundle.to_module(),))

    assert result.blocked is True
    assert result.diagnostics == (
        Diagnostic(
            code="focus.missing_localization",
            message="Focus GER_sample missing localization key 'GER_sample_desc' for l_english.",
            severity="error",
            family="focus",
            module_id="focus/GER_sample",
            slot="loc",
            source_path="def.pdx",
            span={"line": 2, "column": 7},
        ),
    )


def test_simple_source_family_emits_localization_artifacts_from_source_bundle(tmp_path: Path) -> None:
    root = tmp_path / "GER_sample"
    root.mkdir()
    (root / "meta.yaml").write_text("type: focus\n", encoding="utf-8")
    (root / "main.loc").write_text("l_english:\n  GER_sample: Sample Focus\n  GER_sample_desc: Sample description\n", encoding="utf-8")
    matched = match_slots(root, (Slot("loc", "*.loc", many=True),), module_id="focus/GER_sample")
    bundle = load_module_sources(root, matched.source_slots, module_id="focus/GER_sample", inferred_type="focus")
    module = bundle.to_module()
    registry = (
        BuildRegistry()
        .add(SimpleSourceFamily(family="focus", loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml"))
        .add(LocalizationYMLWriter())
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(module,))
    written = write_artifacts(result, registry, tmp_path / "out")

    target = tmp_path / "out/localisation/english/GER_sample_l_english.yml"
    assert [artifact.path for artifact in result.artifacts] == ["localisation/english/GER_sample_l_english.yml"]
    assert written == {"localisation/english/GER_sample_l_english.yml": target}
    assert target.read_text(encoding="utf-8-sig") == 'l_english:\n GER_sample:0 "Sample Focus"\n GER_sample_desc:0 "Sample description"\n'


def test_routed_source_family_emits_templates_from_settings_route(tmp_path: Path) -> None:
    root = tmp_path / "TRAIT_SAMPLE"
    root.mkdir()
    (root / "meta.yaml").write_text("type: trait\nsettings:\n  subtype: country_leader\n", encoding="utf-8")
    (root / "def.pdx").write_text("TRAIT_SAMPLE = { random = no }", encoding="utf-8")
    (root / "main.loc").write_text("en:\n  TRAIT_SAMPLE: Sample Trait\n", encoding="utf-8")
    bundle = load_module_sources(
        root,
        {"def": ("def.pdx",), "loc": ("main.loc",)},
        module_id="trait/TRAIT_SAMPLE",
        inferred_type="trait",
    )
    registry = (
        BuildRegistry()
        .add(
            RoutedSourceFamily(
                family="trait",
                routes={
                    "country_leader": SourceRoute(
                        pdx_path_template="common/country_leader/{object_id}.txt",
                        loc_path_template="localisation/{language_folder}/{object_id}_{language}.yml",
                    )
                },
            )
        )
        .add(PDXTextWriter())
        .add(LocalizationYMLWriter())
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(bundle.to_module(),))
    written = write_artifacts(result, registry, tmp_path / "out")

    assert result.blocked is False
    assert [artifact.path for artifact in result.artifacts] == [
        "common/country_leader/TRAIT_SAMPLE.txt",
        "localisation/english/TRAIT_SAMPLE_l_english.yml",
    ]
    assert written == {
        "common/country_leader/TRAIT_SAMPLE.txt": tmp_path / "out/common/country_leader/TRAIT_SAMPLE.txt",
        "localisation/english/TRAIT_SAMPLE_l_english.yml": tmp_path / "out/localisation/english/TRAIT_SAMPLE_l_english.yml",
    }


def test_routed_source_family_uses_code_owned_default_route_without_metadata(
    tmp_path: Path,
) -> None:
    root = tmp_path / "TRAIT_SAMPLE"
    root.mkdir()
    (root / "def.pdx").write_text(
        "leader_traits = { TRAIT_SAMPLE = { random = no } }",
        encoding="utf-8",
    )
    bundle = load_module_sources(
        root,
        {"def": ("def.pdx",)},
        module_id="trait/TRAIT_SAMPLE",
        inferred_type="trait",
    )
    registry = BuildRegistry().add(
        RoutedSourceFamily(
            family="trait",
            routes={
                "country_leader": SourceRoute(pdx_path_template="common/country_leader/{object_id}.txt"),
                "scientist": SourceRoute(pdx_path_template="common/scientist_traits/{object_id}.txt"),
            },
            default_route="country_leader",
        )
    )

    family_view = registry.to_view()["families"][0]
    result = plan_build(
        project_id="minimal_hoi4",
        registry=registry,
        modules=(bundle.to_module(),),
    )

    assert result.blocked is False
    assert [artifact.path for artifact in result.artifacts] == ["common/country_leader/TRAIT_SAMPLE.txt"]
    assert family_view["default_route"] == "country_leader"
    assert family_view["metadata"]["settings"]["subtype"] == {
        "required": False,
        "values": ["country_leader", "scientist"],
        "default": "country_leader",
    }


def test_routed_source_family_explicit_route_overrides_default(tmp_path: Path) -> None:
    root = tmp_path / "TRAIT_SAMPLE"
    root.mkdir()
    (root / "meta.yaml").write_text(
        "settings:\n  subtype: scientist\n",
        encoding="utf-8",
    )
    (root / "def.pdx").write_text(
        "scientist_traits = { TRAIT_SAMPLE = { } }",
        encoding="utf-8",
    )
    bundle = load_module_sources(
        root,
        {"def": ("def.pdx",)},
        module_id="trait/TRAIT_SAMPLE",
        inferred_type="trait",
    )
    registry = BuildRegistry().add(
        RoutedSourceFamily(
            family="trait",
            routes={
                "country_leader": SourceRoute(pdx_path_template="common/country_leader/{object_id}.txt"),
                "scientist": SourceRoute(pdx_path_template="common/scientist_traits/{object_id}.txt"),
            },
            default_route="country_leader",
        )
    )

    result = plan_build(
        project_id="minimal_hoi4",
        registry=registry,
        modules=(bundle.to_module(),),
    )

    assert result.blocked is False
    assert [artifact.path for artifact in result.artifacts] == ["common/scientist_traits/TRAIT_SAMPLE.txt"]


def test_routed_source_family_registers_and_emits_nothing_for_explicit_non_emitting_route(tmp_path: Path) -> None:
    root = tmp_path / "MODEL_AGGREGATE"
    root.mkdir()
    (root / "meta.yaml").write_text("type: model_asset\nsettings:\n  asset_kind: aggregate\n", encoding="utf-8")
    (root / "def.pdx").write_text("entity = { name = MODEL_AGGREGATE }", encoding="utf-8")
    bundle = load_module_sources(
        root,
        {"def": ("def.pdx",)},
        module_id="model_asset/MODEL_AGGREGATE",
        inferred_type="model_asset",
    )
    registry = BuildRegistry().add(
        RoutedSourceFamily(
            family="model_asset",
            settings_key="asset_kind",
            routes={
                "aggregate": SourceRoute(emits_artifacts=False),
                "record": SourceRoute(pdx_path_template="gfx/models/{object_id}.asset"),
            },
        )
    )

    family_view = registry.to_view()["families"][0]
    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(bundle.to_module(),))

    assert registry.family("model_asset").routes["aggregate"].emits_artifacts is False
    assert family_view["routes"] == {
        "aggregate": {"emits_artifacts": False},
        "record": {"pdx": "gfx/models/{object_id}.asset"},
    }
    assert family_view["metadata"]["settings"]["asset_kind"] == {
        "required": True,
        "values": ["aggregate", "record"],
    }
    assert [output["route"] for output in family_view["outputs"]] == ["record"]
    assert result.blocked is False
    assert result.artifacts == ()


@pytest.mark.parametrize(
    ("route", "message"),
    [
        (SourceRoute(), "must define at least one artifact template"),
        (
            SourceRoute(pdx_path_template="gfx/models/{object_id}.asset", emits_artifacts=False),
            "cannot define artifact templates when emits_artifacts is false",
        ),
        (SourceRoute(emits_artifacts="false"), "emits_artifacts must be a boolean"),
    ],
)
def test_routed_source_family_rejects_invalid_emission_contracts(route: SourceRoute, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        BuildRegistry().add(RoutedSourceFamily(family="model_asset", routes={"aggregate": route}))


def test_routed_source_family_emits_aggregate_sprite_gfx_for_declared_sprite_slots(tmp_path: Path) -> None:
    modules = []
    for name, subtype in (("TRAIT_ADVISOR", "country_leader"), ("TRAIT_SCIENTIST", "scientist")):
        root = tmp_path / name
        root.mkdir()
        (root / "meta.yaml").write_text(f"type: trait\nsettings:\n  subtype: {subtype}\n", encoding="utf-8")
        (root / "icon.dds").write_bytes(f"{name} dds bytes".encode("utf-8"))
        bundle = load_module_sources(
            root,
            {"icon": ("icon.dds",)},
            module_id=f"trait/{name}",
            inferred_type="trait",
            slots=(Slot("icon", "icon.dds", kind="copy"),),
        )
        modules.append(bundle.to_module())
    registry = (
        BuildRegistry()
        .add(
            RoutedSourceFamily(
                family="trait",
                routes={
                    "country_leader": SourceRoute(copy_path_template="gfx/leaders/{object_id}{source_suffix}"),
                    "scientist": SourceRoute(copy_path_template="gfx/scientists/{object_id}{source_suffix}"),
                },
                sprite_gfx_path_template="interface/paradev_{family}.gfx",
                sprite_name_template="GFX_trait_{object_id}",
                sprite_slots=("icon",),
            )
        )
        .add(StaticCopyWriter())
        .add(SpriteGFXWriter())
    )

    family_view = registry.to_view()["families"][0]
    assert family_view["sprite_slots"] == ["icon"]
    assert family_view["templates"] == {
        "sprite_gfx": "interface/paradev_{family}.gfx",
        "sprite_name": "GFX_trait_{object_id}",
    }
    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=tuple(modules))
    written = write_artifacts(result, registry, tmp_path / "out")

    assert result.blocked is False
    assert [artifact.path for artifact in result.artifacts] == [
        "gfx/leaders/TRAIT_ADVISOR.dds",
        "gfx/scientists/TRAIT_SCIENTIST.dds",
        "interface/paradev_trait.gfx",
    ]
    assert result.artifacts[2].artifact_type == "sprite_gfx"
    assert result.artifacts[2].owner == "project:minimal_hoi4"
    assert result.artifacts[2].inputs == (
        tmp_path / "TRAIT_ADVISOR/icon.dds",
        tmp_path / "TRAIT_SCIENTIST/icon.dds",
    )
    assert result.artifacts[2].metadata == {"family": "trait", "sprite_count": 2}
    assert written["interface/paradev_trait.gfx"] == tmp_path / "out/interface/paradev_trait.gfx"
    assert (tmp_path / "out/interface/paradev_trait.gfx").read_text(encoding="utf-8") == (
        "spriteTypes = {\n"
        "\tSpriteType = {\n"
        '\t\tname = "GFX_trait_TRAIT_ADVISOR"\n'
        '\t\ttexturefile = "gfx/leaders/TRAIT_ADVISOR.dds"\n'
        "\t}\n"
        "\tSpriteType = {\n"
        '\t\tname = "GFX_trait_TRAIT_SCIENTIST"\n'
        '\t\ttexturefile = "gfx/scientists/TRAIT_SCIENTIST.dds"\n'
        "\t}\n"
        "}\n"
    )


def test_routed_source_family_blocks_missing_or_unknown_settings_route(tmp_path: Path) -> None:
    missing_root = tmp_path / "TRAIT_MISSING"
    unknown_root = tmp_path / "TRAIT_UNKNOWN"
    missing_root.mkdir()
    unknown_root.mkdir()
    (missing_root / "meta.yaml").write_text("type: trait\n", encoding="utf-8")
    (missing_root / "def.pdx").write_text("TRAIT_MISSING = { random = no }", encoding="utf-8")
    (unknown_root / "meta.yaml").write_text("type: trait\nsettings:\n  subtype: operative\n", encoding="utf-8")
    (unknown_root / "def.pdx").write_text("TRAIT_UNKNOWN = { random = no }", encoding="utf-8")
    missing = load_module_sources(
        missing_root,
        {"def": ("def.pdx",)},
        module_id="trait/TRAIT_MISSING",
        inferred_type="trait",
    ).to_module()
    unknown = load_module_sources(
        unknown_root,
        {"def": ("def.pdx",)},
        module_id="trait/TRAIT_UNKNOWN",
        inferred_type="trait",
    ).to_module()
    registry = BuildRegistry().add(
        RoutedSourceFamily(
            family="trait",
            routes={"country_leader": SourceRoute(pdx_path_template="common/country_leader/{object_id}.txt")},
        )
    )

    result = plan_build(project_id="minimal_hoi4", registry=registry, modules=(missing, unknown))

    assert result.blocked is True
    assert result.artifacts == ()
    assert result.diagnostics == (
        Diagnostic(
            code="family.missing_route",
            message="Module trait/TRAIT_MISSING must set settings.subtype to one of: country_leader.",
            severity="error",
            family="trait",
            module_id="trait/TRAIT_MISSING",
            source_path="meta.yaml",
        ),
        Diagnostic(
            code="family.unsupported_route",
            message="Module trait/TRAIT_UNKNOWN settings.subtype 'operative' must be one of: country_leader.",
            severity="error",
            family="trait",
            module_id="trait/TRAIT_UNKNOWN",
            source_path="meta.yaml",
        ),
    )


def _focus_module(tmp_path: Path, *, root_name: str, module_id: str, text: str):
    root = tmp_path / root_name
    root.mkdir()
    (root / "meta.yaml").write_text("type: focus\ncollection: GER_main\n", encoding="utf-8")
    (root / "def.pdx").write_text(text, encoding="utf-8")
    bundle = load_module_sources(
        root,
        {"def": ("def.pdx",)},
        module_id=module_id,
        inferred_type="focus",
    )
    return bundle.to_module()
