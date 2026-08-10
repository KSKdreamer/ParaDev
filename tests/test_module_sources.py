from __future__ import annotations

import hashlib
from pathlib import Path

from heavenbase.utils import sha256hash

from paradev.build import (
    CollectionSourceBundle,
    CopySource,
    LocalizationEntry,
    Slot,
    load_collection_sources,
    load_module_sources,
    match_slots,
)


def test_load_module_sources_combines_metadata_slots_and_loader_records(tmp_path: Path) -> None:
    root = tmp_path / "GER_sample"
    (root / "copy").mkdir(parents=True)
    (root / "meta.yaml").write_text(
        "\n".join(
            [
                "type: focus",
                "title: Sample Focus",
                "collection: GER_main",
            ]
        ),
        encoding="utf-8",
    )
    (root / "def.pdx").write_text("focus = { id = GER_sample }", encoding="utf-8")
    (root / "main.loc").write_text("l_english:\n  GER_sample: Sample Focus\n", encoding="utf-8")
    payload = b"sample image bytes"
    (root / "copy/icon.png").write_bytes(payload)

    matched = match_slots(
        root,
        (
            Slot("def", "def.pdx", required=True),
            Slot("loc", "*.loc", many=True),
            Slot("copy", "copy/*", many=True),
        ),
        module_id="focus/GER_sample",
    )
    bundle = load_module_sources(root, matched.source_slots, module_id="focus/GER_sample", inferred_type="focus")

    assert matched.diagnostics == ()
    assert bundle.diagnostics == ()
    assert bundle.metadata["object_id"] == "GER_sample"
    assert bundle.metadata["title"] == "Sample Focus"
    assert bundle.pdx_sources[0].path == "def.pdx"
    assert bundle.loc_entries == (
        LocalizationEntry(key="GER_sample", language="l_english", text="Sample Focus", source_path="main.loc", module_id="focus/GER_sample"),
    )
    assert bundle.copy_sources == (
        CopySource(
            slot="copy",
            path="copy/icon.png",
            output_path="copy/icon.png",
            sha256=sha256hash(payload),
            size=18,
            content_sha256=hashlib.sha256(payload).hexdigest(),
        ),
    )
    module = bundle.to_module()
    assert module.module_id == "focus/GER_sample"
    assert module.family == "focus"
    assert module.collection_id == "GER_main"
    assert module.source_slots == matched.source_slots
    assert module.metadata["object_id"] == "GER_sample"


def test_load_module_sources_uses_slot_loader_roles(tmp_path: Path) -> None:
    root = tmp_path / "GER_news"
    (root / "media").mkdir(parents=True)
    (root / "body.txt").write_text("country_event = { id = germany.1 }", encoding="utf-8")
    (root / "strings.yml").write_text("l_english:\n  germany.1.t: News\n", encoding="utf-8")
    payload = b"event picture"
    (root / "media/news.png").write_bytes(payload)
    slots = (
        Slot("body", "body.txt", required=True, kind="pdx"),
        Slot("strings", "strings.yml", kind="loc"),
        Slot("media", "media/*", many=True, kind="copy"),
    )

    matched = match_slots(root, slots, module_id="event/GER_news")
    bundle = load_module_sources(root, matched.source_slots, module_id="event/GER_news", inferred_type="event", slots=slots)

    assert matched.diagnostics == ()
    assert bundle.diagnostics == ()
    assert bundle.pdx_sources[0].slot == "body"
    assert bundle.pdx_sources[0].path == "body.txt"
    assert bundle.loc_entries == (
        LocalizationEntry(key="germany.1.t", language="l_english", text="News", source_path="strings.yml", module_id="event/GER_news"),
    )
    assert bundle.copy_sources == (
        CopySource(
            slot="media",
            path="media/news.png",
            output_path="media/news.png",
            sha256=sha256hash(payload),
            size=13,
            content_sha256=hashlib.sha256(payload).hexdigest(),
        ),
    )


def test_load_collection_sources_uses_slot_loader_roles(tmp_path: Path) -> None:
    root = tmp_path / "germany"
    root.mkdir()
    (root / "category.txt").write_text("add_namespace = germany", encoding="utf-8")
    (root / "strings.yml").write_text("en:\n  germany: Germany Events\n", encoding="utf-8")
    slots = (
        Slot("category", "category.txt", kind="pdx"),
        Slot("strings", "strings.yml", kind="loc"),
    )

    matched = match_slots(root, slots)
    result = load_collection_sources(root, family="event", collection_id="germany", source_slots=matched.source_slots, slots=slots)

    assert matched.diagnostics == ()
    assert result.diagnostics == ()
    assert isinstance(result.collection.payload, CollectionSourceBundle)
    assert result.collection.payload.source_slots == {"category": ("category.txt",), "strings": ("strings.yml",)}
    assert [(source.slot, source.path) for source in result.collection.payload.pdx_sources] == [("category", "category.txt")]
    assert result.collection.payload.loc_entries == (LocalizationEntry(key="germany", language="l_english", text="Germany Events", source_path="strings.yml"),)


def test_load_collection_sources_uses_copy_slot_loader_role(tmp_path: Path) -> None:
    root = tmp_path / "germany"
    (root / "media").mkdir(parents=True)
    payload = b"collection image"
    (root / "media/banner.png").write_bytes(payload)
    slots = (Slot("media", "media/*", many=True, kind="copy"),)

    matched = match_slots(root, slots)
    result = load_collection_sources(root, family="event", collection_id="germany", source_slots=matched.source_slots, slots=slots)

    assert matched.diagnostics == ()
    assert result.diagnostics == ()
    assert isinstance(result.collection.payload, CollectionSourceBundle)
    assert result.collection.payload.copy_sources == (
        CopySource(
            slot="media",
            path="media/banner.png",
            output_path="media/banner.png",
            sha256=sha256hash(payload),
            size=16,
            content_sha256=hashlib.sha256(payload).hexdigest(),
        ),
    )
