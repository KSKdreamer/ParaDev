from __future__ import annotations

import sys
from pathlib import Path

import pytest
from heavenbase.utils import cmd, load_yaml

from paradev.build._extension_metadata import (
    hide_project_extension_metadata,
    migrate_extension_publication_metadata,
    plan_extension_publication_metadata,
    plan_hidden_extension_metadata,
)


def _write_extension(root: Path, name: str, descriptor: bytes) -> Path:
    extension = root / "extensions" / name
    extension.mkdir(parents=True)
    (extension / "__init__.py").write_text("", encoding="utf-8")
    (extension / "meta.yaml").write_bytes(descriptor)
    return extension


def test_hidden_extension_metadata_migration_is_exact_and_resumable(
    tmp_path: Path,
) -> None:
    first = _write_extension(tmp_path, "first", b"manifest_version: 2\n")
    second = _write_extension(tmp_path, "second", b"manifest_version: 2\r\n")
    duplicate = second / ".paradev/meta.yaml"
    duplicate.parent.mkdir()
    duplicate.write_bytes((second / "meta.yaml").read_bytes())

    plan = plan_hidden_extension_metadata(tmp_path)
    applied = hide_project_extension_metadata(tmp_path, write=True)

    assert applied == plan
    assert [move.action for move in plan] == ["move", "remove-duplicate"]
    assert not (first / "meta.yaml").exists()
    assert (first / ".paradev/meta.yaml").read_bytes() == (b"manifest_version: 2\n")
    assert not (second / "meta.yaml").exists()
    assert duplicate.read_bytes() == b"manifest_version: 2\r\n"
    assert hide_project_extension_metadata(tmp_path, write=True) == ()


def test_hidden_extension_metadata_migration_rejects_conflicting_duplicate(
    tmp_path: Path,
) -> None:
    extension = _write_extension(
        tmp_path,
        "sample",
        b"manifest_version: 2\n",
    )
    hidden = extension / ".paradev/meta.yaml"
    hidden.parent.mkdir()
    hidden.write_bytes(b"manifest_version: 1\n")

    with pytest.raises(ValueError, match="conflicting"):
        hide_project_extension_metadata(tmp_path, write=True)

    assert (extension / "meta.yaml").read_bytes() == b"manifest_version: 2\n"
    assert hidden.read_bytes() == b"manifest_version: 1\n"


def test_entity_materializer_removes_stale_path_definition_idempotently(
    tmp_path: Path,
) -> None:
    extension = _write_extension(
        tmp_path,
        "sample",
        b"""\
manifest_version: 2
items:
  - kind: entity
    identifier: sample
    source: path
    target: {module: null, qualname: SampleEntity}
    meta:
      schema_version: 1
      definition:
        entity_id: stale-inline-copy
        fields: {}
""",
    )
    script = Path(__file__).resolve().parents[1] / "scripts/materialize_project_extension_entities.py"

    cmd([sys.executable, script, tmp_path], check=True)
    descriptor_path = extension / "meta.yaml"
    descriptor = load_yaml(str(descriptor_path), strict=True)
    first_bytes = descriptor_path.read_bytes()

    assert descriptor["items"][0]["meta"] == {"schema_version": 1}

    cmd([sys.executable, script, tmp_path], check=True)

    assert descriptor_path.read_bytes() == first_bytes


def test_publication_metadata_migration_is_exact_and_idempotent(
    tmp_path: Path,
) -> None:
    descriptor = b"""\
manifest_version: 2
items:
  - kind: paradev_build_family
    identifier: sample
    meta:
      schema_version: 1
      definition:
        declaration:
          title: Sample
          retired_families: [sample_component, sample_asset_component]
"""
    extension = _write_extension(tmp_path, "sample", descriptor)
    (extension / "__init__.py").write_text(
        """\
def build_family():
    return object(
        retired_families=("sample_asset_component", "sample_component"),
    )
""",
        encoding="utf-8",
    )

    plan = plan_extension_publication_metadata(tmp_path)
    applied = migrate_extension_publication_metadata(tmp_path, write=True)
    migrated = load_yaml(str(extension / "meta.yaml"), strict=True)
    family_meta = migrated["items"][0]["meta"]

    assert applied == plan
    assert len(plan) == 1
    assert family_meta["publication"] == {
        "replaces_families": [
            "sample_asset_component",
            "sample_component",
        ]
    }
    assert "retired_families" not in family_meta["definition"]["declaration"]
    assert migrate_extension_publication_metadata(tmp_path, write=True) == ()


def test_publication_metadata_migration_rejects_conflicting_sources_without_write(
    tmp_path: Path,
) -> None:
    descriptor = b"""\
manifest_version: 2
items:
  - kind: paradev_build_family
    identifier: sample
    meta:
      schema_version: 1
      definition:
        declaration:
          retired_families: [sample_component]
"""
    extension = _write_extension(tmp_path, "sample", descriptor)
    (extension / "__init__.py").write_text(
        """\
def build_family():
    return object(retired_families=("different_component",))
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="conflicting publication"):
        migrate_extension_publication_metadata(tmp_path, write=True)

    assert (extension / "meta.yaml").read_bytes() == descriptor
