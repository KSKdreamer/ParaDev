from __future__ import annotations

import gzip
import json
import logging
import os
from pathlib import Path
import sys
import threading

import pytest

from paradev.build import discover_modules, source_cache
from paradev.pdx import PDXBlock
from paradev.sdk import Project


def _source_cache_file(root: Path) -> Path:
    cache_files = tuple((root / ".paradev/cache/source-families").rglob("*.json.gz"))
    assert len(cache_files) == 1
    return cache_files[0]


def _read_cache_document(path: Path) -> dict[str, object]:
    document = json.loads(gzip.decompress(path.read_bytes()))
    assert isinstance(document, dict)
    return document


def _write_cache_document(path: Path, document: dict[str, object]) -> None:
    path.write_bytes(
        gzip.compress(
            json.dumps(
                document,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8"),
            compresslevel=1,
            mtime=0,
        )
    )


def _write_project(root: Path, *, with_collection: bool = False) -> Project:
    _write_focus_module(root, "TEST_FOCUS", x=1)
    if with_collection:
        collection_root = root / "src/collections/focus/TEST_TREE"
        collection_root.mkdir(parents=True)
        (collection_root / "def.txt").write_text(
            "focus_tree = { id = TEST_TREE }\n",
            encoding="utf-8",
        )
    (root / "paradev.yaml").write_text(
        "\n".join(
            (
                "project_id: source_cache",
                "title: Source Cache",
                "game: hoi4",
                "source_roots: [src]",
                "output_root: build/mod",
                "build_root: .paradev/.cache/build",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return Project.load(root)


def _write_focus_module(root: Path, module_id: str, *, x: int) -> Path:
    module_root = root / f"src/modules/focus/{module_id}"
    module_root.mkdir(parents=True)
    (module_root / "def.txt").write_text(
        f"focus = {{ id = {module_id} x = {x} }}\n",
        encoding="utf-8",
    )
    return module_root


def test_project_source_cache_restores_parsed_module_without_reparsing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)

    cold = project.discover_modules()
    original_fingerprint = source_cache._family_fingerprint
    fingerprint_count = 0

    def count_fingerprint(*args: object, **kwargs: object) -> object:
        nonlocal fingerprint_count
        fingerprint_count += 1
        return original_fingerprint(*args, **kwargs)

    def reject_hash(path: Path, **_kwargs: object) -> str:
        raise AssertionError(f"cache hit read source bytes from {path}")

    def reject_parse(_cls: type[PDXBlock], path: str | Path) -> PDXBlock:
        raise AssertionError(f"cache hit reparsed {path}")

    monkeypatch.setattr(source_cache, "_family_fingerprint", count_fingerprint)
    monkeypatch.setattr(source_cache, "_hash_source_file", reject_hash)
    monkeypatch.setattr(PDXBlock, "from_file", classmethod(reject_parse))
    warm = Project.load(tmp_path).discover_modules()

    assert cold.cache_misses == 1
    assert warm.cache_hits == 1
    assert warm.cached_records == 1
    assert fingerprint_count == 1
    assert warm.modules[0].payload.pdx_sources[0].block.dump() == (cold.modules[0].payload.pdx_sources[0].block.dump())


def test_source_cache_checks_independent_families_in_parallel(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    idea_root = project.root / "src/modules/idea/TEST_IDEA"
    idea_root.mkdir(parents=True)
    (idea_root / "def.txt").write_text(
        "ideas = { TEST_IDEA = { } }\n",
        encoding="utf-8",
    )
    barrier = threading.Barrier(2)
    threads: set[int] = set()
    original_fingerprint = source_cache._family_fingerprint

    def synchronized_fingerprint(
        family_root: Path,
        *,
        previous: object = (),
    ) -> object:
        threads.add(threading.get_ident())
        barrier.wait(timeout=2)
        return original_fingerprint(
            family_root,
            previous=previous,
        )

    monkeypatch.setattr(source_cache, "_family_fingerprint", synchronized_fingerprint)

    result = discover_modules(
        project.source_roots,
        _cache_root=project.root / ".paradev/cache/source-families",
        _parallelism=2,
    )

    assert [module.module_id for module in result.modules] == [
        "focus/TEST_FOCUS",
        "idea/TEST_IDEA",
    ]
    assert result.cache_misses == 2
    assert len(threads) == 2


def test_project_source_cache_refreshes_changed_source_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    project.discover_modules()
    source = tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"
    source.write_text(
        "focus = { id = TEST_FOCUS x = 2 }\n",
        encoding="utf-8",
    )
    original = PDXBlock.from_file.__func__
    parsed: list[Path] = []

    def record_parse(cls: type[PDXBlock], path: str | Path) -> PDXBlock:
        parsed.append(Path(path))
        return original(cls, path)

    monkeypatch.setattr(PDXBlock, "from_file", classmethod(record_parse))
    refreshed = Project.load(tmp_path).discover_modules()

    assert refreshed.cache_refreshes == 1
    assert parsed == [source]
    assert "x = 2" in refreshed.modules[0].payload.pdx_sources[0].block.to_str()


def test_project_source_cache_rehashes_same_size_edit_with_restored_mtime(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    project.discover_modules()
    source = tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"
    before = source.stat()
    replacement = "focus = { id = TEST_FOCUS x = 2 }\n"
    assert len(replacement.encode("utf-8")) == before.st_size
    source.write_text(replacement, encoding="utf-8")
    os.utime(
        source,
        ns=(before.st_atime_ns, before.st_mtime_ns),
    )
    original = PDXBlock.from_file.__func__
    parsed: list[Path] = []

    def record_parse(cls: type[PDXBlock], path: str | Path) -> PDXBlock:
        parsed.append(Path(path))
        return original(cls, path)

    monkeypatch.setattr(PDXBlock, "from_file", classmethod(record_parse))
    refreshed = Project.load(tmp_path).discover_modules()

    assert refreshed.cache_refreshes == 1
    assert parsed == [source]
    assert "x = 2" in refreshed.modules[0].payload.pdx_sources[0].block.to_str()


@pytest.mark.parametrize("operation", ("add", "delete", "rename"))
def test_project_source_cache_invalidates_changed_file_inventory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    project = _write_project(tmp_path)
    module_root = tmp_path / "src/modules/focus/TEST_FOCUS"
    extra = module_root / "notes.txt"
    if operation != "add":
        extra.write_text("source inventory\n", encoding="utf-8")
    project.discover_modules()
    if operation == "add":
        extra.write_text("source inventory\n", encoding="utf-8")
    elif operation == "delete":
        extra.unlink()
    else:
        extra.rename(module_root / "renamed.txt")
    original = PDXBlock.from_file.__func__
    parsed: list[Path] = []

    def record_parse(cls: type[PDXBlock], path: str | Path) -> PDXBlock:
        parsed.append(Path(path))
        return original(cls, path)

    monkeypatch.setattr(PDXBlock, "from_file", classmethod(record_parse))
    refreshed = Project.load(tmp_path).discover_modules()

    assert refreshed.cache_refreshes == 1
    assert parsed == [module_root / "def.txt"]


@pytest.mark.parametrize("operation", ("add", "delete", "rename"))
def test_project_source_cache_retries_concurrent_file_topology_change(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    project = _write_project(tmp_path)
    family_root = tmp_path / "src/modules/focus"
    second = family_root / "SECOND_FOCUS"
    if operation != "add":
        _write_focus_module(tmp_path, "SECOND_FOCUS", x=2)
    project.discover_modules()
    original_validate = source_cache._validate_family_snapshot
    validation_count = 0

    def mutate_then_validate(*args: object, **kwargs: object) -> None:
        nonlocal validation_count
        validation_count += 1
        if validation_count == 1:
            if operation == "add":
                _write_focus_module(tmp_path, "SECOND_FOCUS", x=2)
            elif operation == "delete":
                (second / "def.txt").unlink()
                second.rmdir()
            else:
                second.rename(family_root / "RENAMED_FOCUS")
        original_validate(*args, **kwargs)

    monkeypatch.setattr(
        source_cache,
        "_validate_family_snapshot",
        mutate_then_validate,
    )
    refreshed = Project.load(tmp_path).discover_modules()

    expected = {
        "add": ["focus/SECOND_FOCUS", "focus/TEST_FOCUS"],
        "delete": ["focus/TEST_FOCUS"],
        "rename": ["focus/RENAMED_FOCUS", "focus/TEST_FOCUS"],
    }
    assert refreshed.cache_refreshes == 1
    assert [module.module_id for module in refreshed.modules] == expected[operation]
    assert validation_count == 3


@pytest.mark.parametrize("operation", ("add", "delete", "rename"))
def test_source_cache_fingerprint_includes_empty_directory_topology(
    tmp_path: Path,
    operation: str,
) -> None:
    family_root = tmp_path / "family"
    family_root.mkdir()
    empty = family_root / "EMPTY_UNIT"
    if operation != "add":
        empty.mkdir()
    before = source_cache._family_fingerprint(family_root)

    if operation == "add":
        empty.mkdir()
    elif operation == "delete":
        empty.rmdir()
    else:
        empty.rename(family_root / "RENAMED_UNIT")
    after = source_cache._family_fingerprint(family_root)

    assert after.digest != before.digest


@pytest.mark.parametrize("operation", ("add", "delete", "rename"))
def test_source_cache_fingerprint_retries_concurrent_directory_change(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
) -> None:
    family_root = tmp_path / "family"
    family_root.mkdir()
    empty = family_root / "EMPTY_UNIT"
    if operation != "add":
        empty.mkdir()
    original_validate = source_cache._validate_family_snapshot
    validation_count = 0

    def mutate_then_validate(*args: object, **kwargs: object) -> None:
        nonlocal validation_count
        validation_count += 1
        if validation_count == 1:
            if operation == "add":
                empty.mkdir()
            elif operation == "delete":
                empty.rmdir()
            else:
                empty.rename(family_root / "RENAMED_UNIT")
        original_validate(*args, **kwargs)

    monkeypatch.setattr(
        source_cache,
        "_validate_family_snapshot",
        mutate_then_validate,
    )
    fingerprint = source_cache._family_fingerprint(family_root)

    assert validation_count == 2
    assert fingerprint.digest == source_cache._family_fingerprint(family_root).digest


def test_source_cache_fingerprint_brackets_directory_listing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    family_root = tmp_path / "family"
    family_root.mkdir()
    (family_root / "first.txt").write_text("first\n", encoding="utf-8")
    late = family_root / "late.txt"
    original_token = source_cache._source_directory_token
    root_token_count = 0

    def add_after_listing(
        path: Path,
        *,
        root_device: int,
    ) -> object:
        nonlocal root_token_count
        if path == family_root:
            root_token_count += 1
            if root_token_count == 2:
                late.write_text("late\n", encoding="utf-8")
        return original_token(path, root_device=root_device)

    monkeypatch.setattr(
        source_cache,
        "_source_directory_token",
        add_after_listing,
    )
    fingerprint = source_cache._family_fingerprint(family_root)

    assert root_token_count == 5
    assert [entry.relative_path for entry in fingerprint.entries] == [
        "first.txt",
        "late.txt",
    ]


def test_source_cache_fingerprint_rejects_repeated_topology_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    family_root = tmp_path / "family"
    family_root.mkdir()
    transient = family_root / "transient.txt"
    original_validate = source_cache._validate_family_snapshot
    validation_count = 0

    def mutate_then_validate(*args: object, **kwargs: object) -> None:
        nonlocal validation_count
        validation_count += 1
        if transient.exists():
            transient.unlink()
        else:
            transient.write_text("drift\n", encoding="utf-8")
        original_validate(*args, **kwargs)

    monkeypatch.setattr(
        source_cache,
        "_validate_family_snapshot",
        mutate_then_validate,
    )

    with pytest.raises(RuntimeError, match="fingerprint validation"):
        source_cache._family_fingerprint(family_root)

    assert validation_count == 2


def test_project_source_cache_bypasses_retargeted_file_symlink(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path)
    source = tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"
    targets = tmp_path / "targets"
    targets.mkdir()
    first = targets / "first.txt"
    second = targets / "second.txt"
    first.write_text("focus = { id = TEST_FOCUS x = 1 }\n", encoding="utf-8")
    second.write_text("focus = { id = TEST_FOCUS x = 2 }\n", encoding="utf-8")
    source.unlink()
    try:
        source.symlink_to(first)
    except OSError as error:
        pytest.skip(f"filesystem does not permit symlink creation: {error}")
    cold = project.discover_modules()
    source.unlink()
    source.symlink_to(second)

    repeated = Project.load(tmp_path).discover_modules()

    assert cold.cache_signature is None
    assert repeated.cache_signature is None
    assert repeated.cache_hits == repeated.cache_misses == repeated.cache_refreshes == 0
    assert "x = 2" in repeated.modules[0].payload.pdx_sources[0].block.to_str()
    assert tuple((tmp_path / ".paradev/cache/source-families").rglob("*.json.gz")) == ()


def test_project_source_cache_bypasses_directory_symlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    family_root = tmp_path / "src/modules/focus"
    external = tmp_path / "external/SECOND_FOCUS"
    external.mkdir(parents=True)
    external_source = external / "def.txt"
    external_source.write_text(
        "focus = { id = SECOND_FOCUS x = 2 }\n",
        encoding="utf-8",
    )
    linked = family_root / "SECOND_FOCUS"
    try:
        linked.symlink_to(external, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"filesystem does not permit symlink creation: {error}")
    project.discover_modules()
    original = PDXBlock.from_file.__func__
    parsed: list[Path] = []

    def record_parse(cls: type[PDXBlock], path: str | Path) -> PDXBlock:
        parsed.append(Path(path))
        return original(cls, path)

    monkeypatch.setattr(PDXBlock, "from_file", classmethod(record_parse))
    repeated = Project.load(tmp_path).discover_modules()

    assert repeated.cache_signature is None
    assert repeated.cache_hits == repeated.cache_misses == repeated.cache_refreshes == 0
    assert sorted(module.module_id for module in repeated.modules) == [
        "focus/SECOND_FOCUS",
        "focus/TEST_FOCUS",
    ]
    assert parsed == [linked / "def.txt", family_root / "TEST_FOCUS/def.txt"]


def test_source_cache_filesystem_classification_is_cached_by_device(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []

    def probe(device: int) -> str:
        calls.append(device)
        return "apfs"

    source_cache._filesystem_kind_for_device.cache_clear()
    monkeypatch.setattr(source_cache, "_probe_filesystem_kind", probe)
    try:
        assert source_cache._trusted_local_filesystem(
            tmp_path / "first/family",
            device=101,
        )
        assert source_cache._trusted_local_filesystem(
            tmp_path / "second/family",
            device=101,
        )
        assert calls == [101]
    finally:
        source_cache._filesystem_kind_for_device.cache_clear()


def test_source_cache_trusts_linux_ext_filesystem_names() -> None:
    assert {"ext2", "ext3", "ext4"} <= source_cache._TRUSTED_LOCAL_FILESYSTEMS


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS APFS probe")
def test_source_cache_trusts_actual_macos_pihc3_filesystem() -> None:
    project_root = Path("projects/PIHC3").resolve()

    assert source_cache._trusted_local_filesystem(
        project_root,
        device=project_root.stat().st_dev,
    )


def test_project_source_cache_full_hashes_when_metadata_is_untrusted(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    project.discover_modules()
    source = tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"
    original_hash = source_cache._hash_source_file
    hashed: list[Path] = []

    def record_hash(path: Path, **kwargs: object) -> str:
        hashed.append(path)
        return original_hash(path, **kwargs)

    monkeypatch.setattr(
        source_cache,
        "_trusted_local_filesystem",
        lambda *_args, **_kwargs: False,
    )
    monkeypatch.setattr(source_cache, "_hash_source_file", record_hash)
    warm = Project.load(tmp_path).discover_modules()

    assert warm.cache_hits == 1
    assert hashed == [source]


def test_project_source_cache_validates_source_after_payload_decode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    project.discover_modules()
    source = tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"
    original_decode = source_cache._decode_module_result

    def decode_then_edit(payload: object) -> object:
        result = original_decode(payload)
        source.write_text(
            "focus = { id = TEST_FOCUS x = 2 }\n",
            encoding="utf-8",
        )
        return result

    monkeypatch.setattr(source_cache, "_decode_module_result", decode_then_edit)
    refreshed = Project.load(tmp_path).discover_modules()

    assert refreshed.cache_refreshes == 1
    assert refreshed.cache_hits == 0
    assert "x = 2" in refreshed.modules[0].payload.pdx_sources[0].block.to_str()


def test_source_cache_hash_retries_transient_path_identity_race(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    family_root = tmp_path / "family"
    family_root.mkdir()
    source = family_root / "source.txt"
    alternate = tmp_path / "alternate.txt"
    source.write_text("stable A\n", encoding="utf-8")
    alternate.write_text("transient B\n", encoding="utf-8")
    original_open = source_cache.os.open
    open_count = 0

    def race_once(path: str | bytes | os.PathLike[str], flags: int) -> int:
        nonlocal open_count
        open_count += 1
        return original_open(alternate if open_count == 1 else path, flags)

    monkeypatch.setattr(source_cache.os, "open", race_once)
    fingerprint = source_cache._family_fingerprint(family_root)

    assert open_count == 2
    assert fingerprint.digest == source_cache._family_fingerprint(family_root).digest


def test_source_cache_hash_rejects_repeated_path_identity_race(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    family_root = tmp_path / "family"
    family_root.mkdir()
    source = family_root / "source.txt"
    alternate = tmp_path / "alternate.txt"
    source.write_text("stable A\n", encoding="utf-8")
    alternate.write_text("transient B\n", encoding="utf-8")
    original_open = source_cache.os.open

    def race_every_time(_path: str | bytes | os.PathLike[str], flags: int) -> int:
        return original_open(alternate, flags)

    monkeypatch.setattr(source_cache.os, "open", race_every_time)

    with pytest.raises(RuntimeError, match="fingerprint validation"):
        source_cache._family_fingerprint(family_root)


def test_source_cache_rejects_coarse_or_unavailable_metadata_tokens() -> None:
    coarse = source_cache._SourceFileToken(
        size=1,
        mtime_ns=1_700_000_000_000_000_000,
        ctime_ns=1_700_000_001_000_000_000,
        device=1,
        inode=1,
    )
    unavailable = source_cache._SourceFileToken(
        size=1,
        mtime_ns=1_700_000_000_000_000_001,
        ctime_ns=1_700_000_001_000_000_001,
        device=0,
        inode=0,
    )

    assert (
        source_cache._source_metadata_is_reliable(
            coarse,
            observed_before_ns=1_800_000_000_000_000_000,
        )
        is False
    )
    assert (
        source_cache._source_metadata_is_reliable(
            unavailable,
            observed_before_ns=1_800_000_000_000_000_000,
        )
        is False
    )


def test_source_cache_accepts_precise_ctime_with_preserved_coarse_mtime() -> None:
    preserved_source = source_cache._SourceFileToken(
        size=1,
        mtime_ns=1_700_000_000_000_000_000,
        ctime_ns=1_700_000_001_000_000_123,
        device=1,
        inode=1,
    )

    assert source_cache._source_metadata_is_reliable(
        preserved_source,
        observed_before_ns=1_800_000_000_000_000_000,
    )


def test_source_cache_rejects_coarse_ctime_despite_precise_mtime() -> None:
    unsafe_source = source_cache._SourceFileToken(
        size=1,
        mtime_ns=1_700_000_000_000_000_123,
        ctime_ns=1_700_000_001_000_000_000,
        device=1,
        inode=1,
    )

    assert (
        source_cache._source_metadata_is_reliable(
            unsafe_source,
            observed_before_ns=1_800_000_000_000_000_000,
        )
        is False
    )


def test_project_source_cache_signature_is_stable_and_content_addressed(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path, with_collection=True)

    cold_modules = project.discover_modules()
    cold_collections = project.discover_collections()
    warm_modules = Project.load(tmp_path).discover_modules()
    warm_collections = Project.load(tmp_path).discover_collections()

    assert cold_modules.cache_signature == warm_modules.cache_signature
    assert cold_collections.cache_signature == warm_collections.cache_signature
    assert len(cold_modules.cache_signature or "") == 64
    assert len(cold_collections.cache_signature or "") == 64

    source = tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"
    source.write_text(
        "focus = { id = TEST_FOCUS x = 2 }\n",
        encoding="utf-8",
    )
    changed = Project.load(tmp_path).discover_modules()

    assert changed.cache_signature != warm_modules.cache_signature


def test_project_source_cache_refreshes_changed_loader_dependency(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dependency = tmp_path / "editable_dependency.py"
    dependency.write_text("VERSION = 1\n", encoding="utf-8")
    monkeypatch.setattr(source_cache, "_CACHE_CODE_PATHS", ())
    monkeypatch.setattr(
        source_cache,
        "getsourcefile",
        lambda _item: str(dependency),
    )
    source_cache._cache_engine_fingerprint.cache_clear()
    try:
        project = _write_project(tmp_path)
        project.discover_modules()
        dependency.write_text("VERSION = 2\n", encoding="utf-8")
        source_cache._cache_engine_fingerprint.cache_clear()

        refreshed = Project.load(tmp_path).discover_modules()

        assert refreshed.cache_refreshes == 1
        assert refreshed.cache_hits == 0
    finally:
        source_cache._cache_engine_fingerprint.cache_clear()


def test_project_source_cache_recovers_from_corrupt_derived_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    project.discover_modules()
    cache_files = tuple((tmp_path / ".paradev/cache/source-families").rglob("*.json.gz"))
    assert len(cache_files) == 1
    cache_files[0].write_bytes(b"not a cache document")
    original = PDXBlock.from_file.__func__
    parsed: list[Path] = []

    def record_parse(cls: type[PDXBlock], path: str | Path) -> PDXBlock:
        parsed.append(Path(path))
        return original(cls, path)

    monkeypatch.setattr(PDXBlock, "from_file", classmethod(record_parse))
    recovered = Project.load(tmp_path).discover_modules()

    assert recovered.cache_refreshes == 1
    assert parsed == [tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"]
    assert recovered.diagnostics == ()


@pytest.mark.parametrize(
    "damage",
    ("checksum", "duplicate", "out_of_order", "oversized"),
)
def test_project_source_cache_refreshes_invalid_source_inventory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    damage: str,
) -> None:
    project = _write_project(tmp_path)
    module_root = tmp_path / "src/modules/focus/TEST_FOCUS"
    (module_root / "notes.txt").write_text("inventory row\n", encoding="utf-8")
    project.discover_modules()
    cache_file = _source_cache_file(tmp_path)
    document = _read_cache_document(cache_file)
    inventory = document["source_inventory"]
    assert isinstance(inventory, dict)
    entries = inventory["entries"]
    assert isinstance(entries, list)
    assert len(entries) == 2
    if damage == "checksum":
        inventory["checksum"] = "0" * 64
    elif damage == "duplicate":
        entries.append(dict(entries[-1]))
        inventory["checksum"] = source_cache._source_inventory_checksum(entries)
    elif damage == "out_of_order":
        entries.reverse()
        inventory["checksum"] = source_cache._source_inventory_checksum(entries)
    else:
        monkeypatch.setattr(source_cache, "_MAX_SOURCE_INVENTORY_ROWS", 2)
        extra = dict(entries[-1])
        extra["path"] = "zz-extra.txt"
        entries.append(extra)
        inventory["checksum"] = source_cache._source_inventory_checksum(entries)
    _write_cache_document(cache_file, document)
    original = PDXBlock.from_file.__func__
    parsed: list[Path] = []

    def record_parse(cls: type[PDXBlock], path: str | Path) -> PDXBlock:
        parsed.append(Path(path))
        return original(cls, path)

    monkeypatch.setattr(PDXBlock, "from_file", classmethod(record_parse))
    refreshed = Project.load(tmp_path).discover_modules()
    refreshed_document = _read_cache_document(cache_file)

    assert refreshed.cache_refreshes == 1
    assert refreshed.cache_hits == 0
    assert parsed == [module_root / "def.txt"]
    assert len(source_cache._decode_source_inventory(refreshed_document["source_inventory"])) == 2
    assert tuple(cache_file.parent.glob(f".{cache_file.name}.*.tmp")) == ()


def test_project_source_cache_reparses_valid_json_with_malformed_pdx_entries(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    project = _write_project(tmp_path)
    project.discover_modules()
    cache_files = tuple((tmp_path / ".paradev/cache/source-families").rglob("*.json.gz"))
    assert len(cache_files) == 1
    document = json.loads(gzip.decompress(cache_files[0].read_bytes()))
    document["payload"]["modules"][0]["payload"]["pdx_sources"][0]["block"]["entries"] = [None]
    cache_files[0].write_bytes(
        gzip.compress(
            json.dumps(document, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
            compresslevel=1,
            mtime=0,
        )
    )
    original = PDXBlock.from_file.__func__
    parsed: list[Path] = []

    def record_parse(cls: type[PDXBlock], path: str | Path) -> PDXBlock:
        parsed.append(Path(path))
        return original(cls, path)

    monkeypatch.setattr(PDXBlock, "from_file", classmethod(record_parse))
    with caplog.at_level(logging.WARNING, logger=source_cache.__name__):
        recovered = Project.load(tmp_path).discover_modules()

    assert recovered.cache_refreshes == 1
    assert recovered.cache_hits == 0
    assert parsed == [tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"]
    assert "Ignoring invalid parsed source cache" in caplog.text
    assert "AttributeError" in caplog.text


def test_project_source_cache_write_failure_is_non_blocking_and_observable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    project = _write_project(tmp_path)

    def fail_write(_path: Path, _document: object) -> None:
        raise OSError("synthetic disk full")

    monkeypatch.setattr(source_cache, "_write_cache", fail_write)
    with caplog.at_level(logging.WARNING, logger=source_cache.__name__):
        result = project.discover_modules()

    assert len(result.modules) == 1
    assert result.cache_misses == 1
    assert "Could not write parsed source cache" in caplog.text
    assert "synthetic disk full" in caplog.text


def test_project_source_cache_retries_one_edit_during_discovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    source = tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"
    original = PDXBlock.from_file.__func__
    parse_count = 0

    def parse_then_edit(cls: type[PDXBlock], path: str | Path) -> PDXBlock:
        nonlocal parse_count
        block = original(cls, path)
        parse_count += 1
        if parse_count == 1:
            source.write_text(
                "focus = { id = TEST_FOCUS x = 2 }\n",
                encoding="utf-8",
            )
        return block

    monkeypatch.setattr(PDXBlock, "from_file", classmethod(parse_then_edit))
    discovered = project.discover_modules()

    assert parse_count == 2
    assert "x = 2" in discovered.modules[0].payload.pdx_sources[0].block.to_str()


def test_project_source_cache_retries_transient_aba_edit_during_discovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    source = tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"
    original_text = source.read_text(encoding="utf-8")
    transient_text = "focus = { id = TEST_FOCUS x = 2 }\n"
    original = PDXBlock.from_file.__func__
    parse_count = 0

    def parse_transient_then_restore(
        cls: type[PDXBlock],
        path: str | Path,
    ) -> PDXBlock:
        nonlocal parse_count
        parse_count += 1
        if parse_count != 1:
            return original(cls, path)
        restore = tmp_path / "restore.txt"
        restore.write_text(original_text, encoding="utf-8")
        source.write_text(transient_text, encoding="utf-8")
        try:
            return original(cls, path)
        finally:
            os.replace(restore, source)

    monkeypatch.setattr(
        PDXBlock,
        "from_file",
        classmethod(parse_transient_then_restore),
    )
    discovered = project.discover_modules()
    warm = Project.load(tmp_path).discover_modules()

    assert parse_count == 2
    assert source.read_text(encoding="utf-8") == original_text
    assert "x = 1" in discovered.modules[0].payload.pdx_sources[0].block.to_str()
    assert warm.cache_hits == 1
    assert "x = 1" in warm.modules[0].payload.pdx_sources[0].block.to_str()


def test_project_source_cache_rejects_repeated_aba_drift_during_discovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    source = tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"
    original_text = source.read_text(encoding="utf-8")
    transient_text = "focus = { id = TEST_FOCUS x = 2 }\n"
    original = PDXBlock.from_file.__func__
    parse_count = 0

    def parse_transient_then_restore(
        cls: type[PDXBlock],
        path: str | Path,
    ) -> PDXBlock:
        nonlocal parse_count
        parse_count += 1
        restore = tmp_path / f"restore-{parse_count}.txt"
        restore.write_text(original_text, encoding="utf-8")
        source.write_text(transient_text, encoding="utf-8")
        try:
            return original(cls, path)
        finally:
            os.replace(restore, source)

    monkeypatch.setattr(
        PDXBlock,
        "from_file",
        classmethod(parse_transient_then_restore),
    )

    with pytest.raises(RuntimeError, match="changed repeatedly during discovery"):
        project.discover_modules()

    assert parse_count == 2
    assert source.read_text(encoding="utf-8") == original_text
    assert tuple((tmp_path / ".paradev/cache/source-families").rglob("*.json.gz")) == ()


def test_project_source_cache_rejects_repeated_drift_during_discovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    source = tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"
    original = PDXBlock.from_file.__func__
    parse_count = 0

    def parse_then_edit(cls: type[PDXBlock], path: str | Path) -> PDXBlock:
        nonlocal parse_count
        block = original(cls, path)
        parse_count += 1
        source.write_text(
            f"focus = {{ id = TEST_FOCUS x = {parse_count + 1} }}\n",
            encoding="utf-8",
        )
        return block

    monkeypatch.setattr(PDXBlock, "from_file", classmethod(parse_then_edit))

    with pytest.raises(RuntimeError, match="changed repeatedly during discovery"):
        project.discover_modules()

    assert parse_count == 2


def test_project_full_build_bypasses_valid_source_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = _write_project(tmp_path)
    project.build()
    original = PDXBlock.from_file.__func__
    parsed: list[Path] = []

    def record_parse(cls: type[PDXBlock], path: str | Path) -> PDXBlock:
        parsed.append(Path(path))
        return original(cls, path)

    monkeypatch.setattr(PDXBlock, "from_file", classmethod(record_parse))
    events: list[dict[str, object]] = []
    result = Project.load(tmp_path).build(
        full_rebuild=True,
        progress=events.append,
    )

    assert result.blocked is False
    assert parsed == [tmp_path / "src/modules/focus/TEST_FOCUS/def.txt"]
    completed_discovery = [event for event in events if event["phase"] == "discover_modules" and "counts" in event][0]
    assert completed_discovery["counts"] == {"modules": 1}


def test_project_source_cache_restores_collection_source_bundles(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path, with_collection=True)

    cold = project.discover_collections()
    warm = Project.load(tmp_path).discover_collections()

    assert cold.cache_misses == 1
    assert warm.cache_hits == 1
    assert warm.cached_records == 1
    assert warm.collections[0].payload.pdx_sources[0].block.dump() == (cold.collections[0].payload.pdx_sources[0].block.dump())


def test_project_source_cache_signature_is_stable_for_module_target_filter(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path)
    second = tmp_path / "src/modules/focus/SECOND_FOCUS"
    second.mkdir()
    (second / "def.txt").write_text(
        "focus = { id = SECOND_FOCUS x = 2 }\n",
        encoding="utf-8",
    )
    cold = project.discover_modules()

    targeted = discover_modules(
        project.source_roots,
        module_id="focus/TEST_FOCUS",
        _cache_root=tmp_path / ".paradev/cache/source-families",
    )

    assert targeted.cache_hits == 1
    assert [module.module_id for module in targeted.modules] == ["focus/TEST_FOCUS"]
    assert targeted.cache_signature == cold.cache_signature


def test_cached_build_progress_reports_reused_source_records(
    tmp_path: Path,
) -> None:
    project = _write_project(tmp_path)
    project.build()
    events: list[dict[str, object]] = []

    result = Project.load(tmp_path).build(progress=events.append)

    assert result.blocked is False
    completed_discovery = [event for event in events if event["phase"] == "discover_modules" and "counts" in event][0]
    assert completed_discovery["counts"] == {
        "modules": 1,
        "cached_modules": 1,
        "source_cache_hits": 1,
        "source_cache_misses": 0,
        "source_cache_refreshes": 0,
    }
