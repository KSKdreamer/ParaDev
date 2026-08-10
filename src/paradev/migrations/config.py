"""Migrate pre-0.1.1.6 HeavenBase config layers into its Registry store."""

from __future__ import annotations

import heavenbase as hb
from heavenbase.utils import Mapping, exists_file, loads_json, path_to_file_uri, pj, to_mutable_data

import sqlite3

_LEGACY_CONFIG_TABLE = "hb_config_layers"
_MIGRATION_REGISTRY = "paradev-migrations"
_MIGRATION_KEY = "heavenbase-0.1.1.6-config"
_REGISTRY_WRITE_ATTEMPTS = 5
_LEGACY_CONFIG_QUERY = """
SELECT scope, ver, pkg_ver, gen, data, created_at
FROM hb_config_layers
WHERE pkg = ?
ORDER BY scope, ver, id
"""


def migrate_legacy_config_layers(root: str, context: hb.Context) -> None:
    """Copy retained ParaDev config layers into a Context-owned Registry.

    The legacy SQLite table is read in one snapshot and is never changed.
    Missing scopes are created as Registry records before a marker is written
    in a separate migration namespace. The marker is always written last, so
    restarts can safely finish an interrupted migration without resurrecting
    scopes that users remove after migration completes.

    Args:
        root (str): Absolute ParaDev state root containing `config.db`.
        context (hb.Context): Context that owns the persistent Registries.

    Returns:
        None: The function returns after migration is complete or unnecessary.

    Raises:
        TypeError: If a legacy JSON layer is not an object.
        ValueError: If a legacy row is malformed or has duplicate versions.
        RuntimeError: If concurrent Registry writes exhaust bounded retries.
    """

    if not exists_file(pj(root, "config.db", abs=True)):
        return
    migrations = context.registry(_MIGRATION_REGISTRY)
    if _MIGRATION_KEY in migrations:
        return
    records = _legacy_config_records(root)
    if records is None:
        return
    registry = context.registry("system-config")
    for scope, record in records.items():
        _create_registry_item(registry, scope, record)
    _create_registry_item(
        migrations,
        _MIGRATION_KEY,
        {
            "schema": "paradev.config-migration.v1",
            "source": _LEGACY_CONFIG_TABLE,
            "scopes": list(records),
        },
    )


def _create_registry_item(registry: hb.Registry, key: str, value: object) -> None:
    conflict: hb.RegistryConflictError | None = None
    for _attempt in range(_REGISTRY_WRITE_ATTEMPTS):
        if key in registry:
            return
        try:
            registry.create(key, value)
            return
        except hb.RegistryConflictError as error:
            conflict = error
            registry.refresh()
        except ValueError:
            if key in registry:
                return
            raise
    if key in registry:
        return
    raise RuntimeError(f"Could not persist Registry item {key!r} after concurrent writes") from conflict


def _legacy_config_records(root: str) -> dict[str, dict[str, object]] | None:
    database = pj(root, "config.db", abs=True)
    if not exists_file(database):
        return None
    uri = f"{path_to_file_uri(database)}?mode=ro"
    with sqlite3.connect(uri, uri=True) as connection:
        connection.execute("BEGIN")
        table = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (_LEGACY_CONFIG_TABLE,),
        ).fetchone()
        if table is None:
            return None
        rows = connection.execute(_LEGACY_CONFIG_QUERY, ("paradev",)).fetchall()

    records: dict[str, dict[str, object]] = {}
    versions_by_scope: dict[str, set[int]] = {}
    for raw_scope, raw_version, package_version, raw_generation, raw_data, created_at in rows:
        scope = _legacy_scope(raw_scope)
        version = _legacy_integer(raw_version, "version", minimum=1)
        generation = _legacy_integer(raw_generation, "generation", minimum=0)
        if package_version is not None and not isinstance(package_version, str):
            raise TypeError(f"Legacy config package version for {scope!r} must be text or null")
        if not isinstance(created_at, str) or not created_at.strip():
            raise ValueError(f"Legacy config timestamp for {scope!r} version {version} must be non-empty text")
        data = _legacy_data(raw_data, scope, version)
        seen = versions_by_scope.setdefault(scope, set())
        if version in seen:
            raise ValueError(f"Legacy config scope {scope!r} has duplicate version {version}")
        seen.add(version)
        record = records.get(scope)
        if record is None:
            record = {"scope": scope, "generation": 0, "versions": []}
            records[scope] = record
        record["generation"] = max(int(record["generation"]), generation)
        versions = record["versions"]
        if not isinstance(versions, list):
            raise RuntimeError(f"Invalid migration record for scope {scope!r}")
        versions.append(
            {
                "version": version,
                "package_version": package_version,
                "data": data,
                "created_at": created_at,
            }
        )
    return records


def _legacy_scope(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Legacy config scope must be non-empty text")
    scope = value.strip().lower()
    if value != scope:
        raise ValueError(f"Legacy config scope must be canonical lowercase text, got {value!r}")
    return scope


def _legacy_integer(value: object, name: str, *, minimum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ValueError(f"Legacy config {name} must be an integer >= {minimum}, got {value!r}")
    return value


def _legacy_data(value: object, scope: str, version: int) -> dict[str, object]:
    if not isinstance(value, str):
        raise TypeError(f"Legacy config JSON for {scope!r} version {version} must be text")
    try:
        data = loads_json(value)
    except Exception as error:
        raise ValueError(f"Invalid legacy config JSON for {scope!r} version {version}: {error}") from error
    if not isinstance(data, Mapping):
        raise TypeError(f"Legacy config JSON object required for {scope!r} version {version}")
    return to_mutable_data(data)
