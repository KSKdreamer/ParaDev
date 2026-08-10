"""ParaDev configuration surface backed by HeavenBase utilities."""

from __future__ import annotations

from .migrations.config import migrate_legacy_config_layers

import heavenbase as hb
from heavenbase.context import load_bootstrap
from heavenbase.utils import ConfigManager, ConfigSnapshot, InterpolationPolicy, deepcopy, dflat, dget, dmerge, pj
from heavenbase.utils.config.api import ConfigOps

import os

DEFAULT_CONFIG = {
    "paradev": {
        "project": {
            "name": "ParaDev",
        },
        "cli": {
            "output": "yaml",
        },
        "build": {
            "parallelism": 1,
            "strict_metadata": False,
        },
        "desktop": {
            "thumbnail_cache": {
                "max_kb": 256,
            },
        },
        "hoi4": {
            "launch_mode": "steam",
            "game_root": "",
        },
        "ai": {
            "preset": "chat",
            "provider": "deepseek",
            "gateway": "openai",
            "model": "deepseek-v4-flash",
            "key_env": "DEEPSEEK_API_KEY",
            "base_url": "",
            "chat": {
                "default_role": "chat",
            },
        },
    },
}

_MISSING = object()


def _heavenbase_system_defaults() -> dict[str, object]:
    """Return the hidden HeavenBase policy needed by ParaDev-owned backends."""

    heavenbase_defaults = ConfigManager(package="heavenbase", setup=False).load_default()
    return {
        "heavenbase": {
            "db": deepcopy(dget(heavenbase_defaults, "heavenbase.db", default={})),
        },
    }


class _ParaDevConfigManager(ConfigManager):
    """Keep backend construction policy out of ParaDev's user config surface."""

    def __init__(
        self,
        *,
        root: str,
        default: dict[str, object],
        system_defaults: dict[str, object],
    ) -> None:
        self._system_defaults = deepcopy(system_defaults)
        super().__init__(
            package="paradev",
            scope="paradev",
            root=root,
            default=default,
            keep_last_k=10,
            setup=True,
        )

    def snapshot(
        self,
        overrides: dict[str, object] | None = None,
        policy: InterpolationPolicy | None = None,
        refresh: bool = False,
    ) -> ConfigSnapshot:
        visible = super().snapshot(overrides=overrides, policy=policy, refresh=refresh)
        return ConfigSnapshot(
            dmerge([deepcopy(self._system_defaults), visible.to_dict()]),
            visible.gen,
            visible.policy,
        )

    def load(self, refresh: bool = False) -> dict[str, object]:
        """Return only user-facing ParaDev configuration."""

        return ConfigManager.snapshot(self, refresh=refresh).to_dict()

    def get(self, path: str | None = None, default: object = None) -> object:
        """Read hidden system defaults only through internal manager calls."""

        if self._opening_registry:
            merged = dmerge([deepcopy(self._system_defaults), deepcopy(self.default)])
            return deepcopy(dget(merged, path, default)) if path else merged
        return super().get(path, default)


def _config_root(root: str | None = None) -> str:
    selected = root or os.environ.get("PARADEV_ROOT")
    return pj(selected, abs=True) if selected else pj("~", ".paradev", abs=True)


def _bootstrap_config(root: str) -> dict[str, object]:
    packaged = load_bootstrap(home_path=pj(root, ".paradev-packaged-bootstrap.yaml"))
    backend = deepcopy(packaged.backend)
    backend.update(
        {
            "name": "paradev-config",
            "database": "file://%/config.db",
        }
    )
    return {
        "version": 1,
        "root": root,
        "workspace": "paradev",
        "backend": backend,
        "registry": deepcopy(packaged.registry),
    }


def _create_config_runtime(root: str | None = None) -> tuple[hb.Context, ConfigManager]:
    config_root = _config_root(root)
    manager = _ParaDevConfigManager(
        root=config_root,
        default=DEFAULT_CONFIG,
        system_defaults=_heavenbase_system_defaults(),
    )
    context = hb.Context.load(_bootstrap_config(config_root), config=manager)
    manager._bind_registry_factory(lambda: _open_config_registry(config_root, context))
    return context, manager


def _open_config_registry(root: str, context: hb.Context) -> hb.Registry:
    """Open and migrate the persistent config Registry on first config use."""

    try:
        registry = context.registry("system-config")
        migrate_legacy_config_layers(root, context)
    except Exception:
        context.close()
        raise
    return registry


BOOTSTRAP_CONFIG = _bootstrap_config(_config_root())
_CONTEXT_PARADEV, CM_PARADEV = _create_config_runtime()
_CONFIG_OPS = ConfigOps(CM_PARADEV)


def config_get(key: str | None = None, *, scope: str | None = None, merged: bool = True) -> object:
    """Read one ParaDev config key or the whole config payload.

    Args:
        key: Optional dotted config key such as `paradev.project.name`.
        scope: Optional ConfigManager scope. Defaults to the active ParaDev
            scope.
        merged: Whether to read merged defaults plus stored scope values.

    Returns:
        JSON-safe config value or config mapping.
    """

    value = _CONFIG_OPS.get(key=key, scope=scope, merged=merged)
    if merged and key and value is None:
        default = dget(DEFAULT_CONFIG, key, default=_MISSING)
        if default is not _MISSING:
            return default
    return value


def config_list(prefix: str | None = None, *, scope: str | None = None, merged: bool = True) -> list[dict[str, object]]:
    """List flattened ParaDev config rows.

    Args:
        prefix: Optional dotted-key prefix filter.
        scope: Optional ConfigManager scope. Defaults to the active ParaDev
            scope.
        merged: Whether to include merged defaults in the row list.

    Returns:
        JSON-safe flattened rows with `key` and `value` fields.
    """

    rows = _CONFIG_OPS.list(prefix=prefix, scope=scope, merged=merged)
    if not merged:
        return rows
    row_by_key = {str(row["key"]): row for row in rows}
    for key, value in dflat(DEFAULT_CONFIG):
        if prefix and not key.startswith(prefix):
            continue
        row_by_key.setdefault(key, {"key": key, "value": value})
    return list(row_by_key.values())


def config_set(key: str, value: object, *, scope: str | None = None, parse: str = "auto") -> bool:
    """Set one ParaDev config key through the shared ConfigManager.

    Args:
        key: Dotted config key to write.
        value: Raw or parsed config value.
        scope: Optional ConfigManager scope. Defaults to the active ParaDev
            scope.
        parse: Value parser used by HeavenBase config helpers: `auto`, `json`,
            or `raw`.

    Returns:
        Whether the value was written.
    """

    return _CONFIG_OPS.set(key, value, scope=scope, parse=parse)


def config_unset(key: str, *, scope: str | None = None) -> bool:
    """Unset one ParaDev config key through the shared ConfigManager.

    Args:
        key: Dotted config key to remove from the selected scope.
        scope: Optional ConfigManager scope. Defaults to the active ParaDev
            scope.

    Returns:
        Whether the value was removed.
    """

    return _CONFIG_OPS.unset(key, scope=scope)


def config_scopes() -> object:
    """List stored ParaDev config scopes.

    Returns:
        JSON-safe scope listing from `CM_PARADEV`.
    """

    return CM_PARADEV.scopes()


def config_history(*, scope: str | None = None, limit: int = 10) -> object:
    """List ParaDev config history rows for one scope.

    Args:
        scope: Optional ConfigManager scope. Defaults to the active ParaDev
            scope.
        limit: Maximum history row count.

    Returns:
        JSON-safe history rows from `CM_PARADEV`.
    """

    return CM_PARADEV.history(scope=_resolve_config_scope(scope), limit=limit)


def _resolve_config_scope(scope: str | None) -> str:
    if not scope:
        return CM_PARADEV.scope
    value = scope.strip().lower()
    if value == ".":
        return CM_PARADEV.base_scope
    if value == CM_PARADEV.base_scope or value.startswith(f"{CM_PARADEV.base_scope}."):
        return value
    return f"{CM_PARADEV.base_scope}.{value}"


from .config_api import (  # noqa: E402
    CONFIG_API_TABLE_SCHEMA,
    ConfigApiRow,
    ConfigApiTable,
    get_config_api_selection,
    get_config_api_table,
    render_config_api_reference_markdown,
)

__all__ = [
    "DEFAULT_CONFIG",
    "BOOTSTRAP_CONFIG",
    "CM_PARADEV",
    "config_get",
    "config_list",
    "config_set",
    "config_unset",
    "config_scopes",
    "config_history",
    "CONFIG_API_TABLE_SCHEMA",
    "ConfigApiRow",
    "ConfigApiTable",
    "get_config_api_selection",
    "get_config_api_table",
    "render_config_api_reference_markdown",
]
