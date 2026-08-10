from __future__ import annotations

import os
import socket
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from paradev.build import DEFAULT_COLLECTION_SLOTS, DEFAULT_MODULE_SLOTS, Diagnostic, Slot, match_slots
from paradev.build.slots import match_slot_paths


def _write(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x", encoding="utf-8")


def test_slot_matching_supports_exact_glob_regex_and_many(tmp_path: Path) -> None:
    _write(tmp_path / "def.pdx")
    _write(tmp_path / "main.loc")
    _write(tmp_path / "extra.loc")
    _write(tmp_path / "icon.png")
    _write(tmp_path / "notes.txt")

    result = match_slots(
        tmp_path,
        (
            Slot("def", "def.pdx", required=True),
            Slot("loc", "*.loc", many=True),
            Slot("icon", r"^(icon|goal)\.(png|dds|tga)$", regex=True),
        ),
        module_id="focus/GER_sample",
    )

    assert result.source_slots == {
        "def": ("def.pdx",),
        "icon": ("icon.png",),
        "loc": ("extra.loc", "main.loc"),
    }
    assert result.diagnostics == ()


def test_slot_matching_validates_prospective_relative_paths_without_writing() -> None:
    result = match_slot_paths(
        ("mesh.gfx", "entity.asset", "gfx/models/tank/texture.dds"),
        (
            Slot("models", r"^gfx/models/.*\.(gfx|asset)$", required=True, many=True, regex=True),
            Slot("textures", r"^gfx/models/.*\.dds$", many=True, regex=True),
        ),
        module_id="entity/TANK",
    )

    assert result.source_slots == {"textures": ("gfx/models/tank/texture.dds",)}
    assert [diagnostic.code for diagnostic in result.diagnostics] == ["slot.missing_required"]
    assert result.diagnostics[0].module_id == "entity/TANK"


def test_slot_matching_supports_nested_globs(tmp_path: Path) -> None:
    _write(tmp_path / "loc/english.loc")
    _write(tmp_path / "loc/french.loc")

    result = match_slots(tmp_path, (Slot("loc", "loc/*.loc", many=True),))

    assert result.source_slots == {"loc": ("loc/english.loc", "loc/french.loc")}


def test_slot_matching_supports_recursive_loc_globs(tmp_path: Path) -> None:
    _write(tmp_path / "main.loc")
    _write(tmp_path / "loc/english.loc")
    _write(tmp_path / "loc/nested/french.loc")

    result = match_slots(tmp_path, (Slot("loc", "**/*.loc", many=True),))

    assert result.source_slots == {"loc": ("loc/english.loc", "loc/nested/french.loc", "main.loc")}


def test_default_module_slots_use_original_script_and_all_loc_sources(tmp_path: Path) -> None:
    _write(tmp_path / "def.txt")
    _write(tmp_path / "main.loc")
    _write(tmp_path / "loc/english.loc")

    result = match_slots(tmp_path, DEFAULT_MODULE_SLOTS)

    assert result.source_slots["def"] == ("def.txt",)
    assert result.source_slots["loc"] == ("loc/english.loc", "main.loc")


def test_default_collection_slots_use_original_script_and_all_loc_sources(tmp_path: Path) -> None:
    _write(tmp_path / "def.txt")
    _write(tmp_path / "main.loc")
    _write(tmp_path / "loc/english.loc")

    result = match_slots(tmp_path, DEFAULT_COLLECTION_SLOTS)

    assert result.source_slots == {"def": ("def.txt",), "loc": ("loc/english.loc", "main.loc")}


def test_slot_matching_merges_repeated_slot_names_in_path_order(tmp_path: Path) -> None:
    _write(tmp_path / "main.loc")
    _write(tmp_path / "loc/english.loc")
    _write(tmp_path / "loc/french.loc")

    result = match_slots(
        tmp_path,
        (
            Slot("loc", "main.loc", many=True),
            Slot("loc", "loc/*.loc", many=True),
        ),
        module_id="focus/GER_sample",
    )

    assert result.source_slots == {"loc": ("loc/english.loc", "loc/french.loc", "main.loc")}
    assert result.diagnostics == ()


def test_slot_matching_reports_multiple_matches_after_repeated_slot_merge(tmp_path: Path) -> None:
    _write(tmp_path / "icon.dds")
    _write(tmp_path / "icon.png")

    result = match_slots(
        tmp_path,
        (
            Slot("icon", "icon.png"),
            Slot("icon", "icon.dds"),
        ),
        module_id="idea/GER_sample",
    )

    assert result.source_slots == {"icon": ("icon.png",)}
    assert result.diagnostics[0].code == "slot.multiple_matches"
    assert result.diagnostics[0].message == "Slot 'icon' matched 2 files but many=False."
    assert result.diagnostics[0].module_id == "idea/GER_sample"
    assert result.diagnostics[0].slot == "icon"


def test_slot_matching_prioritizes_common_image_slot_formats(tmp_path: Path) -> None:
    for name in ("icon.bmp", "icon.tga", "icon.dds", "icon.jpg", "icon.png"):
        _write(tmp_path / name)

    result = match_slots(
        tmp_path,
        (Slot("icon", r"^icon\.(png|jpg|dds|tga|bmp)$", regex=True),),
        module_id="idea/GER_sample",
    )

    assert result.source_slots == {"icon": ("icon.png",)}
    assert result.diagnostics[0].code == "slot.multiple_matches"


def test_slot_matching_reports_missing_required_slots(tmp_path: Path) -> None:
    result = match_slots(tmp_path, (Slot("def", "def.pdx", required=True),), module_id="focus/GER_sample")

    assert result.source_slots == {}
    assert result.diagnostics[0].code == "slot.missing_required"
    assert result.diagnostics[0].module_id == "focus/GER_sample"
    assert result.diagnostics[0].slot == "def"


def test_slot_matching_treats_a_file_root_as_empty(tmp_path: Path) -> None:
    root = tmp_path / "not-a-module"
    _write(root)

    result = match_slots(root, (Slot("def", "def.pdx", required=True),))

    assert result.source_slots == {}
    assert [diagnostic.code for diagnostic in result.diagnostics] == ["slot.missing_required"]


@pytest.mark.skipif(os.name == "nt", reason="Creating these special files is not portable to Windows.")
def test_slot_matching_ignores_broken_symlinks_and_special_files() -> None:
    with TemporaryDirectory(prefix="paradev-slots-", dir="/tmp") as temporary:
        root = Path(temporary)
        os.symlink("missing.pdx", root / "broken.pdx")
        os.mkfifo(root / "pipe.pdx")
        socket_path = root / "socket.pdx"
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            listener.bind(str(socket_path))

            result = match_slots(
                root,
                (Slot("def", "*.pdx", required=True, many=True),),
            )
        finally:
            listener.close()

    assert result.source_slots == {}
    assert [diagnostic.code for diagnostic in result.diagnostics] == ["slot.missing_required"]


def test_slot_matching_reports_parent_traversal_slot_matches(tmp_path: Path) -> None:
    root = tmp_path / "GER_sample"
    root.mkdir()
    _write(tmp_path / "outside.pdx")

    result = match_slots(root, (Slot("def", "../outside.pdx", required=True),), module_id="focus/GER_sample")

    assert result.source_slots == {}
    assert result.diagnostics == (
        Diagnostic(
            code="slot.invalid_match",
            message="Slot 'def' match '../outside.pdx' must be relative and stay under the source root.",
            module_id="focus/GER_sample",
            slot="def",
        ),
    )


def test_slot_matching_reports_invalid_regex_slots(tmp_path: Path) -> None:
    _write(tmp_path / "def.pdx")

    result = match_slots(tmp_path, (Slot("def", "[", regex=True, required=True),), module_id="focus/GER_sample")

    assert result.source_slots == {}
    assert result.diagnostics[0].code == "slot.invalid_regex"
    assert result.diagnostics[0].module_id == "focus/GER_sample"
    assert result.diagnostics[0].slot == "def"
    assert "must be a valid regex" in result.diagnostics[0].message


def test_slot_matching_reports_source_collisions(tmp_path: Path) -> None:
    _write(tmp_path / "main.loc")

    result = match_slots(tmp_path, (Slot("loc", "*.loc", many=True), Slot("copy", "*.loc", many=True)), module_id="focus/GER_sample")

    assert result.source_slots == {"copy": ("main.loc",), "loc": ("main.loc",)}
    assert result.diagnostics[0].code == "slot.source_collision"
    assert result.diagnostics[0].slot == "copy"
    assert result.diagnostics[0].slots == ("copy", "loc")
    assert result.diagnostics[0].source_path == "main.loc"


def test_slot_matching_allows_explicit_shared_source_ownership(tmp_path: Path) -> None:
    _write(tmp_path / "main.loc")

    result = match_slots(
        tmp_path,
        (
            Slot("loc", "*.loc", many=True, shared=True),
            Slot("copy", "*.loc", many=True, shared=True),
        ),
        module_id="focus/GER_sample",
    )

    assert result.source_slots == {"copy": ("main.loc",), "loc": ("main.loc",)}
    assert result.diagnostics == ()


def test_slot_matching_reports_source_collisions_when_only_one_slot_is_shared(tmp_path: Path) -> None:
    _write(tmp_path / "main.loc")

    result = match_slots(
        tmp_path,
        (
            Slot("loc", "*.loc", many=True, shared=True),
            Slot("copy", "*.loc", many=True),
        ),
        module_id="focus/GER_sample",
    )

    assert result.source_slots == {"copy": ("main.loc",), "loc": ("main.loc",)}
    assert result.diagnostics[0].code == "slot.source_collision"
    assert result.diagnostics[0].slots == ("copy", "loc")
