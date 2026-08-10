from __future__ import annotations

import hashlib
from pathlib import Path
from struct import pack

from heavenbase.utils import sha256hash
import pytest
import yaml

import paradev.build.loaders as loaders
from paradev.build import Diagnostic, load_collection_metadata, load_copy_sources, load_metadata, load_pdx_sources
from paradev.pdx import PDXBlock


def test_metadata_loader_reads_meta_yaml_and_infers_folder_identity(tmp_path: Path) -> None:
    root = tmp_path / "GER_rearmament - optional note"
    root.mkdir()
    (root / "meta.yaml").write_text(
        "\n".join(
            [
                "type: focus",
                "game_id: GER_rebuild_the_ruhr",
                "collection: GER_main",
                "owner: GER",
                "priority: 20",
                "tags: [industry, early_game]",
                "settings:",
                "  icon_fit: cover",
            ]
        ),
        encoding="utf-8",
    )

    result = load_metadata(root, inferred_type="focus", module_id="focus/GER_rearmament")

    assert result.diagnostics == ()
    assert result.metadata == {
        "object_id": "GER_rearmament",
        "note": "optional note",
        "title": "optional note",
        "type": "focus",
        "game_id": "GER_rebuild_the_ruhr",
        "collection": "GER_main",
        "owner": "GER",
        "priority": 20,
        "tags": ["industry", "early_game"],
        "settings": {"icon_fit": "cover"},
    }


def test_metadata_loader_allows_missing_meta_yaml_when_identity_is_inferred(
    tmp_path: Path,
) -> None:
    root = tmp_path / "GER_industry_spirit"
    root.mkdir()

    result = load_metadata(
        root,
        inferred_type="idea",
        module_id="idea/GER_industry_spirit",
    )

    assert result.metadata == {
        "object_id": "GER_industry_spirit",
        "type": "idea",
    }
    assert result.diagnostics == ()


def test_metadata_loader_reports_type_mismatch(tmp_path: Path) -> None:
    root = tmp_path / "GER_rearmament"
    root.mkdir()
    (root / "meta.yaml").write_text("type: event\n", encoding="utf-8")

    result = load_metadata(root, inferred_type="focus", module_id="focus/GER_rearmament")

    assert result.metadata["object_id"] == "GER_rearmament"
    assert result.diagnostics[0].code == "metadata.type_mismatch"
    assert result.diagnostics[0].module_id == "focus/GER_rearmament"
    assert result.diagnostics[0].source_path == "meta.yaml"


def test_metadata_loader_promotes_unknown_keys_when_strict(tmp_path: Path) -> None:
    root = tmp_path / "GER_rearmament"
    root.mkdir()
    (root / "meta.yaml").write_text("type: focus\nlegacy_hint: yes\n", encoding="utf-8")

    loose = load_metadata(root, inferred_type="focus", module_id="focus/GER_rearmament")
    strict = load_metadata(root, inferred_type="focus", module_id="focus/GER_rearmament", strict_metadata=True)

    assert loose.diagnostics == (
        Diagnostic(
            code="metadata.unknown_key",
            message="Unknown metadata key 'legacy_hint'.",
            severity="warning",
            module_id="focus/GER_rearmament",
            source_path="meta.yaml",
        ),
    )
    assert strict.diagnostics == (
        Diagnostic(
            code="metadata.unknown_key",
            message="Unknown metadata key 'legacy_hint'.",
            severity="error",
            module_id="focus/GER_rearmament",
            source_path="meta.yaml",
        ),
    )


def test_metadata_loader_merges_hidden_system_metadata_with_visible_overrides(
    tmp_path: Path,
) -> None:
    root = tmp_path / "GER_rearmament - Rearmament"
    (root / ".paradev").mkdir(parents=True)
    (root / ".paradev/meta.yaml").write_text(
        "settings:\n  migration_id: old\n  route: compiled\n" "tags:\n  - imported\n",
        encoding="utf-8",
    )
    (root / "meta.yaml").write_text(
        "title: Rearmament\nsettings:\n  route: authored\n",
        encoding="utf-8",
    )

    result = load_metadata(
        root,
        inferred_type="focus",
        module_id="focus/GER_rearmament",
    )

    assert result.diagnostics == ()
    assert result.metadata == {
        "object_id": "GER_rearmament",
        "note": "Rearmament",
        "type": "focus",
        "title": "Rearmament",
        "tags": ["imported"],
        "settings": {
            "migration_id": "old",
            "route": "authored",
        },
    }


def test_metadata_loader_reports_malformed_yaml_as_diagnostic(tmp_path: Path) -> None:
    root = tmp_path / "GER_rearmament"
    root.mkdir()
    (root / "meta.yaml").write_text("type: [unterminated\n", encoding="utf-8")

    result = load_metadata(root, inferred_type="focus", module_id="focus/GER_rearmament")

    assert result.metadata == {"object_id": "GER_rearmament", "type": "focus"}
    assert result.diagnostics == (
        Diagnostic(
            code="metadata.invalid_yaml",
            message="meta.yaml contains invalid YAML.",
            module_id="focus/GER_rearmament",
            source_path="meta.yaml",
        ),
    )


def test_metadata_loader_prefers_the_available_safe_c_loader() -> None:
    assert loaders._MetadataYamlLoader is getattr(yaml, "CSafeLoader", yaml.SafeLoader)


@pytest.mark.parametrize(
    "loader",
    [yaml.SafeLoader, getattr(yaml, "CSafeLoader", yaml.SafeLoader)],
)
def test_metadata_loader_rejects_unsafe_python_tags(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    loader: type[yaml.SafeLoader],
) -> None:
    root = tmp_path / "GER_rearmament"
    root.mkdir()
    (root / "meta.yaml").write_text(
        "settings: !!python/object/apply:builtins.eval ['1 + 1']\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(loaders, "_MetadataYamlLoader", loader)

    result = load_metadata(root, inferred_type="focus", module_id="focus/GER_rearmament")

    assert result.metadata == {"object_id": "GER_rearmament", "type": "focus"}
    assert result.diagnostics[0].code == "metadata.invalid_yaml"


def test_metadata_loader_uses_heavenbase_text_file_policy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "GER_rearmament"
    root.mkdir()
    metadata_path = root / "meta.yaml"
    metadata_path.write_text("ignored by fake loader", encoding="utf-8")
    calls: list[tuple[str, str | None, bool]] = []

    def fake_load_txt(path: str, encoding: str | None = None, *, strict: bool = False) -> str:
        calls.append((path, encoding, strict))
        return "type: focus\n"

    monkeypatch.setattr(loaders, "load_txt", fake_load_txt)

    result = load_metadata(root, inferred_type="focus", module_id="focus/GER_rearmament")

    assert result.diagnostics == ()
    assert calls == [(str(metadata_path), "utf-8", True)]


def test_metadata_loader_reports_non_regular_yaml_without_reading(
    tmp_path: Path,
) -> None:
    root = tmp_path / "GER_rearmament"
    root.mkdir()
    (root / "meta.yaml").mkdir()

    result = load_metadata(root, inferred_type="focus", module_id="focus/GER_rearmament")

    assert result.metadata == {"object_id": "GER_rearmament", "type": "focus"}
    assert result.diagnostics[0].code == "metadata.unreadable_source"


def test_metadata_loader_reports_unreadable_yaml_as_diagnostic(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "GER_rearmament"
    root.mkdir()
    (root / "meta.yaml").write_text("type: focus\n", encoding="utf-8")

    def fail_read_text(self: Path, *args: object, **kwargs: object) -> str:
        raise OSError("permission denied")

    monkeypatch.setattr(Path, "read_text", fail_read_text)

    result = load_metadata(root, inferred_type="focus", module_id="focus/GER_rearmament")

    assert result.metadata == {"object_id": "GER_rearmament", "type": "focus"}
    assert result.diagnostics == (
        Diagnostic(
            code="metadata.unreadable_source",
            message="meta.yaml cannot be read. permission denied.",
            module_id="focus/GER_rearmament",
            source_path="meta.yaml",
        ),
    )


def test_collection_metadata_loader_reads_descriptor_and_infers_identity(tmp_path: Path) -> None:
    root = tmp_path / "GER_main"
    root.mkdir()
    (root / "meta.yaml").write_text(
        "\n".join(
            [
                "type: focus_tree",
                "title: German Focus Tree",
                "owner: GER",
                "priority: 5",
                "members:",
                "  - GER_rhineland",
                "  - focus/GER_four_year_plan",
                "settings:",
                "  layout: historical",
            ]
        ),
        encoding="utf-8",
    )

    result = load_collection_metadata(root, family="focus")

    assert result.diagnostics == ()
    assert result.collection.collection_id == "GER_main"
    assert result.collection.family == "focus"
    assert result.collection.module_ids == (
        "focus/GER_rhineland",
        "focus/GER_four_year_plan",
    )
    assert result.collection.metadata == {
        "object_id": "GER_main",
        "type": "focus_tree",
        "title": "German Focus Tree",
        "owner": "GER",
        "priority": 5,
        "members": ["GER_rhineland", "focus/GER_four_year_plan"],
        "settings": {"layout": "historical"},
    }


def test_collection_metadata_loader_merges_hidden_system_metadata(
    tmp_path: Path,
) -> None:
    root = tmp_path / "GER_main - Germany"
    (root / ".paradev").mkdir(parents=True)
    (root / ".paradev/meta.yaml").write_text(
        "settings:\n  migration_id: old\nmembers:\n  - GER_a\n",
        encoding="utf-8",
    )
    (root / "meta.yaml").write_text(
        "title: Germany\nmembers:\n  - GER_b\n",
        encoding="utf-8",
    )

    result = load_collection_metadata(root, family="focus")

    assert result.diagnostics == ()
    assert result.collection.collection_id == "GER_main"
    assert result.collection.module_ids == ("focus/GER_b",)
    assert result.collection.metadata["settings"] == {
        "migration_id": "old",
    }


def test_collection_metadata_loader_rejects_invalid_or_duplicate_members(
    tmp_path: Path,
) -> None:
    root = tmp_path / "GER_main"
    root.mkdir()
    (root / "meta.yaml").write_text(
        "\n".join(
            (
                "members:",
                "  - GER_rhineland",
                "  - GER_rhineland",
                "  - idea/not_a_focus",
                "  - 7",
                "",
            )
        ),
        encoding="utf-8",
    )

    result = load_collection_metadata(root, family="focus")

    assert result.collection.module_ids == ("focus/GER_rhineland",)
    assert [diagnostic.code for diagnostic in result.diagnostics] == [
        "collection_metadata.duplicate_member",
        "collection_metadata.invalid_member",
        "collection_metadata.invalid_member",
    ]


def test_collection_metadata_loader_reports_malformed_yaml_as_diagnostic(tmp_path: Path) -> None:
    root = tmp_path / "GER_main"
    root.mkdir()
    (root / "collection.yaml").write_text("settings: [unterminated\n", encoding="utf-8")

    result = load_collection_metadata(root, family="focus")

    assert result.collection.collection_id == "GER_main"
    assert result.collection.metadata == {"object_id": "GER_main"}
    assert result.diagnostics == (
        Diagnostic(
            code="collection_metadata.invalid_yaml",
            message="Collection metadata contains invalid YAML.",
            collection_id="GER_main",
            source_path="collection.yaml",
        ),
    )


def test_collection_metadata_loader_reports_unreadable_yaml_as_diagnostic(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / "GER_main"
    root.mkdir()
    (root / "collection.yaml").write_text("title: German Focus Tree\n", encoding="utf-8")

    def fail_read_text(self: Path, *args: object, **kwargs: object) -> str:
        raise OSError("permission denied")

    monkeypatch.setattr(Path, "read_text", fail_read_text)

    result = load_collection_metadata(root, family="focus")

    assert result.collection.collection_id == "GER_main"
    assert result.collection.metadata == {"object_id": "GER_main"}
    assert result.diagnostics == (
        Diagnostic(
            code="collection_metadata.unreadable_source",
            message="Collection metadata cannot be read. permission denied.",
            collection_id="GER_main",
            source_path="collection.yaml",
        ),
    )


def test_pdx_loader_parses_sources_in_deterministic_order(tmp_path: Path) -> None:
    (tmp_path / "def.pdx").write_text("focus = { id = GER_sample }", encoding="utf-8")
    (tmp_path / "extra.pdx").write_text("priority > 5", encoding="utf-8")

    result = load_pdx_sources(tmp_path, {"def": ("def.pdx",), "extra": ("extra.pdx",)}, module_id="focus/GER_sample")

    assert result.diagnostics == ()
    assert [(source.slot, source.path, source.block.to_dict(), source.block.file_ext) for source in result.sources] == [
        ("def", "def.pdx", PDXBlock.from_str("focus = { id = GER_sample }").to_dict(), ".pdx"),
        ("extra", "extra.pdx", PDXBlock.from_str("priority > 5").to_dict(), ".pdx"),
    ]


def test_pdx_loader_reports_parse_diagnostics(tmp_path: Path) -> None:
    (tmp_path / "def.pdx").write_text("focus = { id = GER_sample", encoding="utf-8")

    result = load_pdx_sources(tmp_path, {"def": ("def.pdx",)}, module_id="focus/GER_sample")

    assert result.sources == ()
    assert result.diagnostics[0].code == "pdx.unclosed_block"
    assert result.diagnostics[0].slot == "def"
    assert result.diagnostics[0].source_path == "def.pdx"


def test_pdx_loader_reports_missing_source_as_diagnostic(tmp_path: Path) -> None:
    result = load_pdx_sources(tmp_path, {"def": ("missing.pdx",)}, module_id="focus/GER_sample")

    assert result.sources == ()
    assert result.diagnostics == (
        Diagnostic(
            code="pdx.missing_source",
            message="PDX source missing.pdx does not exist.",
            module_id="focus/GER_sample",
            slot="def",
            source_path="missing.pdx",
        ),
    )


def test_pdx_loader_reports_unreadable_source_as_diagnostic(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "def.pdx").write_text("focus = { id = GER_sample }", encoding="utf-8")

    def fail_read_text(self: Path, *args: object, **kwargs: object) -> str:
        if self.name == "def.pdx":
            raise OSError("permission denied")
        return original_read_text(self, *args, **kwargs)

    original_read_text = Path.read_text
    monkeypatch.setattr(Path, "read_text", fail_read_text)

    result = load_pdx_sources(tmp_path, {"def": ("def.pdx",)}, module_id="focus/GER_sample")

    assert result.sources == ()
    assert result.diagnostics == (
        Diagnostic(
            code="pdx.unreadable_source",
            message="PDX source def.pdx cannot be read. permission denied.",
            module_id="focus/GER_sample",
            slot="def",
            source_path="def.pdx",
        ),
    )


def test_pdx_loader_reports_missing_operator_value_diagnostics(tmp_path: Path) -> None:
    (tmp_path / "def.pdx").write_text("focus =", encoding="utf-8")

    result = load_pdx_sources(tmp_path, {"def": ("def.pdx",)}, module_id="focus/GER_sample")

    assert result.sources == ()
    assert result.diagnostics[0].code == "pdx.missing_value"
    assert result.diagnostics[0].message == "PDX operator '=' requires a value."
    assert result.diagnostics[0].module_id == "focus/GER_sample"
    assert result.diagnostics[0].slot == "def"
    assert result.diagnostics[0].source_path == "def.pdx"
    assert result.diagnostics[0].span == {"line": 1, "column": 7}


def test_pdx_loader_reports_unterminated_string_diagnostics(tmp_path: Path) -> None:
    (tmp_path / "def.pdx").write_text('name = "GFX_goal', encoding="utf-8")

    result = load_pdx_sources(tmp_path, {"def": ("def.pdx",)}, module_id="focus/GER_sample")

    assert result.sources == ()
    assert result.diagnostics[0].code == "pdx.unterminated_string"
    assert result.diagnostics[0].message == "Unterminated PDX string."
    assert result.diagnostics[0].module_id == "focus/GER_sample"
    assert result.diagnostics[0].slot == "def"
    assert result.diagnostics[0].source_path == "def.pdx"
    assert result.diagnostics[0].span == {"line": 1, "column": 8}


def test_pdx_loader_reports_empty_variable_diagnostics(tmp_path: Path) -> None:
    (tmp_path / "def.pdx").write_text("value = @", encoding="utf-8")

    result = load_pdx_sources(tmp_path, {"def": ("def.pdx",)}, module_id="focus/GER_sample")

    assert result.sources == ()
    assert result.diagnostics[0].code == "pdx.empty_variable"
    assert result.diagnostics[0].message == "PDX variable '@' requires a name."
    assert result.diagnostics[0].module_id == "focus/GER_sample"
    assert result.diagnostics[0].slot == "def"
    assert result.diagnostics[0].source_path == "def.pdx"
    assert result.diagnostics[0].span == {"line": 1, "column": 9}


def test_pdx_loader_reports_invalid_hex_number_diagnostics(tmp_path: Path) -> None:
    (tmp_path / "def.pdx").write_text("value = 0x", encoding="utf-8")

    result = load_pdx_sources(tmp_path, {"def": ("def.pdx",)}, module_id="focus/GER_sample")

    assert result.sources == ()
    assert result.diagnostics[0].code == "pdx.invalid_hex_number"
    assert result.diagnostics[0].message == "PDX hexadecimal number requires at least one digit."
    assert result.diagnostics[0].module_id == "focus/GER_sample"
    assert result.diagnostics[0].slot == "def"
    assert result.diagnostics[0].source_path == "def.pdx"
    assert result.diagnostics[0].span == {"line": 1, "column": 9}


def test_pdx_loader_keeps_the_core_ast_without_json_round_trips(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "def.pdx").write_text("focus = { id = GER_sample }", encoding="utf-8")

    def fail_json_round_trip(*_args: object, **_kwargs: object) -> object:
        raise AssertionError("build source loading must not project, dump, or reload a parsed PDX AST")

    monkeypatch.setattr(PDXBlock, "to_dict", fail_json_round_trip)
    monkeypatch.setattr(PDXBlock, "dump", fail_json_round_trip)
    monkeypatch.setattr(PDXBlock, "load", classmethod(fail_json_round_trip))

    result = load_pdx_sources(tmp_path, {"def": ("def.pdx",)}, module_id="focus/GER_sample")

    assert result.diagnostics == ()
    assert [(source.slot, source.path, source.block.to_str()) for source in result.sources] == [("def", "def.pdx", "focus = {\n\tid = GER_sample\n}\n")]


def test_pdx_loader_uses_the_logical_source_suffix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "def.txt"
    source.write_text("ignored by fake parser", encoding="utf-8")
    block = PDXBlock.from_str("focus = { id = GER_sample }")
    block.file_ext = ".pdx"

    monkeypatch.setattr(PDXBlock, "from_file", classmethod(lambda cls, path: block))

    result = load_pdx_sources(tmp_path, {"def": ("def.txt",)})

    assert result.diagnostics == ()
    assert result.sources[0].block.file_ext == ".txt"


def test_copy_loader_detects_image_metadata(tmp_path: Path) -> None:
    png = _png_header(width=64, height=48)
    dds = _dds_header(width=32, height=24)
    tga = _tga_header(width=16, height=8)
    (tmp_path / "icon.png").write_bytes(png)
    (tmp_path / "portrait.dds").write_bytes(dds)
    (tmp_path / "picture.tga").write_bytes(tga)

    result = load_copy_sources(
        tmp_path,
        {
            "icon": ("icon.png",),
            "portrait": ("portrait.dds",),
            "picture": ("picture.tga",),
        },
        module_id="idea/GER_sample",
    )

    assert result.diagnostics == ()
    assert [source.to_dict() for source in result.sources] == [
        {
            "slot": "icon",
            "path": "icon.png",
            "output_path": "icon.png",
            "sha256": sha256hash(png),
            "content_sha256": hashlib.sha256(png).hexdigest(),
            "size": len(png),
            "media_type": "image/png",
            "format": "png",
            "width": 64,
            "height": 48,
        },
        {
            "slot": "picture",
            "path": "picture.tga",
            "output_path": "picture.tga",
            "sha256": sha256hash(tga),
            "content_sha256": hashlib.sha256(tga).hexdigest(),
            "size": len(tga),
            "media_type": "image/x-tga",
            "format": "tga",
            "width": 16,
            "height": 8,
        },
        {
            "slot": "portrait",
            "path": "portrait.dds",
            "output_path": "portrait.dds",
            "sha256": sha256hash(dds),
            "content_sha256": hashlib.sha256(dds).hexdigest(),
            "size": len(dds),
            "media_type": "image/vnd-ms-dds",
            "format": "dds",
            "width": 32,
            "height": 24,
        },
    ]


def test_copy_loader_reports_unreadable_source_as_diagnostic(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "icon.png").write_bytes(b"sample image bytes")

    def fail_read_bytes(self: Path) -> bytes:
        if self.name == "icon.png":
            raise OSError("permission denied")
        return original_read_bytes(self)

    original_read_bytes = Path.read_bytes
    monkeypatch.setattr(Path, "read_bytes", fail_read_bytes)

    result = load_copy_sources(tmp_path, {"icon": ("icon.png",)}, module_id="idea/GER_sample")

    assert result.sources == ()
    assert result.diagnostics == (
        Diagnostic(
            code="copy.unreadable_source",
            message="Static copy source icon.png cannot be read. permission denied.",
            module_id="idea/GER_sample",
            slot="icon",
            source_path="icon.png",
        ),
    )


def _png_header(*, width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + pack(">I4sIIBBBBBI", 13, b"IHDR", width, height, 8, 6, 0, 0, 0, 0)


def _dds_header(*, width: int, height: int) -> bytes:
    header = bytearray(128)
    header[:4] = b"DDS "
    header[4:8] = pack("<I", 124)
    header[12:16] = pack("<I", height)
    header[16:20] = pack("<I", width)
    return bytes(header)


def _tga_header(*, width: int, height: int) -> bytes:
    header = bytearray(18)
    header[2] = 2
    header[12:14] = pack("<H", width)
    header[14:16] = pack("<H", height)
    return bytes(header)
