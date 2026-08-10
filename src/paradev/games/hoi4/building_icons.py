"""HoI4 building icon strip generation from per-building module icons."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Set
from dataclasses import dataclass, replace
from pathlib import Path
import tempfile

from heavenbase.utils import sha256hash
from PIL import Image

from paradev.build._fs import AnchoredDirectory, open_anchored_directory
from paradev.build import Artifact, BuildResult, Module, ModuleSourceBundle, SpriteType
from paradev.pdx import PDXBlock, PDXScalar

BUILDING_ICON_STRIP_PATH = Path("gfx/interface/buildings/building_icon_strip.dds")
BUILDING_STRIP_SPRITE_NAME = "GFX_buildings_strip"
DEFAULT_BUILDING_ICON_FRAME_SIZE = 46
BUILDING_ICON_POSTPROCESSOR = "hoi4.building_icon_strip"


@dataclass(frozen=True, slots=True)
class BuildingIconStripSummary:
    """Summary of a generated HoI4 building icon strip.

    Args:
        frame_count: Number of atlas frames generated.
        frame_by_building_id: One-based atlas frame for each building id.
        strip_path: Filesystem path of the generated DDS atlas.
        rewritten_building_files: Emitted building definitions whose frame ids
            were rewritten.
        updated_gfx_files: Emitted interface declarations whose frame count was
            updated.
        artifacts: Final emitted artifact descriptors to reconcile into the
            build result before manifests are written.
    """

    frame_count: int
    frame_by_building_id: dict[str, int]
    strip_path: Path
    rewritten_building_files: tuple[Path, ...] = ()
    updated_gfx_files: tuple[Path, ...] = ()
    artifacts: tuple[Artifact, ...] = ()


@dataclass(frozen=True, slots=True)
class _BuildingIconRecord:
    building_id: str
    module_id: str
    source_path: Path


def postprocess_building_icon_strip(
    result: BuildResult,
    *,
    output_root: Path,
    frame_size: int = DEFAULT_BUILDING_ICON_FRAME_SIZE,
) -> BuildingIconStripSummary:
    """Generate the HoI4 building atlas and remap emitted building frame ids.

    Args:
        result: Planned build result whose building modules own icon sources.
        output_root: Emitted mod root containing building and interface files.
        frame_size: Width and height of each generated atlas frame.

    Returns:
        Generated frame summary plus emitted artifact deltas for the strip and
        every rewritten output file.
    """

    with open_anchored_directory(output_root) as publication_root:
        return _postprocess_building_icon_strip_anchored(
            result,
            output_root=publication_root,
            frame_size=frame_size,
        )


def _postprocess_building_icon_strip_anchored(
    result: BuildResult,
    *,
    output_root: AnchoredDirectory,
    frame_size: int = DEFAULT_BUILDING_ICON_FRAME_SIZE,
    on_written: Callable[[Artifact, Path], None] | None = None,
    replace_paths: Set[str] | None = None,
    adopt_paths: Set[str] | None = None,
    rename_paths: Mapping[str, str] | None = None,
) -> BuildingIconStripSummary:
    """Stage and publish building-icon deltas through one retained root."""

    with tempfile.TemporaryDirectory(prefix="paradev-building-publication-") as temp_dir:
        staging_root = Path(temp_dir)
        stage_paths = {Path("common") / "buildings" / f"{record.building_id}.txt" for record in _building_icon_records(result)}
        for artifact in result.artifacts:
            path = Path(str(artifact.path).replace("\\", "/"))
            if artifact.target_root != "output" or not (
                path.parts[:2] == ("common", "buildings") or (path.parts[:1] == ("interface",) and path.suffix == ".gfx")
            ):
                continue
            stage_paths.add(path)
        for path in sorted(stage_paths):
            payload = output_root.read_bytes(path.as_posix())
            if payload is None:
                continue
            target = staging_root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)

        summary = _postprocess_building_icon_strip_path(
            result,
            output_root=staging_root,
            frame_size=frame_size,
        )
        for artifact in summary.artifacts:
            artifact_path = str(artifact.path).replace("\\", "/")
            previous_spelling = rename_paths.get(artifact_path) if rename_paths is not None else None
            replace_existing = replace_paths is None or artifact_path in replace_paths
            staged_path = staging_root / str(artifact.path)
            unchanged = False
            if replace_existing:
                try:
                    comparison = output_root.file_matches(artifact_path, staged_path)
                except ValueError:
                    comparison = None
                if comparison is None:
                    replace_existing = False
                else:
                    unchanged = comparison and previous_spelling is None
            elif adopt_paths is not None and artifact_path in adopt_paths:
                try:
                    comparison = output_root.file_matches(artifact_path, staged_path)
                except ValueError as error:
                    raise ValueError(f"Cached build cannot recover non-regular untracked postprocessed artifact: {artifact_path}.") from error
                if comparison is not None:
                    if not comparison:
                        raise ValueError(f"Cached build refuses to adopt an untracked postprocessed artifact whose content differs: {artifact_path}.")
                    unchanged = True
            path = (
                output_root.requested_path / artifact_path
                if unchanged
                else output_root.publish_file(
                    artifact_path,
                    staged_path,
                    replace=replace_existing,
                )
            )
            if previous_spelling is not None:
                normalized = output_root.normalize_path_spelling(
                    previous_spelling,
                    artifact_path,
                )
                if not normalized:
                    raise ValueError(
                        "Cached build could not normalize a tracked " f"postprocessed artifact path spelling: " f"{previous_spelling} -> {artifact_path}."
                    )
            if on_written is not None:
                on_written(artifact, path)
        return replace(
            summary,
            strip_path=output_root.requested_path / BUILDING_ICON_STRIP_PATH,
            rewritten_building_files=tuple(output_root.requested_path / path.relative_to(staging_root) for path in summary.rewritten_building_files),
            updated_gfx_files=tuple(output_root.requested_path / path.relative_to(staging_root) for path in summary.updated_gfx_files),
        )


def _postprocess_building_icon_strip_path(
    result: BuildResult,
    *,
    output_root: Path,
    frame_size: int,
) -> BuildingIconStripSummary:
    """Run the postprocessor only inside a caller-controlled staging root."""

    records = _building_icon_records(result)
    target = output_root / BUILDING_ICON_STRIP_PATH
    if not records:
        return BuildingIconStripSummary(frame_count=0, frame_by_building_id={}, strip_path=target)

    frame_by_building_id = {record.building_id: index for index, record in enumerate(records, start=1)}
    _write_icon_strip(records, target, frame_size=frame_size)
    rewritten = _rewrite_building_frames(output_root, frame_by_building_id)
    updated_gfx = _update_building_strip_gfx_frames(output_root, frame_count=len(records))
    artifacts = _postprocessed_artifacts(
        result,
        output_root=output_root,
        records=records,
        strip_path=target,
        rewritten_building_files=rewritten,
        updated_gfx_files=updated_gfx,
        frame_size=frame_size,
    )
    return BuildingIconStripSummary(
        frame_count=len(records),
        frame_by_building_id=frame_by_building_id,
        strip_path=target,
        rewritten_building_files=tuple(rewritten),
        updated_gfx_files=tuple(updated_gfx),
        artifacts=artifacts,
    )


def _planned_building_icon_strip(result: BuildResult) -> Artifact | None:
    """Return the predictable postprocessor-only strip publication row."""

    records = _building_icon_records(result)
    if not records:
        return None
    return Artifact(
        path=BUILDING_ICON_STRIP_PATH,
        artifact_type="building_icon_strip",
        owner=f"project:{result.project_id}",
        inputs=tuple(record.source_path for record in records),
        target_root="output",
        metadata={
            "family": "building",
            "module_ids": [record.module_id for record in records],
            "postprocessor": BUILDING_ICON_POSTPROCESSOR,
        },
    )


def _building_icon_stage_transform(result: BuildResult) -> Callable[[Artifact, Path], None]:
    """Return a writer-stage transform for final building frame values."""

    records = _building_icon_records(result)
    frame_by_building_id = {record.building_id: index for index, record in enumerate(records, start=1)}
    frame_count = len(records)

    def transform(artifact: Artifact, path: Path) -> None:
        artifact_path = Path(_artifact_path(artifact))
        if artifact.target_root != "output":
            return
        if artifact_path.parts[:2] == ("common", "buildings") and artifact_path.suffix == ".txt":
            frame = frame_by_building_id.get(artifact_path.stem)
            if frame is None:
                return
            block = PDXBlock.from_file(path)
            if _set_building_icon_frame(block, building_id=artifact_path.stem, frame=frame):
                block.to_file(path)
            return
        if artifact_path.parts[:1] != ("interface",) or artifact_path.suffix != ".gfx":
            return
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if BUILDING_STRIP_SPRITE_NAME not in text:
            return
        block = PDXBlock.from_str(text)
        if _set_building_strip_no_of_frames(block, frame_count=frame_count):
            block.to_file(path)

    return transform


def _building_icon_stage_transform_required(artifact: Artifact) -> bool:
    """Return whether building-icon finalization can change one artifact."""

    if artifact.target_root != "output":
        return False
    artifact_path = Path(_artifact_path(artifact))
    return (artifact_path.parts[:2] == ("common", "buildings") and artifact_path.suffix == ".txt") or (
        artifact_path.parts[:1] == ("interface",) and artifact_path.suffix == ".gfx"
    )


def _postprocessed_artifacts(
    result: BuildResult,
    *,
    output_root: Path,
    records: tuple[_BuildingIconRecord, ...],
    strip_path: Path,
    rewritten_building_files: list[Path],
    updated_gfx_files: list[Path],
    frame_size: int,
) -> tuple[Artifact, ...]:
    planned = {_artifact_path(artifact): artifact for artifact in result.artifacts if artifact.target_root == "output"}
    module_ids = tuple(record.module_id for record in records)
    deltas = [
        _emitted_artifact(
            strip_path,
            output_root=output_root,
            artifact_type="building_icon_strip",
            owner=f"project:{result.project_id}",
            inputs=tuple(record.source_path for record in records),
            metadata={
                "format": "dds",
                "frame_count": len(records),
                "height": frame_size,
                "media_type": "image/vnd-ms.dds",
                "module_ids": list(module_ids),
                "width": frame_size * len(records),
            },
        )
    ]
    records_by_id = {record.building_id: record for record in records}
    for path in rewritten_building_files:
        relative_path = _relative_artifact_path(path, output_root)
        original = planned.get(relative_path)
        record = records_by_id.get(path.stem)
        deltas.append(
            _emitted_artifact(
                path,
                output_root=output_root,
                original=original,
                artifact_type="pdx",
                owner=f"module:{record.module_id}" if record is not None else f"project:{result.project_id}",
                inputs=_module_slot_inputs(result, record.module_id, "def") if record is not None else (),
            )
        )
    for path in updated_gfx_files:
        relative_path = _relative_artifact_path(path, output_root)
        original = planned.get(relative_path)
        artifact = _emitted_artifact(
            path,
            output_root=output_root,
            original=original,
            artifact_type="pdx",
            owner=f"project:{result.project_id}",
        )
        if original is not None and original.artifact_type == "sprite_gfx":
            artifact = replace(artifact, payload=_building_strip_sprite_payload(original.payload, frame_count=len(records)))
        deltas.append(artifact)
    return tuple(deltas)


def _emitted_artifact(
    path: Path,
    *,
    output_root: Path,
    artifact_type: str,
    owner: str,
    original: Artifact | None = None,
    inputs: tuple[str | Path, ...] = (),
    metadata: dict[str, object] | None = None,
) -> Artifact:
    payload = path.read_bytes()
    emitted_metadata = dict(original.metadata) if original is not None else {}
    if original is not None and original.artifact_type == "copy":
        _preserve_copy_source_metadata(emitted_metadata, original.inputs)
    emitted_metadata.update(metadata or {})
    if "byte_size" in emitted_metadata:
        emitted_metadata["byte_size"] = len(payload)
    emitted_metadata.update(
        {
            "postprocessor": BUILDING_ICON_POSTPROCESSOR,
            "sha256": sha256hash(payload),
            "size": len(payload),
        }
    )
    return Artifact(
        path=_relative_artifact_path(path, output_root),
        artifact_type=original.artifact_type if original is not None else artifact_type,
        owner=original.owner if original is not None else owner,
        inputs=original.inputs if original is not None else inputs,
        mode="emit",
        target_root="output",
        metadata=emitted_metadata,
        payload=original.payload if original is not None else None,
    )


def _preserve_copy_source_metadata(metadata: dict[str, object], inputs: tuple[str | Path, ...]) -> None:
    if inputs:
        source_payload = Path(inputs[0]).read_bytes()
        metadata["source_sha256"] = sha256hash(source_payload)
        metadata["source_size"] = len(source_payload)
        return
    source_sha256 = metadata.get("sha256")
    if isinstance(source_sha256, str) and source_sha256:
        metadata["source_sha256"] = source_sha256
    source_size = metadata.get("size", metadata.get("byte_size"))
    if type(source_size) is int:
        metadata["source_size"] = source_size


def _building_strip_sprite_payload(payload: object, *, frame_count: int) -> object:
    if not isinstance(payload, tuple):
        return payload
    return tuple(
        (
            replace(sprite, properties={**sprite.properties, "noOfFrames": frame_count})
            if isinstance(sprite, SpriteType) and sprite.name == BUILDING_STRIP_SPRITE_NAME
            else sprite
        )
        for sprite in payload
    )


def _module_slot_inputs(result: BuildResult, module_id: str, slot: str) -> tuple[Path, ...]:
    for module in result.modules:
        if module.module_id != module_id:
            continue
        return tuple(Path(module.root) / path for path in module.source_slots.get(slot, ()))
    return ()


def _artifact_path(artifact: Artifact) -> str:
    return str(artifact.path).replace("\\", "/")


def _relative_artifact_path(path: Path, output_root: Path) -> str:
    return path.relative_to(output_root).as_posix()


def _building_icon_records(result: BuildResult) -> tuple[_BuildingIconRecord, ...]:
    records: list[_BuildingIconRecord] = []
    for module in result.modules:
        if module.family != "building":
            continue
        icon_path = _module_icon_path(module)
        if icon_path is None:
            continue
        records.append(_BuildingIconRecord(building_id=_module_object_id(module), module_id=module.module_id, source_path=icon_path))
    return tuple(sorted(records, key=lambda record: record.building_id))


def _module_icon_path(module: Module) -> Path | None:
    if isinstance(module.payload, ModuleSourceBundle):
        root = Path(module.payload.root)
        for source in module.payload.copy_sources:
            if source.slot == "icon":
                path = root / source.path
                if path.is_file():
                    return path
    for rel_path in module.source_slots.get("icon", ()):
        path = Path(module.root) / rel_path
        if path.is_file():
            return path
    return None


def _module_object_id(module: Module) -> str:
    if "/" in module.module_id:
        return module.module_id.split("/", 1)[1]
    return Path(module.root).name


def _write_icon_strip(records: tuple[_BuildingIconRecord, ...], target: Path, *, frame_size: int) -> None:
    if frame_size <= 0:
        raise ValueError("HoI4 building icon frame size must be greater than zero.")
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.new(
        "RGBA",
        (frame_size * len(records), frame_size),
        (0, 0, 0, 0),
    ) as strip:
        for index, record in enumerate(records):
            with _pillow_icon_frame(record.source_path, frame_size=frame_size) as frame:
                strip.alpha_composite(frame, (index * frame_size, 0))
        try:
            strip.save(target, format="DDS", pixel_format="DXT5")
        except (OSError, ValueError) as error:
            raise RuntimeError(f"Pillow failed to write HoI4 building icon strip {target}: {error}") from error


def _pillow_icon_frame(source: Path, *, frame_size: int) -> Image.Image:
    try:
        with Image.open(source) as image:
            image.load()
            icon = image.convert("RGBA")
    except (OSError, ValueError) as error:
        raise RuntimeError(f"Pillow failed to read HoI4 building icon {source}: {error}") from error

    scale = min(frame_size / icon.width, frame_size / icon.height)
    resized_size = (
        max(1, min(frame_size, round(icon.width * scale))),
        max(1, min(frame_size, round(icon.height * scale))),
    )
    with icon, icon.resize(resized_size, Image.Resampling.LANCZOS) as resized:
        frame = Image.new("RGBA", (frame_size, frame_size), (0, 0, 0, 0))
        frame.alpha_composite(
            resized,
            (
                (frame_size - resized.width) // 2,
                (frame_size - resized.height) // 2,
            ),
        )
    return frame


def _rewrite_building_frames(output_root: Path, frame_by_building_id: dict[str, int]) -> list[Path]:
    rewritten: list[Path] = []
    for building_id, frame in sorted(frame_by_building_id.items()):
        path = output_root / "common" / "buildings" / f"{building_id}.txt"
        if not path.is_file():
            continue
        block = PDXBlock.from_file(path)
        if _set_building_icon_frame(block, building_id=building_id, frame=frame):
            block.to_file(path)
            rewritten.append(path)
    return rewritten


def _set_building_icon_frame(block: PDXBlock, *, building_id: str, frame: int) -> bool:
    wrapper = block.find("buildings")
    if wrapper is None or not isinstance(wrapper.val, PDXBlock):
        return False
    for entry in wrapper.val.entries:
        if entry.key_str != building_id or not isinstance(entry.val, PDXBlock):
            continue
        entry.val["icon_frame"] = frame
        return True
    return False


def _update_building_strip_gfx_frames(output_root: Path, *, frame_count: int) -> list[Path]:
    interface_root = output_root / "interface"
    if not interface_root.is_dir():
        return []
    updated: list[Path] = []
    for path in sorted(interface_root.rglob("*.gfx")):
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        if BUILDING_STRIP_SPRITE_NAME not in text:
            continue
        block = PDXBlock.from_str(text)
        if _set_building_strip_no_of_frames(block, frame_count=frame_count):
            block.to_file(path)
            updated.append(path)
    return updated


def _set_building_strip_no_of_frames(block: PDXBlock, *, frame_count: int) -> bool:
    changed = False
    for sprite_block in _nested_blocks(block, "SpriteType"):
        name_entry = sprite_block.find("name")
        if name_entry is None or not isinstance(name_entry.val, PDXScalar):
            continue
        if str(name_entry.val.val) != BUILDING_STRIP_SPRITE_NAME:
            continue
        sprite_block["noOfFrames"] = frame_count
        changed = True
    return changed


def _nested_blocks(block: PDXBlock, key: str) -> tuple[PDXBlock, ...]:
    out: list[PDXBlock] = []
    normalized_key = key.lower()
    for entry in block.entries:
        if not isinstance(entry.val, PDXBlock):
            continue
        if (entry.key_str or "").lower() == normalized_key:
            out.append(entry.val)
        out.extend(_nested_blocks(entry.val, key))
    return tuple(out)
