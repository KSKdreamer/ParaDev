from __future__ import annotations

import json
import logging
import sqlite3
import subprocess
import sys
import warnings
from pathlib import Path
from threading import Event, Thread
from types import SimpleNamespace

import heavenbase as hb
import paradev.hb as paradev_hb
import paradev.sdk.project as project_sdk
import pytest
from heavenbase.utils import copy_dir, delete_dir
from typer.testing import CliRunner

from paradev.cli import build_app
from paradev.config import _CONTEXT_PARADEV
from paradev.hb import catalog_preview, catalog_query, catalog_refresh, catalog_smoke, catalog_status, catalog_write
from paradev.hb.hoi4 import HOI4_EXTENSION_ID, register_hoi4_extension
from paradev.sdk import Project

PROJECT_ROOT = Path("demos/assets/projects/minimal").resolve()


def test_hb_hoi4_extension_registration_avoids_reserved_sqlite_field_names() -> None:
    workspace = hb.HeavenBase(
        "paradev-hoi4-extension-warning-contract",
        context=_CONTEXT_PARADEV,
        backends={"main": {"type": "sqlite"}},
        detached=True,
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        register_hoi4_extension()
        workspace.enable_extension(HOI4_EXTENSION_ID)

    reserved_name_warnings = [warning for warning in caught if "reserved provider name" in str(warning.message)]
    assert reserved_name_warnings == []


def test_hb_pdx_symbol_entity_uses_typed_preview_fields() -> None:
    workspace = hb.HeavenBase(
        "paradev-hoi4-pdx-symbol-schema-contract",
        context=_CONTEXT_PARADEV,
        backends={"main": {"type": "sqlite"}},
        detached=True,
    )

    register_hoi4_extension()
    workspace.enable_extension(HOI4_EXTENSION_ID)

    fields = workspace.entities["hoi4-pdx-symbol"].schema().fields
    assert set(fields) == {
        "object_id",
        "symbol_id",
        "document_id",
        "module_id",
        "collection_id",
        "family",
        "slot",
        "path",
        "symbol_key",
        "kind",
        "op",
        "value",
        "value_type",
        "source_line",
        "source_column",
    }
    assert fields["symbol_id"].required is True
    assert fields["module_id"].required is False
    assert fields["source_line"].required is False
    assert "data" not in fields
    assert "name" not in fields
    assert "description" not in fields
    assert "tags" not in fields


def test_hb_pdx_symbol_projection_rejects_unregistered_fields() -> None:
    with pytest.raises(ValueError, match="Unsupported pdx-symbol fields: future_field"):
        paradev_hb._catalog_row(
            "pdx-symbol",
            {
                "symbol_id": "focus/GER_contract:def:def.txt:0",
                "document_id": "focus/GER_contract:def:def.txt",
                "module_id": "focus/GER_contract",
                "family": "focus",
                "slot": "def",
                "path": "focus",
                "key": "focus",
                "kind": "block",
                "future_field": "must be registered before persistence",
            },
        )


def test_hb_hoi4_extension_registration_does_not_mutate_default_context() -> None:
    default_resolver = hb.DEFAULT_CONTEXT.modules()
    paradev_resolver = _CONTEXT_PARADEV.modules()
    default_before = hb.ext.Extension.identifiers(resolver=default_resolver)

    register_hoi4_extension()

    assert hb.ext.Extension.identifiers(resolver=default_resolver) == default_before
    assert HOI4_EXTENSION_ID in hb.ext.Extension.identifiers(resolver=paradev_resolver)


def test_hb_database_disposal_targets_paradev_context_authority(tmp_path: Path) -> None:
    database_path = tmp_path / "paradev-authority.sqlite"
    workspace = paradev_hb._detached_workspace(
        "paradev-database-authority",
        backends={"main": {"type": "sqlite", "database": database_path.resolve().as_uri()}},
    )
    database = workspace.backends.get("main").db

    assert database.disposed is False

    paradev_hb._dispose_database_engine(database_path)

    assert database.disposed is True


@pytest.mark.parametrize("backend_type", ["inmem", "sqlite"])
def test_hb_fresh_catalog_writer_matches_public_upsert_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    backend_type: str,
) -> None:
    def workspace(name: str) -> hb.HeavenBase:
        backend: dict[str, str] = {"type": backend_type}
        if backend_type == "sqlite":
            backend["database"] = (tmp_path / f"{name}.sqlite").resolve().as_uri()
        result = hb.HeavenBase(
            "paradev-fresh-writer-contract",
            context=_CONTEXT_PARADEV,
            backends={"main": backend},
            detached=True,
        )
        register_hoi4_extension()
        result.enable_extension(HOI4_EXTENSION_ID)
        monkeypatch.setattr(result._catalog, "now", lambda: 1_234_567_890)
        return result

    public_workspace = workspace("public")
    fresh_workspace = workspace("fresh")
    module_identifier = paradev_hb.normalize_entity_identifier("module")
    public_entity = public_workspace.entities[module_identifier]
    fresh_entity = fresh_workspace.entities[module_identifier]
    row = paradev_hb._catalog_row(
        "module",
        {
            "module_id": "focus/GER_contract",
            "family": "focus",
            "root": "src/modules/focus/GER_contract",
            "source_slots": {"def": ["def.txt"]},
            "metadata": {"object_id": "GER_contract"},
            "status": "loaded",
        },
    )

    public_workspace.upsert_many(public_entity, [dict(row)], overwrite=False)
    paradev_hb._write_fresh_catalog_chunk(fresh_workspace, fresh_entity, [dict(row)])

    assert fresh_workspace.query(fresh_entity).execute().rows() == public_workspace.query(public_entity).execute().rows()
    assert fresh_workspace.query(hb.Catalog).execute().rows() == public_workspace.query(hb.Catalog).execute().rows()


@pytest.mark.parametrize("backend_type", ["inmem", "sqlite"])
def test_hb_fresh_catalog_writer_matches_typed_pdx_symbol_upsert(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    backend_type: str,
) -> None:
    def workspace(name: str) -> hb.HeavenBase:
        backend: dict[str, str] = {"type": backend_type}
        if backend_type == "sqlite":
            backend["database"] = (tmp_path / f"{name}.sqlite").resolve().as_uri()
        result = hb.HeavenBase(
            "paradev-fresh-pdx-symbol-writer-contract",
            context=_CONTEXT_PARADEV,
            backends={"main": backend},
            detached=True,
        )
        register_hoi4_extension()
        result.enable_extension(HOI4_EXTENSION_ID)
        monkeypatch.setattr(result._catalog, "now", lambda: 1_234_567_890)
        return result

    public_workspace = workspace("public-symbol")
    fresh_workspace = workspace("fresh-symbol")
    public_entity = public_workspace.entities["hoi4-pdx-symbol"]
    fresh_entity = fresh_workspace.entities["hoi4-pdx-symbol"]
    row = paradev_hb._catalog_row(
        "pdx-symbol",
        {
            "symbol_id": "focus/GER_contract:def:def.txt:1",
            "document_id": "focus/GER_contract:def:def.txt",
            "module_id": "focus/GER_contract",
            "family": "focus",
            "slot": "def",
            "path": "focus/id",
            "key": "id",
            "op": "=",
            "kind": "scalar",
            "value": "GER_contract",
            "value_type": "id",
            "line": 2,
            "column": 2,
        },
    )

    public_workspace.upsert_many(public_entity, [dict(row)], overwrite=False)
    paradev_hb._write_fresh_catalog_chunk(fresh_workspace, fresh_entity, [dict(row)])

    assert fresh_workspace.query(fresh_entity).execute().rows() == public_workspace.query(public_entity).execute().rows()
    assert fresh_workspace.query(hb.Catalog).execute().rows() == public_workspace.query(hb.Catalog).execute().rows()


def test_hb_fresh_catalog_writer_prefers_supported_heavenbase_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace = paradev_hb._detached_workspace(
        "paradev-supported-fresh-catalog-mode",
        backends={"main": {"type": "sqlite", "database": (tmp_path / "fresh.sqlite").resolve().as_uri()}},
    )
    register_hoi4_extension()
    workspace.enable_extension(HOI4_EXTENSION_ID)
    entity = workspace.entities[paradev_hb.normalize_entity_identifier("module")]
    row = paradev_hb._catalog_row(
        "module",
        {
            "module_id": "focus/GER_contract",
            "family": "focus",
            "root": "src/modules/focus/GER_contract",
            "source_slots": {"def": ["def.txt"]},
            "metadata": {"object_id": "GER_contract"},
            "status": "loaded",
        },
    )
    calls: list[str] = []
    original_upsert_many = workspace.upsert_many

    def supported_upsert_many(entity_cls: type[hb.Entity], rows: list[dict[str, object]], *, catalog_mode: str) -> list[str]:
        calls.append(catalog_mode)
        return original_upsert_many(entity_cls, rows)

    monkeypatch.setattr(paradev_hb, "_heavenbase_fresh_catalog_mode_supported", lambda: True)
    monkeypatch.setattr(workspace, "upsert_many", supported_upsert_many)

    assert paradev_hb._write_fresh_catalog_chunk(workspace, entity, [row]) == [row["object_id"]]
    assert calls == ["fresh"]


def test_hb_catalog_preview_projects_build_rows_without_writing(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)

    payload = catalog_preview(project)

    assert payload["schema"] == "paradev.hb.catalog-preview.v1"
    assert payload["project_id"] == "minimal_hoi4"
    assert payload["game"] == "hoi4"
    assert payload["profile"] == "hoi4"
    assert payload["counts"] == {
        "asset": 0,
        "build-artifact": 5,
        "build-dependency": 2,
        "build-graph-edge": 5,
        "build-graph-node": 8,
        "collection": 1,
        "diagnostic": 0,
        "hoi4-entity": 1,
        "loc-entry": 2,
        "module": 1,
        "pdx-document": 1,
        "pdx-symbol": 3,
        "project": 1,
        "source-file": 2,
        "source-slot": 5,
        "sprite": 0,
    }
    assert payload["entities"]["project"] == [
        {
            "project_id": "minimal_hoi4",
            "title": "Minimal HOI4 Project",
            "game": "hoi4",
            "root": str(project_root),
            "manifest": str(project_root / "paradev.yaml"),
            "output_root": str(project_root / "build/mod"),
            "build_root": str(project_root / ".paradev/.cache/build"),
        }
    ]
    assert payload["entities"]["source-file"] == [
        {
            "owner_kind": "module",
            "module_id": "focus/GER_sample",
            "family": "focus",
            "root": str(project_root / "src/modules/focus/GER_sample"),
            "slot": "def",
            "path": str(project_root / "src/modules/focus/GER_sample/def.txt"),
            "relative_path": "def.txt",
            "loader": "pdx",
            "status": "loaded",
            "entry_count": 1,
        },
        {
            "owner_kind": "module",
            "module_id": "focus/GER_sample",
            "family": "focus",
            "root": str(project_root / "src/modules/focus/GER_sample"),
            "slot": "loc",
            "path": str(project_root / "src/modules/focus/GER_sample/main.loc"),
            "relative_path": "main.loc",
            "loader": "loc",
            "status": "loaded",
            "localization_count": 2,
            "languages": ["l_english"],
        },
    ]
    assert payload["entities"]["module"] == [
        {
            "module_id": "focus/GER_sample",
            "family": "focus",
            "root": str(project_root / "src/modules/focus/GER_sample"),
            "source_slots": {"def": ["def.txt"], "loc": ["main.loc"]},
            "metadata": {
                "after": ["focus:GER_rhineland"],
                "collection": "GER_main",
                "object_id": "GER_sample",
                "owner": "GER",
                "requires": ["idea:GER_industrial_spirit"],
                "tags": ["sample"],
                "title": "Sample Focus",
                "type": "focus",
            },
            "collection_id": "GER_main",
            "active": True,
            "status": "active",
        }
    ]
    assert payload["entities"]["collection"] == [
        {
            "collection_id": "GER_main",
            "family": "focus",
            "module_ids": ["focus/GER_sample"],
            "metadata": {},
        }
    ]
    assert [(row["slot"], row["status"], row["source_count"]) for row in payload["entities"]["source-slot"]] == [
        ("assets", "empty", 0),
        ("copy", "empty", 0),
        ("def", "satisfied", 1),
        ("icon", "empty", 0),
        ("loc", "satisfied", 1),
    ]
    assert payload["entities"]["source-slot"][2]["paths"] == [str(project_root / "src/modules/focus/GER_sample/def.txt")]
    assert payload["entities"]["hoi4-entity"] == [
        {
            "entity_id": "focus/GER_sample",
            "family": "focus",
            "object_id": "GER_sample",
            "module_id": "focus/GER_sample",
            "collection_id": "GER_main",
            "title": "Sample Focus",
            "owner": "GER",
            "tags": ["sample"],
        }
    ]
    assert [row["path"] for row in payload["entities"]["build-artifact"]] == [
        "common/national_focus/GER_main.txt",
        "views/focus-tree/GER_main.json",
        "localisation/english/GER_sample_l_english.yml",
        "descriptor.mod",
        "launcher/minimal_hoi4.mod",
    ]
    assert [row.get("module_ids", []) for row in payload["entities"]["build-artifact"]] == [
        ["focus/GER_sample"],
        ["focus/GER_sample"],
        ["focus/GER_sample"],
        [],
        [],
    ]
    assert [row.get("collection_ids", []) for row in payload["entities"]["build-artifact"]] == [
        ["GER_main"],
        ["GER_main"],
        [],
        [],
        [],
    ]
    assert [row["key"] for row in payload["entities"]["loc-entry"]] == ["GER_sample", "GER_sample_desc"]
    assert not project.build_root.exists()


def test_hb_catalog_keeps_inactive_modules_authorable_without_build_entities(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "inactive-module"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    metadata_path = project_root / "src/modules/focus/GER_sample/meta.yaml"
    metadata_path.write_text(
        metadata_path.read_text(encoding="utf-8") + "inactive: true\n",
        encoding="utf-8",
    )
    project = Project.load(project_root)

    result = project.build()
    payload = catalog_preview(project, result=result)

    assert result.modules == ()
    assert payload["counts"]["module"] == 1
    assert payload["counts"]["hoi4-entity"] == 0
    assert payload["entities"]["module"][0]["module_id"] == ("focus/GER_sample")
    assert payload["entities"]["module"][0]["active"] is False
    assert payload["entities"]["module"][0]["status"] == "inactive"


def test_hb_catalog_preview_indexes_pdx_documents_and_symbols(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)

    payload = catalog_preview(Project.load(project_root))

    document = dict(payload["entities"]["pdx-document"][0])
    ast_hash = document.pop("ast_hash")
    assert len(ast_hash) == 64
    assert document == {
        "document_id": "focus/GER_sample:def:def.txt",
        "module_id": "focus/GER_sample",
        "family": "focus",
        "slot": "def",
        "path": str(project_root / "src/modules/focus/GER_sample/def.txt"),
        "file_ext": ".txt",
        "entry_count": 1,
    }
    assert payload["entities"]["pdx-symbol"] == [
        {
            "symbol_id": "focus/GER_sample:def:def.txt:0",
            "document_id": "focus/GER_sample:def:def.txt",
            "module_id": "focus/GER_sample",
            "family": "focus",
            "slot": "def",
            "path": "focus",
            "key": "focus",
            "op": "=",
            "kind": "block",
            "line": 1,
            "column": 1,
        },
        {
            "symbol_id": "focus/GER_sample:def:def.txt:1",
            "document_id": "focus/GER_sample:def:def.txt",
            "module_id": "focus/GER_sample",
            "family": "focus",
            "slot": "def",
            "path": "focus/id",
            "key": "id",
            "op": "=",
            "kind": "scalar",
            "value": "GER_sample",
            "value_type": "id",
            "line": 2,
            "column": 2,
        },
        {
            "symbol_id": "focus/GER_sample:def:def.txt:2",
            "document_id": "focus/GER_sample:def:def.txt",
            "module_id": "focus/GER_sample",
            "family": "focus",
            "slot": "def",
            "path": "focus/cost",
            "key": "cost",
            "op": "=",
            "kind": "scalar",
            "value": "10",
            "value_type": "num",
            "line": 3,
            "column": 2,
        },
    ]


def test_hb_catalog_preview_cli_outputs_json(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)

    result = CliRunner().invoke(build_app(), ["hb", "catalog-preview", str(project_root), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.hb.catalog-preview.v1"
    assert payload["counts"]["project"] == 1
    assert payload["counts"]["build-artifact"] == 5
    assert payload["entities"]["build-dependency"] == [
        {
            "source": "module:focus/GER_sample",
            "target": "idea:GER_industrial_spirit",
            "kind": "requires",
        },
        {
            "source": "module:focus/GER_sample",
            "target": "focus:GER_rhineland",
            "kind": "after",
        },
    ]


def test_project_inspect_catalog_preview_outputs_hb_payload(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)

    payload = project.inspect("catalog-preview")

    assert payload == catalog_preview(project)
    assert payload["entities"]["source-file"][0]["loader"] == "pdx"


def test_hb_catalog_smoke_registers_preview_rows_without_writing(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)

    payload = catalog_smoke(project)

    assert payload["schema"] == "paradev.hb.catalog-smoke.v1"
    assert payload["project_id"] == "minimal_hoi4"
    assert payload["workspace_id"].startswith("paradev-smoke-minimal-hoi4-")
    assert payload["preview_counts"]["pdx-symbol"] == 3
    assert "hoi4" in hb.ext.Extension.identifiers(resolver=_CONTEXT_PARADEV.modules())
    assert payload["enabled_extensions"]["hoi4"]["entities"] == [
        "hoi4-asset",
        "hoi4-build-artifact",
        "hoi4-build-dependency",
        "hoi4-build-graph-edge",
        "hoi4-build-graph-node",
        "hoi4-collection",
        "hoi4-diagnostic",
        "hoi4-entity",
        "hoi4-loc-entry",
        "hoi4-module",
        "hoi4-pdx-document",
        "hoi4-pdx-symbol",
        "hoi4-project",
        "hoi4-source-file",
        "hoi4-source-slot",
        "hoi4-sprite",
    ]
    assert payload["registered_entities"] == [
        "hoi4-asset",
        "hoi4-build-artifact",
        "hoi4-build-dependency",
        "hoi4-build-graph-edge",
        "hoi4-build-graph-node",
        "hoi4-collection",
        "hoi4-diagnostic",
        "hoi4-entity",
        "hoi4-loc-entry",
        "hoi4-module",
        "hoi4-pdx-document",
        "hoi4-pdx-symbol",
        "hoi4-project",
        "hoi4-source-file",
        "hoi4-source-slot",
        "hoi4-sprite",
    ]
    assert payload["row_counts"]["pdx-symbol"] == 3
    assert payload["catalog_counts"]["hoi4-pdx-symbol"] == 3
    assert payload["catalog_count"] == sum(payload["row_counts"].values())
    assert payload["metaschema_entity_count"] >= len(payload["registered_entities"]) + 2
    assert payload["ok"] is True
    assert not project.build_root.exists()


def test_hb_catalog_smoke_cli_outputs_json(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)

    result = CliRunner().invoke(build_app(), ["hb", "catalog-smoke", str(project_root), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.hb.catalog-smoke.v1"
    assert payload["preview_counts"]["project"] == 1
    assert payload["catalog_counts"]["hoi4-project"] == 1
    assert payload["row_counts"]["build-artifact"] == 5


def test_hb_catalog_status_missing_is_side_effect_free(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    monkeypatch.setattr(Project, "build", lambda *args, **kwargs: pytest.fail("catalog_status built the project"))

    payload = catalog_status(project)

    database = project_root / ".paradev/.cache/hb/catalog.sqlite"
    assert payload == {
        "schema": "paradev.hb.catalog-status.v1",
        "project_id": "minimal_hoi4",
        "database": str(database),
        "status": "missing",
        "code": "catalog.missing",
    }
    assert project.catalog_status() == payload
    assert not (project_root / ".paradev").exists()
    assert not Path(f"{database}.refresh.lock").exists()


def test_hb_catalog_status_written_database_is_present(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    database = Path(str(catalog_write(project)["database"]))

    payload = project.catalog_status()

    assert payload == {
        "schema": "paradev.hb.catalog-status.v1",
        "project_id": "minimal_hoi4",
        "database": str(database),
        "status": "present",
        "code": "catalog.present",
    }


def test_hb_catalog_truncated_stale_marker_blocks_reads_fail_closed(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    database = Path(str(catalog_write(project)["database"]))
    marker = paradev_hb._catalog_stale_path(database)
    marker.touch()

    assert catalog_status(project)["status"] == "incomplete"
    with pytest.raises(RuntimeError, match="Refresh the project Catalog"):
        catalog_query(project, entity="module")
    with pytest.raises(RuntimeError, match="Refresh the project Catalog"):
        paradev_hb.catalog_completion_items(project)


@pytest.mark.parametrize("case", ["broken-symlink", "database-directory", "orphan-wal", "orphan-shm"])
def test_hb_catalog_status_classifies_incomplete_database_layouts(tmp_path: Path, case: str) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    database = tmp_path / "catalog.sqlite"
    if case == "broken-symlink":
        database.symlink_to(tmp_path / "missing.sqlite")
    elif case == "database-directory":
        database.mkdir()
    else:
        Path(f"{database}-{'wal' if case == 'orphan-wal' else 'shm'}").touch()

    payload = catalog_status(project, database=database)

    assert payload["database"] == str(database)
    assert payload["status"] == "incomplete"
    assert payload["code"] == "catalog.incomplete"


def test_hb_catalog_status_classifies_unreadable_database_permissions(tmp_path: Path) -> None:
    project = Project.load(PROJECT_ROOT)
    database = tmp_path / "catalog.sqlite"
    database.write_bytes(b"catalog")
    database.chmod(0)
    try:
        payload = catalog_status(project, database=database)
    finally:
        database.chmod(0o600)

    assert payload["status"] == "unreadable"
    assert payload["code"] == "catalog.unreadable"


def test_hb_catalog_status_classifies_stat_failure_as_unreadable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.load(PROJECT_ROOT)
    database = tmp_path / "catalog.sqlite"
    original_lstat = Path.lstat

    def guarded_lstat(path: Path) -> object:
        if path == database:
            raise PermissionError("catalog stat denied")
        return original_lstat(path)

    monkeypatch.setattr(Path, "lstat", guarded_lstat)

    payload = catalog_status(project, database=database)

    assert payload["status"] == "unreadable"
    assert payload["code"] == "catalog.unreadable"


def test_hb_catalog_write_creates_sqlite_database_without_build_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    monkeypatch.setattr(paradev_hb, "catalog_preview", lambda *args, **kwargs: pytest.fail("catalog_write materialized a full preview"))

    payload = catalog_write(project)

    database = project_root / ".paradev/.cache/hb/catalog.sqlite"
    assert payload["schema"] == "paradev.hb.catalog-write.v1"
    assert payload["project_id"] == "minimal_hoi4"
    assert payload["database"] == str(database)
    assert payload["workspace_id"].startswith("paradev-catalog-minimal-hoi4-")
    assert payload["row_counts"]["pdx-symbol"] == 3
    assert payload["catalog_counts"]["hoi4-pdx-symbol"] == 3
    assert payload["catalog_count"] == sum(payload["row_counts"].values())
    assert payload["ok"] is True
    assert database.exists()
    assert not project.build_root.exists()
    with sqlite3.connect(database) as connection:
        indexes = {str(row[1]) for row in connection.execute("pragma index_list('sys_catalog')")}
    assert "paradev_sys_catalog_browse" in indexes


def test_hb_initial_catalog_write_blocks_partial_reads(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    database = project_root / ".paradev/.cache/hb/catalog.sqlite"
    materializing = Event()
    release = Event()
    errors: list[BaseException] = []
    original = paradev_hb._catalog_workspace_summary

    def blocked_summary(payload: object, workspace: hb.HeavenBase) -> dict[str, object]:
        materializing.set()
        assert release.wait(timeout=10)
        assert isinstance(payload, dict)
        return original(payload, workspace)

    monkeypatch.setattr(paradev_hb, "_catalog_workspace_summary", blocked_summary)

    def write() -> None:
        try:
            catalog_write(project, preview=catalog_preview(project))
        except BaseException as error:
            errors.append(error)

    writer = Thread(target=write)
    writer.start()
    try:
        assert materializing.wait(timeout=10)
        assert database.is_file()
        assert paradev_hb._catalog_stale_path(database).is_file()
        with pytest.raises(RuntimeError, match="Refresh the project Catalog"):
            catalog_query(project, entity="module")
        with pytest.raises(RuntimeError, match="Refresh the project Catalog"):
            paradev_hb.catalog_completion_items(project, prefix="GER")
    finally:
        release.set()
        writer.join(timeout=30)

    assert not writer.is_alive()
    assert errors == []
    assert catalog_status(project)["status"] == "present"


def test_hb_module_rename_marks_the_complete_catalog_stale(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    database = Path(str(catalog_write(project)["database"]))
    before_counts = paradev_hb._catalog_database_counts(database)

    payload = project.rename_module("focus/GER_sample", "GER_renamed")

    assert payload["catalog_mutation"] == {
        "schema": "paradev.hb.catalog-mutation.v1",
        "status": "failed",
        "code": "catalog.mutation.failed",
        "database": str(database),
        "message": (
            "Project sources changed, so the derived HeavenBase Catalog is stale. " "Refresh the project Catalog before using Catalog queries or completions."
        ),
    }
    assert paradev_hb.catalog_status(project)["code"] == "catalog.incomplete"
    assert paradev_hb._catalog_stale_path(database).is_file()
    assert paradev_hb._catalog_database_counts(database) == before_counts
    assert not (project_root / "src/modules/focus/GER_sample").exists()
    assert (project_root / "src/modules/focus/GER_renamed").is_dir()
    with pytest.raises(RuntimeError, match="Refresh the project Catalog"):
        catalog_query(project, entity="module")
    with pytest.raises(RuntimeError, match="Refresh the project Catalog"):
        paradev_hb.catalog_completion_items(project, prefix="GER")


def test_hb_module_create_marks_existing_catalog_stale(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    database = Path(str(catalog_write(project)["database"]))
    before_counts = paradev_hb._catalog_database_counts(database)

    payload = project.create_module(
        "idea",
        "GER_industry_spirit",
        values={"title": "German Industry Spirit", "description": "Industrial production spirit."},
    )

    assert payload["written"] is True
    assert payload["catalog_mutation"]["status"] == "failed"
    assert "Refresh the project Catalog" in payload["catalog_mutation"]["message"]
    assert paradev_hb.catalog_status(project)["status"] == "incomplete"
    assert paradev_hb._catalog_database_counts(database) == before_counts


def test_hb_source_draft_marks_existing_catalog_stale(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    database = Path(str(catalog_write(project)["database"]))
    before_counts = paradev_hb._catalog_database_counts(database)
    metadata_path = project_root / "src/modules/focus/GER_sample/meta.yaml"
    metadata_text = metadata_path.read_text(encoding="utf-8").replace("title: Sample Focus", "title: Updated Sample Focus")

    payload = project.apply_source_draft(source_edits=[{"path": str(metadata_path), "text": metadata_text}])

    assert payload["catalog_mutation"] == {
        "schema": "paradev.hb.catalog-mutation.v1",
        "status": "failed",
        "code": "catalog.mutation.failed",
        "database": str(database),
        "message": (
            "Project sources changed, so the derived HeavenBase Catalog is stale. " "Refresh the project Catalog before using Catalog queries or completions."
        ),
    }
    assert "title: Updated Sample Focus" in metadata_path.read_text(encoding="utf-8")
    assert paradev_hb.catalog_status(project)["status"] == "incomplete"
    assert paradev_hb._catalog_database_counts(database) == before_counts


def test_hb_module_catalog_authoring_row_only_synthesizes_authoritative_metadata(tmp_path: Path) -> None:
    module_root = tmp_path / "src/modules/focus/GER_sample"
    module_root.mkdir(parents=True)
    (module_root / "meta.yml").write_text("title: Ignored metadata\n", encoding="utf-8")
    row = {"module_id": "focus/GER_sample", "root": str(module_root)}

    assert paradev_hb._module_catalog_authoring_row(row)["source_slots"] == {}

    (module_root / "meta.yaml").write_text("title: Authoritative metadata\n", encoding="utf-8")

    assert paradev_hb._module_catalog_authoring_row(row)["source_slots"] == {"meta": ["meta.yaml"]}


def test_hb_module_catalog_projection_reports_post_write_materialization_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project = Project.create(tmp_path / "starter", title="Starter")
    with project.manifest_path.open("a", encoding="utf-8") as stream:
        stream.write(
            "\ntemplates:\n"
            "  modifier/source-only:\n"
            "    title: Source-only Modifier\n"
            "    family: modifier\n"
            "    files:\n"
            "      def.txt: '{object_id} = {{}}'\n"
        )
    project = Project.load(project.root)
    database = Path(str(catalog_write(project)["database"]))
    before_counts = paradev_hb._catalog_database_counts(database)

    def fail_projection(*args, **kwargs):
        raise ValueError("Unknown module after scaffold")

    monkeypatch.setattr(project_sdk, "_find_project_module", fail_projection)

    payload = project.scaffold_module("modifier/source-only", "GER_notes", write=True)

    assert payload["written"] is True
    assert payload["catalog_mutation"]["status"] == "failed"
    assert "Unknown module after scaffold" in payload["catalog_mutation"]["message"]
    assert (project.root / "src/modules/modifier/GER_notes/def.txt").read_text(encoding="utf-8") == "GER_notes = {}\n"
    assert paradev_hb._catalog_database_counts(database) == before_counts


def test_hb_module_remove_preserves_old_catalog_only_as_blocked_stale_cache(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    database = Path(str(catalog_write(project)["database"]))
    expected_counts = paradev_hb._catalog_database_counts(database)

    payload = project.remove_module("focus/GER_sample", write=True)

    assert payload["removed"] is True
    assert payload["catalog_mutation"]["status"] == "failed"
    assert "Refresh the project Catalog" in payload["catalog_mutation"]["message"]
    assert paradev_hb.catalog_status(project)["status"] == "incomplete"
    assert paradev_hb._catalog_database_counts(database) == expected_counts
    with pytest.raises(RuntimeError, match="Refresh the project Catalog"):
        catalog_query(project, entity="module")


def test_hb_module_catalog_projection_missing_is_not_configured_without_database(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    database = project_root / ".paradev/.cache/hb/catalog.sqlite"

    payload = project.rename_module("focus/GER_sample", "GER_renamed")

    assert payload["catalog_mutation"] == {
        "schema": "paradev.hb.catalog-mutation.v1",
        "status": "not_configured",
        "code": "catalog.mutation.not_configured",
        "database": str(database),
    }
    assert not database.exists()
    assert Path(f"{database}.refresh.lock").is_file()


def test_hb_catalog_refresh_rebuilds_and_clears_module_stale_marker(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    database = Path(str(catalog_write(project)["database"]))

    payload = project.rename_module("focus/GER_sample", "GER_refreshed")

    mutation = payload["catalog_mutation"]
    assert mutation["status"] == "failed"
    assert mutation["code"] == "catalog.mutation.failed"
    assert paradev_hb.catalog_status(project)["status"] == "incomplete"
    assert paradev_hb._catalog_stale_path(database).is_file()

    refreshed = catalog_refresh(project)

    assert refreshed["ok"] is True
    assert paradev_hb.catalog_status(project)["status"] == "present"
    assert not paradev_hb._catalog_stale_path(database).exists()
    modules = catalog_query(project, entity="module")
    assert modules["count"] == 1
    assert modules["rows"][0]["data"]["module_id"] == "focus/GER_refreshed"
    source_files = catalog_query(project, entity="source-file")
    assert source_files["count"] == 2
    assert all("GER_refreshed" in row["data"]["path"] for row in source_files["rows"])


def test_hb_catalog_refresh_failure_keeps_stale_catalog_reads_blocked(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    database = Path(str(catalog_write(project)["database"]))
    before_counts = paradev_hb._catalog_database_counts(database)
    project.rename_module("focus/GER_sample", "GER_refresh_failed")

    def fail_replace(_source: Path, _target: Path) -> list[Path]:
        raise OSError("injected Catalog replacement failure")

    monkeypatch.setattr(paradev_hb, "_replace_database_file", fail_replace)

    with pytest.raises(OSError, match="injected Catalog replacement failure"):
        catalog_refresh(project)

    assert paradev_hb._catalog_stale_path(database).is_file()
    assert catalog_status(project)["status"] == "incomplete"
    assert paradev_hb._catalog_database_counts(database) == before_counts
    with pytest.raises(RuntimeError, match="Refresh the project Catalog"):
        catalog_query(project, entity="module")


@pytest.mark.parametrize("initial_status", ["missing", "present"])
def test_hb_module_catalog_invalidation_waits_for_refresh_writer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    initial_status: str,
) -> None:
    project = SimpleNamespace(root=tmp_path, project_id="mutation-lock")
    database = paradev_hb._catalog_database_path(project, None)
    status_checked = Event()
    ready = Event()
    if initial_status == "present":
        ready.set()

    def fake_status(_project, **_kwargs):
        status_checked.set()
        status = "present" if ready.is_set() else "missing"
        return {"status": status, "code": f"catalog.{status}"}

    monkeypatch.setattr(paradev_hb, "catalog_status", fake_status)

    result: list[dict[str, object]] = []
    errors: list[BaseException] = []

    def mutate() -> None:
        try:
            result.append(
                paradev_hb._sync_module_catalog_projection(
                    project,
                    previous={"module_id": "focus/GER_old", "root": "src/modules/focus/GER_old"},
                )
            )
        except BaseException as error:
            errors.append(error)

    with paradev_hb._catalog_refresh_lock(database):
        thread = Thread(target=mutate, daemon=True)
        thread.start()
        assert status_checked.wait(timeout=1)
        assert thread.is_alive()
        ready.set()
    thread.join(timeout=2)

    assert not thread.is_alive()
    assert errors == []
    assert result[0]["status"] == "failed"
    assert "Refresh the project Catalog" in result[0]["message"]
    assert paradev_hb._catalog_stale_path(database).is_file()


def test_hb_initial_catalog_write_orders_before_module_rename(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    original_build = Project.build
    snapshot_ready = Event()
    release_writer = Event()
    rename_finished = Event()
    writer_results: list[dict[str, object]] = []
    rename_results: list[dict[str, object]] = []
    errors: list[BaseException] = []

    def paused_build(self, *args, **kwargs):
        result = original_build(self, *args, **kwargs)
        snapshot_ready.set()
        if not release_writer.wait(timeout=10):
            raise TimeoutError("Catalog writer test was not released")
        return result

    def write_catalog() -> None:
        try:
            writer_results.append(catalog_write(project))
        except BaseException as error:
            errors.append(error)

    def rename_module() -> None:
        try:
            rename_results.append(project.rename_module("focus/GER_sample", "GER_renamed"))
        except BaseException as error:
            errors.append(error)
        finally:
            rename_finished.set()

    monkeypatch.setattr(Project, "build", paused_build)
    writer = Thread(target=write_catalog, daemon=True)
    writer.start()
    try:
        assert snapshot_ready.wait(timeout=10)
        renamer = Thread(target=rename_module, daemon=True)
        renamer.start()
        assert not rename_finished.wait(timeout=0.1)
        assert (project_root / "src/modules/focus/GER_sample").is_dir()
    finally:
        release_writer.set()
    writer.join(timeout=60)
    renamer.join(timeout=60)

    assert not writer.is_alive()
    assert not renamer.is_alive()
    assert errors == []
    assert writer_results[0]["ok"] is True
    assert rename_results[0]["catalog_mutation"]["status"] == "failed"
    assert paradev_hb.catalog_status(project)["status"] == "incomplete"
    assert not (project_root / "src/modules/focus/GER_sample").exists()
    assert (project_root / "src/modules/focus/GER_renamed").is_dir()
    with pytest.raises(RuntimeError, match="Refresh the project Catalog"):
        catalog_query(project, entity="module")


def test_hb_module_rename_and_remove_share_source_delta_ordering(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    catalog_write(project)
    original_sync = paradev_hb._sync_module_catalog_projection
    renamed_source_ready = Event()
    release_rename = Event()
    remove_finished = Event()
    rename_results: list[dict[str, object]] = []
    remove_results: list[dict[str, object]] = []
    errors: list[BaseException] = []

    def paused_sync(*args, **kwargs):
        if kwargs.get("current") is not None:
            renamed_source_ready.set()
            if not release_rename.wait(timeout=10):
                raise TimeoutError("Module rename test was not released")
        return original_sync(*args, **kwargs)

    def rename_module() -> None:
        try:
            rename_results.append(project.rename_module("focus/GER_sample", "GER_renamed"))
        except BaseException as error:
            errors.append(error)

    def remove_module() -> None:
        try:
            remove_results.append(project.remove_module("focus/GER_renamed", write=True))
        except BaseException as error:
            errors.append(error)
        finally:
            remove_finished.set()

    monkeypatch.setattr(paradev_hb, "_sync_module_catalog_projection", paused_sync)
    renamer = Thread(target=rename_module, daemon=True)
    renamer.start()
    try:
        assert renamed_source_ready.wait(timeout=10)
        assert not (project_root / "src/modules/focus/GER_sample").exists()
        assert (project_root / "src/modules/focus/GER_renamed").is_dir()
        remover = Thread(target=remove_module, daemon=True)
        remover.start()
        assert not remove_finished.wait(timeout=0.1)
    finally:
        release_rename.set()
    renamer.join(timeout=30)
    remover.join(timeout=30)

    assert not renamer.is_alive()
    assert not remover.is_alive()
    assert errors == []
    assert rename_results[0]["catalog_mutation"]["status"] == "failed"
    assert remove_results[0]["removed"] is True
    assert remove_results[0]["catalog_mutation"]["status"] == "failed"
    assert paradev_hb.catalog_status(project)["status"] == "incomplete"
    with pytest.raises(RuntimeError, match="Refresh the project Catalog"):
        catalog_query(project, entity="module")


def test_hb_module_catalog_scope_marks_stale_before_source_mutation(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    database = Path(str(catalog_write(project)["database"]))

    with paradev_hb._module_catalog_mutation_scope(project):
        assert paradev_hb._catalog_stale_path(database).is_file()
        assert paradev_hb.catalog_status(project)["status"] == "incomplete"


def test_hb_module_catalog_scope_marks_an_incomplete_catalog_stale(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    database = Path(str(catalog_write(project)["database"]))
    database.unlink()
    database.mkdir()
    assert paradev_hb.catalog_status(project)["status"] == "incomplete"

    with paradev_hb._module_catalog_mutation_scope(project):
        assert paradev_hb._catalog_stale_path(database).is_file()
        with pytest.raises(RuntimeError, match="Refresh the project Catalog"):
            catalog_query(project, entity="module")


def test_hb_module_catalog_scope_aborts_before_source_mutation_when_invalidation_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    catalog_write(project)
    source_mutation_reached = False

    def fail_invalidation(_database: Path) -> Path:
        raise OSError("injected stale marker failure")

    monkeypatch.setattr(paradev_hb, "_mark_catalog_stale", fail_invalidation)

    with pytest.raises(OSError, match="injected stale marker failure"):
        with paradev_hb._module_catalog_mutation_scope(project):
            source_mutation_reached = True

    assert source_mutation_reached is False
    assert paradev_hb.catalog_status(project)["status"] == "present"


def test_hb_catalog_refresh_staging_paths_are_unique(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite"
    payload = {"project_id": "minimal_hoi4"}

    first = paradev_hb._refresh_database_path(database, payload)
    second = paradev_hb._refresh_database_path(database, payload)

    assert first != second
    assert first.parent == database.parent
    assert first.name.startswith("catalog.sqlite.refresh-")
    assert second.name.startswith("catalog.sqlite.refresh-")


def test_hb_catalog_refresh_lock_serializes_only_the_same_target(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite"
    other_database = tmp_path / "other.sqlite"

    with paradev_hb._catalog_refresh_lock(database):
        with pytest.raises(BlockingIOError, match="catalog refresh already in progress"):
            with paradev_hb._catalog_refresh_lock(database):
                pytest.fail("A second same-target refresh acquired the mutex")
        with pytest.raises(BlockingIOError, match="catalog refresh already in progress"):
            with paradev_hb._catalog_refresh_lock(database, timeout=0.01):
                pytest.fail("A bounded same-target writer acquired the mutex")
        with paradev_hb._catalog_refresh_lock(other_database):
            pass


def test_hb_catalog_refresh_lock_cleanup_does_not_mask_completed_operation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    completed = Event()

    class FailingCleanupConnection:
        in_transaction = True

        def execute(self, _statement: str) -> None:
            return None

        def rollback(self) -> None:
            raise RuntimeError("injected rollback failure")

        def close(self) -> None:
            raise RuntimeError("injected close failure")

    monkeypatch.setattr(paradev_hb.sqlite3, "connect", lambda *_args, **_kwargs: FailingCleanupConnection())

    with caplog.at_level(logging.WARNING, logger="paradev.hb"):
        with paradev_hb._catalog_refresh_lock(tmp_path / "catalog.sqlite"):
            completed.set()

    assert completed.is_set()
    assert "injected rollback failure" in caplog.text
    assert "injected close failure" in caplog.text


def test_hb_catalog_refresh_lock_cleanup_preserves_inner_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    class FailingCleanupConnection:
        in_transaction = True

        def execute(self, _statement: str) -> None:
            return None

        def rollback(self) -> None:
            raise RuntimeError("injected rollback failure")

        def close(self) -> None:
            raise RuntimeError("injected close failure")

    monkeypatch.setattr(paradev_hb.sqlite3, "connect", lambda *_args, **_kwargs: FailingCleanupConnection())

    with caplog.at_level(logging.WARNING, logger="paradev.hb"):
        with pytest.raises(ValueError, match="primary mutation failure"):
            with paradev_hb._catalog_refresh_lock(tmp_path / "catalog.sqlite"):
                raise ValueError("primary mutation failure")

    assert "injected rollback failure" in caplog.text
    assert "injected close failure" in caplog.text


def test_hb_catalog_refresh_lock_recovers_after_killed_process(tmp_path: Path) -> None:
    database = tmp_path / "catalog.sqlite"
    staging = paradev_hb._refresh_database_path(database, {"project_id": "interrupted"})
    staging.touch()
    Path(f"{staging}-wal").touch()
    script = (
        "import time\n"
        "from pathlib import Path\n"
        "from paradev.hb import _catalog_refresh_lock\n"
        f"database = Path({str(database)!r})\n"
        "with _catalog_refresh_lock(database):\n"
        "    print('locked', flush=True)\n"
        "    time.sleep(60)\n"
    )
    process = subprocess.Popen(
        [sys.executable, "-c", script],
        cwd=Path.cwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert process.stdout is not None
        assert process.stdout.readline().strip() == "locked"
        process.kill()
        assert process.wait(timeout=10) != 0
        with paradev_hb._catalog_refresh_lock(database):
            recovered = paradev_hb._remove_stale_refresh_databases(database)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)

    assert set(recovered) == {staging, Path(f"{staging}-wal")}
    assert not staging.exists()
    assert not Path(f"{staging}-wal").exists()


def test_hb_catalog_read_uri_preserves_committed_legacy_wal_rows(tmp_path: Path) -> None:
    database = tmp_path / "legacy-catalog.sqlite"
    writer = sqlite3.connect(database)
    try:
        writer.execute("pragma journal_mode=wal")
        writer.execute("pragma wal_autocheckpoint=0")
        writer.execute("create table legacy_catalog_probe (value text not null)")
        writer.execute("insert into legacy_catalog_probe values ('visible')")
        writer.commit()

        uri = paradev_hb._catalog_read_uri(database)

        assert uri.endswith("?mode=ro")
        with sqlite3.connect(uri, uri=True) as reader:
            assert reader.execute("select value from legacy_catalog_probe").fetchone() == ("visible",)
    finally:
        writer.close()


def test_hb_catalog_write_accepts_relative_database_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    monkeypatch.chdir(tmp_path)

    payload = catalog_write(project, database="catalog #1.sqlite")

    database = tmp_path / "catalog #1.sqlite"
    assert payload["database"] == str(database)
    assert database.is_file()


def test_hb_catalog_write_bounds_catalog_fields_without_dropping_target_data(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    delete_dir(project_root / ".paradev")
    project = Project.load(project_root)
    preview = catalog_preview(project)
    long_edge_id = "edge:" + ("very-long-segment:" * 24)
    long_loc_text = "Long localization body. " * 260
    preview["entities"]["build-graph-edge"].append(
        {
            "edge_id": long_edge_id,
            "kind": "requires",
            "source": "source:long",
            "target": "target:long",
        }
    )
    preview["entities"]["loc-entry"].append(
        {
            "key": "LONG_LOC",
            "language": "l_english",
            "text": long_loc_text,
            "module_id": "focus/GER_sample",
        }
    )
    for index in range(997):
        preview["entities"]["loc-entry"].append(
            {
                "key": f"BULK_LOC_{index}",
                "language": "l_english",
                "text": f"Bulk localization {index}",
                "module_id": "focus/GER_sample",
            }
        )
    database = project_root / ".paradev/.cache/hb/catalog.sqlite"

    catalog_write(project, preview=preview, database=database)

    edge_payload = catalog_query(project, entity="build-graph-edge")
    edge_row = next(row for row in edge_payload["rows"] if row["data"].get("edge_id") == long_edge_id)
    assert len(edge_row["name"]) <= 255
    assert edge_row["data"]["edge_id"] == long_edge_id
    loc_payload = catalog_query(project, entity="loc-entry")
    loc_row = next(row for row in loc_payload["rows"] if row["data"].get("key") == "LONG_LOC")
    assert len(loc_row["desc"]) <= 4095
    assert loc_row["data"]["text"] == long_loc_text


def test_hb_catalog_preview_indexes_build_graph_nodes_and_edges(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)

    payload = catalog_preview(Project.load(project_root))

    graph_nodes = payload["entities"]["build-graph-node"]
    graph_edges = payload["entities"]["build-graph-edge"]
    assert graph_nodes[0] == {
        "id": "artifact:build:views/focus-tree/GER_main.json",
        "type": "artifact",
        "group": "artifact:build",
        "label": "views/focus-tree/GER_main.json",
        "display_label": "GER_main.json",
        "display_detail": "build / views/focus-tree",
        "display_path": "views/focus-tree/GER_main.json",
        "path": "views/focus-tree/GER_main.json",
        "artifact_type": "view",
        "target_root": "build",
        "owner": "collection:GER_main",
        "module_ids": ["focus/GER_sample"],
        "collection_ids": ["GER_main"],
    }
    assert {
        "edge_id": "module:focus/GER_sample:requires:reference:idea:GER_industrial_spirit",
        "source": "module:focus/GER_sample",
        "target": "reference:idea:GER_industrial_spirit",
        "kind": "requires",
    } in graph_edges
    assert {
        "edge_id": f"source:{project_root / 'src/modules/focus/GER_sample/def.txt'}:emits:artifact:output:common/national_focus/GER_main.txt",
        "source": f"source:{project_root / 'src/modules/focus/GER_sample/def.txt'}",
        "target": "artifact:output:common/national_focus/GER_main.txt",
        "kind": "emits",
        "artifact_type": "pdx",
        "target_root": "output",
    } in graph_edges


def test_hb_catalog_write_refuses_existing_database_files(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    database = project_root / ".paradev/.cache/hb/catalog.sqlite"
    database.parent.mkdir(parents=True)
    database.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError, match="catalog.sqlite"):
        catalog_write(Project.load(project_root))


def test_hb_catalog_write_removes_partial_database_after_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    database = project_root / ".paradev/.cache/hb/catalog.sqlite"

    def fail_summary(payload: object, workspace: object) -> dict[str, object]:
        del payload, workspace
        raise RuntimeError("catalog materialization failed")

    monkeypatch.setattr(paradev_hb, "_catalog_workspace_summary", fail_summary)

    with pytest.raises(RuntimeError, match="catalog materialization failed"):
        catalog_write(project, preview={"project_id": project.project_id})

    assert not database.exists()
    assert not Path(f"{database}-wal").exists()
    assert not Path(f"{database}-shm").exists()
    assert not paradev_hb._catalog_stale_path(database).exists()


def test_hb_catalog_write_cli_outputs_json(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)

    result = CliRunner().invoke(build_app(), ["hb", "catalog-write", str(project_root), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.hb.catalog-write.v1"
    assert payload["database"] == str(project_root / ".paradev/.cache/hb/catalog.sqlite")
    assert payload["catalog_counts"]["hoi4-project"] == 1
    assert payload["row_counts"]["build-artifact"] == 5


def test_hb_catalog_refresh_replaces_existing_database_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    write_payload = catalog_write(project)
    database = Path(str(write_payload["database"]))
    wal = Path(f"{database}-wal")
    shm = Path(f"{database}-shm")
    wal.write_text("stale wal", encoding="utf-8")
    shm.write_text("stale shm", encoding="utf-8")
    orphan = paradev_hb._refresh_database_path(database, {"project_id": "orphan"})
    orphan_sidecar_only = paradev_hb._refresh_database_path(database, {"project_id": "sidecar-only"})
    orphan.touch()
    Path(f"{orphan}-wal").touch()
    Path(f"{orphan}-shm").touch()
    Path(f"{orphan_sidecar_only}-wal").touch()
    near_match = database.with_name(f"{database.name}.refresh-not-owned.sqlite")
    near_match.touch()
    monkeypatch.setattr(paradev_hb, "catalog_preview", lambda *args, **kwargs: pytest.fail("catalog_refresh materialized a full preview"))

    payload = catalog_refresh(project)

    assert payload["schema"] == "paradev.hb.catalog-refresh.v1"
    assert payload["database"] == str(database)
    assert payload["removed"] == [str(database), str(wal), str(shm)]
    assert set(payload["recovered"]) == {
        str(orphan),
        str(Path(f"{orphan}-wal")),
        str(Path(f"{orphan}-shm")),
        str(Path(f"{orphan_sidecar_only}-wal")),
    }
    assert payload["catalog_counts"]["hoi4-pdx-symbol"] == 3
    assert payload["ok"] is True
    assert database.exists()
    assert not wal.exists()
    assert not shm.exists()
    assert near_match.exists()
    assert catalog_query(project, entity="pdx-symbol")["count"] == 3


def test_hb_catalog_refresh_cli_outputs_json(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    catalog_write(Project.load(project_root))
    database = project_root / ".paradev/.cache/hb/catalog.sqlite"
    expected_removed = [str(path) for path in (database, Path(f"{database}-wal"), Path(f"{database}-shm")) if path.exists()]

    result = CliRunner().invoke(build_app(), ["hb", "catalog-refresh", str(project_root), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.hb.catalog-refresh.v1"
    assert payload["database"] == str(database)
    assert payload["removed"] == expected_removed
    assert payload["row_counts"]["build-artifact"] == 5


def test_hb_catalog_write_and_refresh_rest_routes_output_json(tmp_path: Path) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces.rest import build_app as build_rest_app

    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    client = testclient.TestClient(build_rest_app())

    write_response = client.post("/projects/catalog", params={"path": str(project_root)})

    assert write_response.status_code == 200, write_response.text
    write_payload = write_response.json()
    database = project_root / ".paradev/.cache/hb/catalog.sqlite"
    assert write_payload["schema"] == "paradev.hb.catalog-write.v1"
    assert write_payload["database"] == str(database)
    assert write_payload["catalog_counts"]["hoi4-project"] == 1
    assert database.exists()

    refresh_response = client.put("/projects/catalog", params={"path": str(project_root)})

    assert refresh_response.status_code == 200, refresh_response.text
    refresh_payload = refresh_response.json()
    assert refresh_payload["schema"] == "paradev.hb.catalog-refresh.v1"
    assert refresh_payload["database"] == str(database)
    assert str(database) in refresh_payload["removed"]
    assert set(refresh_payload["removed"]).issubset({str(database), f"{database}-wal", f"{database}-shm"})
    assert refresh_payload["row_counts"]["build-artifact"] == 5


def test_hb_catalog_query_reads_written_sqlite_catalog(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)

    payload = catalog_query(project, entity="hoi4-pdx-symbol")

    assert payload["schema"] == "paradev.hb.catalog-query.v1"
    assert payload["project_id"] == "minimal_hoi4"
    assert payload["database"] == str(project_root / ".paradev/.cache/hb/catalog.sqlite")
    assert payload["filters"] == {"entity": "hoi4-pdx-symbol"}
    assert payload["total_count"] == 37
    assert payload["count"] == 3
    assert [row["name"] for row in payload["rows"]] == ["focus", "focus/cost", "focus/id"]
    assert all(row["target_entity"] == "hoi4-pdx-symbol" for row in payload["rows"])
    preview_symbols = {row["path"]: row for row in catalog_preview(project)["entities"]["pdx-symbol"]}
    assert {row["name"]: row["data"] for row in payload["rows"]} == preview_symbols
    database = project_root / ".paradev/.cache/hb/catalog.sqlite"
    with sqlite3.connect(database) as connection:
        columns = {str(row[1]) for row in connection.execute("pragma table_info(hoi4_pdx_symbol)")}
    assert columns == {
        "object_id",
        "symbol_id",
        "document_id",
        "module_id",
        "collection_id",
        "family",
        "slot",
        "path",
        "symbol_key",
        "kind",
        "op",
        "value",
        "value_type",
        "source_line",
        "source_column",
    }


def test_hb_catalog_reads_pre_typed_pdx_symbol_cache(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)
    expected = catalog_query(project, entity="pdx-symbol")
    database = project_root / ".paradev/.cache/hb/catalog.sqlite"

    with sqlite3.connect(database) as connection:
        connection.execute("drop table hoi4_pdx_symbol")
        connection.execute("create table hoi4_pdx_symbol (object_id text primary key, data text)")
        connection.executemany(
            "insert into hoi4_pdx_symbol (object_id, data) values (?, ?)",
            [(row["target_id"], json.dumps(row["data"])) for row in expected["rows"]],
        )

    payload = catalog_query(project, entity="pdx-symbol")
    completions = paradev_hb.catalog_completion_items(project, prefix="cost", limit=20)

    assert payload["rows"] == expected["rows"]
    assert [item["label"] for item in completions] == ["cost"]
    assert completions[0]["detail"] == "focus/cost"


def test_hb_catalog_query_reads_persisted_build_graph_edges(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)

    payload = catalog_query(project, entity="build-graph-edge", tag="requires")

    assert payload["filters"] == {"entity": "hoi4-build-graph-edge", "tag": "requires"}
    assert payload["count"] == 1
    assert payload["rows"][0]["name"] == "module:focus/GER_sample:requires:reference:idea:GER_industrial_spirit"
    assert payload["rows"][0]["target_entity"] == "hoi4-build-graph-edge"
    assert payload["rows"][0]["tags"] == [
        "build-graph-edge",
        "requires",
        "module:focus/GER_sample",
        "reference:idea:GER_industrial_spirit",
    ]


def test_hb_catalog_query_finds_artifacts_by_module_tag(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)

    payload = catalog_query(project, entity="build-artifact", tag="focus/GER_sample")

    assert payload["filters"] == {"entity": "hoi4-build-artifact", "tag": "focus/GER_sample"}
    assert payload["count"] == 3
    assert [row["name"] for row in payload["rows"]] == [
        "common/national_focus/GER_main.txt",
        "localisation/english/GER_sample_l_english.yml",
        "views/focus-tree/GER_main.json",
    ]
    assert all("focus/GER_sample" in row["tags"] for row in payload["rows"])


def test_hb_streaming_catalog_query_finds_modules_by_family_tag(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)

    payload = catalog_query(project, entity="module", tag="focus", include_data=False)

    assert payload["filters"] == {"entity": "hoi4-module", "tag": "focus", "include_data": False}
    assert payload["count"] == 1
    assert payload["rows"][0]["name"] == "focus/GER_sample"
    assert payload["rows"][0]["tags"] == [
        "module",
        "focus",
        "focus/GER_sample",
        "GER_main",
        "active",
    ]
    assert "data" not in payload["rows"][0]
    database = project_root / ".paradev/.cache/hb/catalog.sqlite"
    assert not Path(f"{database}-wal").exists()
    assert not Path(f"{database}-shm").exists()
    with sqlite3.connect(f"{database.resolve().as_uri()}?mode=ro&immutable=1", uri=True) as connection:
        tag_type, tag_count = connection.execute(
            "select json_type(tags), json_array_length(tags) from sys_catalog where target_entity = ?",
            ("hoi4-module",),
        ).fetchone()
    assert (tag_type, tag_count) == ("array", 5)


def test_hb_catalog_query_finds_sources_by_loader_tag(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)

    payload = catalog_query(project, entity="source-file", tag="loader:pdx")

    assert payload["filters"] == {"entity": "hoi4-source-file", "tag": "loader:pdx"}
    assert payload["count"] == 1
    assert payload["rows"][0]["name"] == str(project_root / "src/modules/focus/GER_sample/def.txt")
    assert payload["rows"][0]["data"] == {
        "owner_kind": "module",
        "module_id": "focus/GER_sample",
        "family": "focus",
        "root": str(project_root / "src/modules/focus/GER_sample"),
        "slot": "def",
        "path": str(project_root / "src/modules/focus/GER_sample/def.txt"),
        "relative_path": "def.txt",
        "loader": "pdx",
        "status": "loaded",
        "entry_count": 1,
    }
    assert {"module:focus/GER_sample", "slot:def", "loader:pdx", "status:loaded"}.issubset(set(payload["rows"][0]["tags"]))


def test_project_inspect_catalog_query_reads_persisted_rows(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)

    payload = project.inspect("catalog-query", entity="source-file", tag="loader:pdx")

    assert payload["schema"] == "paradev.hb.catalog-query.v1"
    assert payload["filters"] == {
        "entity": "hoi4-source-file",
        "tag": "loader:pdx",
        "limit": 100,
        "include_data": False,
    }
    assert payload["count"] == 1
    assert "data" not in payload["rows"][0]


def test_project_inspect_catalog_query_rejects_unsafe_pages(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)

    with pytest.raises(ValueError, match="integer from 1 to 200"):
        project.inspect("  CATALOG_QUERY  ", limit=201)
    with pytest.raises(ValueError, match="hydrated requests must use limit 1"):
        project.inspect("catalog_query", include_data=True)


def test_hb_catalog_query_filters_by_name_and_tag(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)

    payload = catalog_query(project, name="GER_sample_desc", tag="focus/GER_sample")

    assert payload["filters"] == {"name": "GER_sample_desc", "tag": "focus/GER_sample"}
    assert payload["count"] == 1
    assert payload["rows"][0]["target_entity"] == "hoi4-loc-entry"
    assert payload["rows"][0]["name"] == "GER_sample_desc"

    database = project_root / ".paradev/.cache/hb/catalog.sqlite"
    with sqlite3.connect(database) as connection:
        connection.execute("update sys_catalog set name = ? where name = ?", ("ÄGER_sample_desc", "GER_sample_desc"))

    payload = catalog_query(project, name="äger_SAMPLE", tag="focus/GER_sample", include_data=False)

    assert payload["count"] == 1
    assert payload["rows"][0]["name"] == "ÄGER_sample_desc"


def test_hb_catalog_query_pages_filtered_rows_without_data(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)

    first_page = catalog_query(project, entity="pdx-symbol", limit=2, include_data=False)

    assert first_page["filters"] == {
        "entity": "hoi4-pdx-symbol",
        "limit": 2,
        "include_data": False,
    }
    assert first_page["filtered_count"] == 3
    assert first_page["count"] == 2
    assert first_page["page"] == {"offset": 0, "limit": 2, "has_more": True, "next_offset": 2}
    assert [row["name"] for row in first_page["rows"]] == ["focus", "focus/cost"]

    payload = catalog_query(project, entity="pdx-symbol", limit=2, offset=2, include_data=False)

    assert payload["filters"] == {
        "entity": "hoi4-pdx-symbol",
        "limit": 2,
        "offset": 2,
        "include_data": False,
    }
    assert payload["total_count"] == 37
    assert payload["filtered_count"] == 3
    assert payload["count"] == 1
    assert payload["data_included"] is False
    assert payload["page"] == {"offset": 2, "limit": 2, "has_more": False, "next_offset": None}
    assert [row["name"] for row in payload["rows"]] == ["focus/id"]
    assert all("data" not in row for row in payload["rows"])

    empty_page = catalog_query(project, entity="pdx-symbol", limit=2, offset=10, include_data=False)

    assert empty_page["count"] == 0
    assert empty_page["page"] == {"offset": 10, "limit": 2, "has_more": False, "next_offset": None}


def test_hb_catalog_query_filters_by_exact_target_id(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)
    target_id = catalog_query(project, entity="pdx-symbol")["rows"][1]["target_id"]

    payload = catalog_query(project, target_id=target_id, include_data=False)

    assert payload["filters"] == {"target_id": target_id, "include_data": False}
    assert payload["filtered_count"] == 1
    assert payload["count"] == 1
    assert payload["rows"][0]["target_id"] == target_id


def test_hb_catalog_query_hydrates_only_returned_page(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)
    catalog_write(project)
    hydrated: list[str] = []

    def fake_catalog_target_data(connection: sqlite3.Connection, row: sqlite3.Row) -> dict[str, object]:
        del connection
        hydrated.append(str(row["target_id"]))
        return {"hydrated": True}

    monkeypatch.setattr("paradev.hb._catalog_target_data", fake_catalog_target_data)

    payload = catalog_query(project, entity="pdx-symbol", limit=1, offset=1)

    assert payload["count"] == 1
    assert payload["rows"][0]["data"] == {"hydrated": True}
    hydrated_target_id = payload["rows"][0]["target_id"]
    assert hydrated == [hydrated_target_id]

    payload = catalog_query(project, entity="pdx-symbol", limit=1, include_data=False)

    assert payload["count"] == 1
    assert "data" not in payload["rows"][0]
    assert hydrated == [hydrated_target_id]


@pytest.mark.parametrize(
    ("filters", "message"),
    [
        ({"limit": 0}, "limit must be a positive integer"),
        ({"limit": True}, "limit must be a positive integer"),
        ({"offset": -1}, "offset must be a non-negative integer"),
        ({"offset": True}, "offset must be a non-negative integer"),
        ({"include_data": 1}, "include_data must be a boolean"),
    ],
)
def test_hb_catalog_query_rejects_invalid_paging_filters(
    tmp_path: Path,
    filters: dict[str, object],
    message: str,
) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    project = Project.load(project_root)

    with pytest.raises(ValueError, match=message):
        catalog_query(project, **filters)  # type: ignore[arg-type]


def test_hb_catalog_query_cli_outputs_json(tmp_path: Path) -> None:
    project_root = tmp_path / "minimal"
    copy_dir(PROJECT_ROOT, project_root)
    catalog_write(Project.load(project_root))

    result = CliRunner().invoke(
        build_app(),
        ["hb", "catalog-query", str(project_root), "--entity", "pdx-symbol", "--json"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "paradev.hb.catalog-query.v1"
    assert payload["count"] == 3
    assert payload["filters"] == {
        "entity": "hoi4-pdx-symbol",
        "limit": 100,
        "include_data": False,
    }


def test_hb_catalog_query_cli_uses_sdk_inspection_dispatcher(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeProject:
        def inspect(self, kind: str, **filters: object) -> dict[str, object]:
            assert kind == "catalog-query"
            assert filters == {
                "database": "catalog.sqlite",
                "entity": "source-file",
                "target_id": None,
                "name": None,
                "tag": "loader:pdx",
                "limit": 3,
                "offset": 0,
                "include_data": False,
            }
            return {"schema": "fake.catalog-query", "rows": []}

    def fake_open_project(path: str) -> FakeProject:
        assert path == "demo"
        return FakeProject()

    monkeypatch.setattr("paradev.cli.open_project", fake_open_project)

    result = CliRunner().invoke(
        build_app(),
        [
            "hb",
            "catalog-query",
            "demo",
            "--database",
            "catalog.sqlite",
            "--entity",
            "source-file",
            "--tag",
            "loader:pdx",
            "--limit",
            "3",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == {"schema": "fake.catalog-query", "rows": []}
