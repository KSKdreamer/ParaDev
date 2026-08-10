from __future__ import annotations

from dataclasses import replace
import shutil
import subprocess
from pathlib import Path

import pytest
from heavenbase.utils import sha256hash
from PIL import Image

from paradev.build import Artifact, BuildResult, CopySource, Module, ModuleSourceBundle, SpriteType, manifest_payloads


@pytest.mark.parametrize(
    ("path", "target_root", "expected"),
    [
        ("common/buildings/alpha.txt", "output", True),
        ("interface/countrystateview.gfx", "output", True),
        ("common/ideas/alpha.txt", "output", False),
        ("gfx/interface/buildings/alpha.dds", "output", False),
        ("interface/countrystateview.gfx", "build", False),
    ],
)
def test_building_icon_stage_transform_predicate_is_narrow(
    path: str,
    target_root: str,
    expected: bool,
) -> None:
    from paradev.games.hoi4.building_icons import (
        _building_icon_stage_transform_required,
    )

    artifact = Artifact(
        path=path,
        artifact_type="pdx",
        owner="module:test/sample",
        target_root=target_root,
    )

    assert _building_icon_stage_transform_required(artifact) is expected


def test_hoi4_building_icon_postprocessor_generates_strip_and_remaps_frames(tmp_path: Path) -> None:
    from paradev.games.hoi4.building_icons import postprocess_building_icon_strip

    output_root = tmp_path / "out"
    (output_root / "common/buildings").mkdir(parents=True)
    (output_root / "interface").mkdir(parents=True)
    (output_root / "common/buildings/alpha.txt").write_text("buildings = { alpha = { icon_frame = 28 } }\n", encoding="utf-8")
    (output_root / "common/buildings/beta.txt").write_text("buildings = { beta = { icon_frame = 28 } }\n", encoding="utf-8")
    (output_root / "common/buildings/fog.txt").write_text("buildings = { fog = { icon_frame = 9999 } }\n", encoding="utf-8")
    (output_root / "interface/countrystateview.gfx").write_text(
        'spriteTypes = {\n\tspriteType = {\n\t\tname = "GFX_buildings_strip"\n'
        '\t\ttextureFile = "gfx/interface/buildings/building_icon_strip.dds"\n\t\tnoOfFrames = 31\n\t}\n}\n',
        encoding="utf-8",
    )
    modules = (
        _building_module(tmp_path, "beta", "blue"),
        _building_module(tmp_path, "alpha", "red"),
        _support_module(tmp_path, "fog"),
    )
    gfx_artifact = Artifact(
        path="interface/countrystateview.gfx",
        artifact_type="sprite_gfx",
        owner="project:icon_test",
        payload=(
            SpriteType(
                name="GFX_buildings_strip",
                texturefile="gfx/interface/buildings/building_icon_strip.dds",
                properties={"noOfFrames": 31},
            ),
        ),
    )
    result = BuildResult.plan(project_id="icon_test", profile="hoi4", modules=modules, artifacts=(gfx_artifact,))

    summary = postprocess_building_icon_strip(result, output_root=output_root)

    assert summary.frame_count == 2
    assert summary.frame_by_building_id == {"alpha": 1, "beta": 2}
    assert (output_root / "gfx/interface/buildings/building_icon_strip.dds").is_file()
    assert _image_size(output_root / "gfx/interface/buildings/building_icon_strip.dds") == (92, 46)
    assert "noOfFrames = 2" in (output_root / "interface/countrystateview.gfx").read_text(encoding="utf-8")
    assert "icon_frame = 1" in (output_root / "common/buildings/alpha.txt").read_text(encoding="utf-8")
    assert "icon_frame = 2" in (output_root / "common/buildings/beta.txt").read_text(encoding="utf-8")
    assert "icon_frame = 9999" in (output_root / "common/buildings/fog.txt").read_text(encoding="utf-8")
    artifacts = {str(artifact.path): artifact for artifact in summary.artifacts}
    assert list(artifacts) == [
        "gfx/interface/buildings/building_icon_strip.dds",
        "common/buildings/alpha.txt",
        "common/buildings/beta.txt",
        "interface/countrystateview.gfx",
    ]
    strip_artifact = artifacts["gfx/interface/buildings/building_icon_strip.dds"]
    assert strip_artifact.artifact_type == "building_icon_strip"
    assert strip_artifact.owner == "project:icon_test"
    assert strip_artifact.inputs == (tmp_path / "src/alpha/icon.png", tmp_path / "src/beta/icon.png")
    assert strip_artifact.metadata["module_ids"] == ["building/alpha", "building/beta"]
    for relative_path, artifact in artifacts.items():
        payload = (output_root / relative_path).read_bytes()
        assert artifact.mode == "emit"
        assert artifact.metadata["postprocessor"] == "hoi4.building_icon_strip"
        assert artifact.metadata["sha256"] == sha256hash(payload)
        assert artifact.metadata["size"] == len(payload)
    assert artifacts["common/buildings/alpha.txt"].owner == "module:building/alpha"
    assert artifacts["common/buildings/beta.txt"].owner == "module:building/beta"
    updated_gfx_artifact = artifacts["interface/countrystateview.gfx"]
    assert updated_gfx_artifact.payload == (
        SpriteType(
            name="GFX_buildings_strip",
            texturefile="gfx/interface/buildings/building_icon_strip.dds",
            properties={"noOfFrames": 2},
        ),
    )
    sprites = manifest_payloads(replace(result, artifacts=summary.artifacts))["sprites.json"]["sprites"]
    assert sprites[0]["properties"]["noOfFrames"] == 2


def test_hoi4_building_icon_postprocessor_uses_pillow_for_supported_sources(
    tmp_path: Path,
) -> None:
    from paradev.games.hoi4 import building_icons

    output_root = tmp_path / "out"
    (output_root / "common/buildings").mkdir(parents=True)
    (output_root / "interface").mkdir(parents=True)
    for building_id in ("alpha", "beta", "gamma"):
        (output_root / "common/buildings" / f"{building_id}.txt").write_text(
            f"buildings = {{ {building_id} = {{ icon_frame = 28 }} }}\n",
            encoding="utf-8",
        )
    (output_root / "interface/countrystateview.gfx").write_text(
        'spriteTypes = {\n\tspriteType = {\n\t\tname = "GFX_buildings_strip"\n'
        '\t\ttextureFile = "gfx/interface/buildings/building_icon_strip.dds"\n\t\tnoOfFrames = 31\n\t}\n}\n',
        encoding="utf-8",
    )
    modules = (
        _building_module_with_pillow(
            tmp_path,
            "gamma",
            suffix=".tga",
            size=(8, 8),
            color=(0, 0, 255, 255),
        ),
        _building_module_with_pillow(
            tmp_path,
            "beta",
            suffix=".dds",
            size=(6, 12),
            color=(0, 255, 0, 255),
        ),
        _building_module_with_pillow(
            tmp_path,
            "alpha",
            suffix=".png",
            size=(12, 6),
            color=(255, 0, 0, 255),
        ),
    )
    gfx_artifact = Artifact(
        path="interface/countrystateview.gfx",
        artifact_type="sprite_gfx",
        owner="project:icon_test",
        payload=(
            SpriteType(
                name="GFX_buildings_strip",
                texturefile="gfx/interface/buildings/building_icon_strip.dds",
                properties={"noOfFrames": 31},
            ),
        ),
    )
    result = BuildResult.plan(
        project_id="icon_test",
        profile="hoi4",
        modules=modules,
        artifacts=(gfx_artifact,),
    )

    summary = building_icons.postprocess_building_icon_strip(
        result,
        output_root=output_root,
        frame_size=16,
    )

    strip_path = output_root / "gfx/interface/buildings/building_icon_strip.dds"
    strip_payload = strip_path.read_bytes()
    assert strip_payload[:4] == b"DDS "
    assert strip_payload[12:20] == (16).to_bytes(4, "little") + (48).to_bytes(4, "little")
    assert strip_payload[84:88] == b"DXT5"
    with Image.open(strip_path) as strip:
        assert strip.format == "DDS"
        assert strip.size == (48, 16)
        rgba = strip.convert("RGBA")
    try:
        assert rgba.getpixel((8, 8))[0] > 200
        assert rgba.getpixel((24, 8))[1] > 200
        assert rgba.getpixel((40, 8))[2] > 200
        assert rgba.getpixel((8, 0))[3] < 32
        assert rgba.getpixel((16, 8))[3] < 32
    finally:
        rgba.close()
    assert summary.frame_count == 3
    assert summary.frame_by_building_id == {"alpha": 1, "beta": 2, "gamma": 3}
    for frame, building_id in enumerate(("alpha", "beta", "gamma"), start=1):
        assert f"icon_frame = {frame}" in (output_root / "common/buildings" / f"{building_id}.txt").read_text(encoding="utf-8")
    assert "noOfFrames = 3" in (output_root / "interface/countrystateview.gfx").read_text(encoding="utf-8")
    artifacts = {str(artifact.path): artifact for artifact in summary.artifacts}
    assert list(artifacts) == [
        "gfx/interface/buildings/building_icon_strip.dds",
        "common/buildings/alpha.txt",
        "common/buildings/beta.txt",
        "common/buildings/gamma.txt",
        "interface/countrystateview.gfx",
    ]
    strip_artifact = artifacts["gfx/interface/buildings/building_icon_strip.dds"]
    assert strip_artifact.inputs == (
        tmp_path / "src/alpha/icon.png",
        tmp_path / "src/beta/icon.dds",
        tmp_path / "src/gamma/icon.tga",
    )
    assert strip_artifact.metadata["format"] == "dds"
    assert strip_artifact.metadata["frame_count"] == 3
    assert strip_artifact.metadata["width"] == 48
    assert strip_artifact.metadata["height"] == 16
    for relative_path, artifact in artifacts.items():
        payload = (output_root / relative_path).read_bytes()
        assert artifact.metadata["sha256"] == sha256hash(payload)
        assert artifact.metadata["size"] == len(payload)


def test_hoi4_building_icon_pillow_reports_unreadable_source(
    tmp_path: Path,
) -> None:
    from paradev.games.hoi4 import building_icons

    output_root = tmp_path / "out"
    (output_root / "common/buildings").mkdir(parents=True)
    (output_root / "common/buildings/alpha.txt").write_text(
        "buildings = { alpha = { icon_frame = 28 } }\n",
        encoding="utf-8",
    )
    icon = tmp_path / "src/alpha/icon.png"
    icon.parent.mkdir(parents=True)
    icon.write_bytes(b"not an image")
    result = BuildResult.plan(
        project_id="icon_test",
        profile="hoi4",
        modules=(_building_module_for_icon(tmp_path, "alpha", icon),),
        artifacts=(),
    )

    with pytest.raises(
        RuntimeError,
        match=r"Pillow failed to read HoI4 building icon .*icon\.png",
    ):
        building_icons.postprocess_building_icon_strip(
            result,
            output_root=output_root,
        )

    assert not (output_root / "gfx/interface/buildings/building_icon_strip.dds").exists()
    assert "icon_frame = 28" in (output_root / "common/buildings/alpha.txt").read_text(encoding="utf-8")


def test_hoi4_building_icon_writer_ignores_host_image_tools(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from paradev.games.hoi4 import building_icons

    modules = (
        _building_module_with_pillow(
            tmp_path,
            "alpha",
            suffix=".png",
            size=(12, 6),
            color=(255, 0, 0, 255),
        ),
        _building_module_with_pillow(
            tmp_path,
            "beta",
            suffix=".png",
            size=(6, 12),
            color=(0, 0, 255, 255),
        ),
    )
    records = building_icons._building_icon_records(
        BuildResult.plan(
            project_id="icon_test",
            profile="hoi4",
            modules=modules,
            artifacts=(),
        )
    )
    host_tools_target = tmp_path / "with-host-tools.dds"
    minimal_path_target = tmp_path / "without-host-tools.dds"

    monkeypatch.setenv("PATH", "/fake/host/image-tools")
    monkeypatch.setattr(
        shutil,
        "which",
        lambda command: f"/fake/host/image-tools/{command}" if command in {"magick", "convert"} else None,
    )
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *_args, **_kwargs: pytest.fail("building icon strip invoked a host image tool"),
    )
    building_icons._write_icon_strip(records, host_tools_target, frame_size=16)

    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(shutil, "which", lambda _command: None)
    building_icons._write_icon_strip(records, minimal_path_target, frame_size=16)

    host_tools_payload = host_tools_target.read_bytes()
    minimal_path_payload = minimal_path_target.read_bytes()
    assert sha256hash(host_tools_payload) == sha256hash(minimal_path_payload)
    assert host_tools_payload[:4] == b"DDS "
    assert host_tools_payload[12:20] == (16).to_bytes(4, "little") + (32).to_bytes(4, "little")
    assert host_tools_payload[84:88] == b"DXT5"


def _building_module(tmp_path: Path, building_id: str, color: str) -> Module:
    root = tmp_path / "src" / building_id
    root.mkdir(parents=True)
    icon = root / "icon.png"
    with Image.new("RGBA", (8, 8), color) as image:
        image.save(icon)
    return _building_module_for_icon(tmp_path, building_id, icon)


def _building_module_with_pillow(
    tmp_path: Path,
    building_id: str,
    *,
    suffix: str,
    size: tuple[int, int],
    color: tuple[int, int, int, int],
) -> Module:
    root = tmp_path / "src" / building_id
    root.mkdir(parents=True)
    icon = root / f"icon{suffix}"
    with Image.new("RGBA", size, color) as image:
        save_options = {"pixel_format": "DXT5"} if suffix == ".dds" else {}
        image.save(icon, **save_options)
    return _building_module_for_icon(tmp_path, building_id, icon)


def _building_module_for_icon(
    tmp_path: Path,
    building_id: str,
    icon: Path,
) -> Module:
    root = tmp_path / "src" / building_id
    payload = icon.read_bytes()
    image_format = icon.suffix.removeprefix(".")
    bundle = ModuleSourceBundle(
        root=str(root),
        source_slots={"icon": (icon.name,)},
        metadata={"type": "building"},
        copy_sources=(
            CopySource(
                slot="icon",
                path=icon.name,
                output_path=icon.name,
                sha256=str(len(payload)),
                size=len(payload),
                media_type=f"image/{image_format}",
                format=image_format,
                width=8,
                height=8,
            ),
        ),
        module_id=f"building/{building_id}",
    )
    return Module(
        module_id=f"building/{building_id}",
        family="building",
        root=str(root),
        source_slots={"icon": (icon.name,)},
        metadata={"type": "building"},
        payload=bundle,
    )


def _support_module(tmp_path: Path, building_id: str) -> Module:
    root = tmp_path / "src" / building_id
    root.mkdir(parents=True)
    bundle = ModuleSourceBundle(
        root=str(root),
        source_slots={},
        metadata={"type": "building"},
        module_id=f"building/{building_id}",
    )
    return Module(
        module_id=f"building/{building_id}",
        family="building",
        root=str(root),
        source_slots={},
        metadata={"type": "building"},
        payload=bundle,
    )


def _image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size
