from __future__ import annotations

import sqlite3
import sys
from os import PathLike, environ

import pytest
from heavenbase.utils import cmd, exists_file, exists_path, load_bin, pj, touch_dir

from paradev.config import DEFAULT_CONFIG, _create_config_runtime
from paradev.migrations.config import _create_registry_item

_LEGACY_SCHEMA = """
CREATE TABLE hb_config_layers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pkg TEXT NOT NULL,
    scope TEXT NOT NULL,
    ver INTEGER NOT NULL,
    pkg_ver TEXT,
    gen INTEGER NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def _write_legacy_rows(root: str | PathLike[str], rows: list[tuple[object, ...]]) -> None:
    touch_dir(root)
    with sqlite3.connect(pj(root, "config.db")) as connection:
        connection.execute(_LEGACY_SCHEMA)
        connection.executemany(
            """
            INSERT INTO hb_config_layers (pkg, scope, ver, pkg_ver, gen, data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )


def _legacy_rows(root: str | PathLike[str]) -> list[tuple[object, ...]]:
    with sqlite3.connect(pj(root, "config.db")) as connection:
        return list(connection.execute("""
                SELECT pkg, scope, ver, pkg_ver, gen, data, created_at
                FROM hb_config_layers
                ORDER BY id
                """))


def _isolated_config_read_script(root: str | PathLike[str]) -> str:
    return "\n".join(
        [
            "from heavenbase import DEFAULT_CONTEXT",
            "from heavenbase.backends.inmem.backend import InMemBackend",
            "from heavenbase.utils import CM_HVNB",
            f"CM_HVNB.root = {str(root)!r}",
            'DEFAULT_CONTEXT._backend = InMemBackend("system", ws_id="default")',
            "DEFAULT_CONTEXT._owns_backend = False",
            "DEFAULT_CONTEXT._registries.clear()",
            "CM_HVNB._registry = None",
            "CM_HVNB._setup_pending = True",
            'CM_HVNB._bind_registry_factory(lambda: DEFAULT_CONTEXT.registry("system-config"))',
            "CM_HVNB._clear_caches()",
            "CM_HVNB.setup(reset=True)",
            "import paradev",
            "paradev.CM_PARADEV.get('paradev.project.name')",
        ]
    )


def test_legacy_config_migration_preserves_layers_history_and_source_rows(tmp_path: PathLike[str]) -> None:
    rows = [
        (
            "paradev",
            "paradev",
            1,
            "0.0.9",
            4,
            '{"paradev":{"project":{"name":"Legacy"},"test":{"obsolete":true}}}',
            "2026-01-01T00:00:00+00:00",
        ),
        (
            "paradev",
            "paradev",
            2,
            "0.1.0",
            7,
            '{"paradev":{"project":{"name":"PIHC3"},"test":{"obsolete":{"__HB_REMOVE__":true}}}}',
            "2026-02-01T00:00:00+00:00",
        ),
        (
            "paradev",
            "paradev.novice",
            1,
            None,
            3,
            '{"paradev":{"build":{"strict_metadata":true}}}',
            "2026-03-01T00:00:00+00:00",
        ),
        (
            "another-package",
            "another-package",
            1,
            None,
            1,
            '{"untouched":true}',
            "2026-04-01T00:00:00+00:00",
        ),
    ]
    _write_legacy_rows(tmp_path, rows)

    context, manager = _create_config_runtime(str(tmp_path))
    try:
        assert manager.scopes() == ["paradev", "paradev.novice"]
        assert manager.layer("paradev", version=1) == {"paradev": {"project": {"name": "Legacy"}, "test": {"obsolete": True}}}
        assert manager.layer("paradev", version=2) == {
            "paradev": {
                "project": {"name": "PIHC3"},
                "test": {"obsolete": {"__HB_REMOVE__": True}},
            }
        }
        assert manager.get("paradev.project.name") == "PIHC3"
        assert manager.get("paradev.test.obsolete", default="missing") == "missing"
        assert manager.layer("paradev.novice") == {"paradev": {"build": {"strict_metadata": True}}}
        assert manager.history("paradev", limit=10) == [
            {
                "pkg": "paradev",
                "scope": "paradev",
                "ver": 2,
                "pkg_ver": "0.1.0",
                "gen": 7,
                "data": {
                    "paradev": {
                        "project": {"name": "PIHC3"},
                        "test": {"obsolete": {"__HB_REMOVE__": True}},
                    }
                },
                "created_at": "2026-02-01T00:00:00+00:00",
            },
            {
                "pkg": "paradev",
                "scope": "paradev",
                "ver": 1,
                "pkg_ver": "0.0.9",
                "gen": 7,
                "data": {
                    "paradev": {
                        "project": {"name": "Legacy"},
                        "test": {"obsolete": True},
                    }
                },
                "created_at": "2026-01-01T00:00:00+00:00",
            },
        ]
        manager.set("paradev.project.name", "Post migration")
        newest = manager.history("paradev", limit=1)[0]
        assert newest["ver"] == 3
        assert newest["gen"] == 8
        assert newest["pkg_ver"] == manager.package_version
        assert manager.layer("paradev", version=1)["paradev"]["project"]["name"] == "Legacy"
        assert manager.layer("paradev", version=2)["paradev"]["project"]["name"] == "PIHC3"
    finally:
        context.close()

    assert _legacy_rows(tmp_path) == rows

    reopened_context, reopened = _create_config_runtime(str(tmp_path))
    try:
        assert reopened.get("paradev.project.name") == "Post migration"
        assert [row["ver"] for row in reopened.history("paradev", limit=10)] == [3, 2, 1]
    finally:
        reopened_context.close()
    assert _legacy_rows(tmp_path) == rows


def test_fresh_config_runtime_persists_values_across_reopen(tmp_path: PathLike[str]) -> None:
    root = pj(tmp_path, "fresh")
    context, manager = _create_config_runtime(str(root))
    try:
        assert not exists_path(root)
        assert manager.load() == DEFAULT_CONFIG
        assert exists_file(pj(root, "config.db"))
        manager.set("paradev.project.name", "Persistent PIHC3")
    finally:
        context.close()

    reopened_context, reopened = _create_config_runtime(str(root))
    try:
        assert reopened.get("paradev.project.name") == "Persistent PIHC3"
    finally:
        reopened_context.close()


def test_import_is_lazy_until_config_is_read(tmp_path: PathLike[str]) -> None:
    root = pj(tmp_path, "import-root")
    environment = {**environ, "PARADEV_ROOT": str(root)}

    cmd([sys.executable, "-c", "import paradev"], env=environment, check=True)

    assert not exists_path(pj(root, "config.db"))

    cmd(
        [
            sys.executable,
            "-c",
            _isolated_config_read_script(pj(tmp_path, "heavenbase-child")),
        ],
        env=environment,
        check=True,
    )

    assert exists_file(pj(root, "config.db"))


@pytest.mark.parametrize("database_kind", ["empty", "current"])
def test_import_does_not_open_or_mutate_existing_database(tmp_path: PathLike[str], database_kind: str) -> None:
    root = pj(tmp_path, database_kind)
    touch_dir(root)
    database = pj(root, "config.db")
    if database_kind == "empty":
        with sqlite3.connect(database):
            pass
    else:
        context, manager = _create_config_runtime(str(root))
        try:
            manager.load()
        finally:
            context.close()
    before = load_bin(database, strict=True)
    environment = {**environ, "PARADEV_ROOT": str(root)}

    cmd([sys.executable, "-c", "import paradev"], env=environment, check=True)

    assert load_bin(database, strict=True) == before


def test_legacy_config_migration_does_not_overwrite_existing_scope(tmp_path: PathLike[str]) -> None:
    context, manager = _create_config_runtime(str(tmp_path))
    try:
        manager.set("paradev.project.name", "New Registry Wins")
    finally:
        context.close()
    rows = [
        (
            "paradev",
            "paradev",
            1,
            "0.0.9",
            1,
            '{"paradev":{"project":{"name":"Legacy Must Not Win"}}}',
            "2026-01-01T00:00:00+00:00",
        ),
        (
            "paradev",
            "paradev.profile",
            1,
            "0.0.9",
            1,
            '{"paradev":{"build":{"parallelism":2}}}',
            "2026-01-02T00:00:00+00:00",
        ),
    ]
    _write_legacy_rows(tmp_path, rows)

    reopened_context, reopened = _create_config_runtime(str(tmp_path))
    try:
        assert reopened.get("paradev.project.name") == "New Registry Wins"
        assert reopened.layer("paradev.profile") == {"paradev": {"build": {"parallelism": 2}}}
    finally:
        reopened_context.close()
    assert _legacy_rows(tmp_path) == rows


def test_legacy_config_migration_marker_prevents_scope_resurrection(tmp_path: PathLike[str]) -> None:
    rows = [
        (
            "paradev",
            "paradev.novice",
            1,
            "0.0.9",
            1,
            '{"paradev":{"build":{"strict_metadata":true}}}',
            "2026-01-01T00:00:00+00:00",
        )
    ]
    _write_legacy_rows(tmp_path, rows)
    context, manager = _create_config_runtime(str(tmp_path))
    try:
        assert "paradev.novice" in manager.scopes()
        assert manager.remove("paradev.novice") is True
    finally:
        context.close()

    reopened_context, reopened = _create_config_runtime(str(tmp_path))
    try:
        assert "paradev.novice" not in reopened.scopes()
    finally:
        reopened_context.close()
    assert _legacy_rows(tmp_path) == rows


def test_config_migration_registry_write_retries_after_unrelated_cas_conflict(tmp_path: PathLike[str]) -> None:
    first_context, first_manager = _create_config_runtime(str(tmp_path))
    first_manager.load()
    second_context, _second_manager = _create_config_runtime(str(tmp_path))
    try:
        first_registry = first_context.registry("system-config")
        second_registry = second_context.registry("system-config")
        second_registry.create(
            "paradev.other",
            {"scope": "paradev.other", "generation": 1, "versions": []},
        )

        _create_registry_item(
            first_registry,
            "paradev.target",
            {"scope": "paradev.target", "generation": 1, "versions": []},
        )

        assert "paradev.other" in first_registry
        assert "paradev.target" in first_registry
    finally:
        second_context.close()
        first_context.close()


@pytest.mark.parametrize(
    ("scope", "version", "generation", "data", "message"),
    [
        ("", 1, 1, "{}", "scope"),
        ("paradev", 0, 1, "{}", "version"),
        ("paradev", 1, -1, "{}", "generation"),
        ("paradev", 1, 1, "[]", "JSON object"),
        ("paradev", 1, 1, "{broken", "JSON"),
    ],
)
def test_legacy_config_migration_rejects_malformed_rows_before_writing_registry(
    tmp_path: PathLike[str],
    scope: str,
    version: int,
    generation: int,
    data: str,
    message: str,
) -> None:
    rows = [
        (
            "paradev",
            scope,
            version,
            "0.0.9",
            generation,
            data,
            "2026-01-01T00:00:00+00:00",
        )
    ]
    _write_legacy_rows(tmp_path, rows)

    context, manager = _create_config_runtime(str(tmp_path))
    try:
        with pytest.raises((TypeError, ValueError), match=message):
            manager.load()
    finally:
        context.close()

    assert _legacy_rows(tmp_path) == rows
    with sqlite3.connect(pj(tmp_path, "config.db")) as connection:
        count = connection.execute("SELECT COUNT(*) FROM sys_registry_state").fetchone()[0]
    assert count == 0


def test_legacy_config_migration_rejects_duplicate_scope_versions(tmp_path: PathLike[str]) -> None:
    rows = [
        ("paradev", "paradev", 1, None, 1, "{}", "2026-01-01T00:00:00+00:00"),
        ("paradev", "paradev", 1, None, 2, "{}", "2026-01-02T00:00:00+00:00"),
    ]
    _write_legacy_rows(tmp_path, rows)

    context, manager = _create_config_runtime(str(tmp_path))
    try:
        with pytest.raises(ValueError, match="duplicate version"):
            manager.load()
    finally:
        context.close()

    assert _legacy_rows(tmp_path) == rows


def test_legacy_config_migration_rejects_blank_timestamp(tmp_path: PathLike[str]) -> None:
    rows = [("paradev", "paradev", 1, None, 1, "{}", " ")]
    _write_legacy_rows(tmp_path, rows)

    context, manager = _create_config_runtime(str(tmp_path))
    try:
        with pytest.raises(ValueError, match="timestamp"):
            manager.load()
    finally:
        context.close()

    assert _legacy_rows(tmp_path) == rows
