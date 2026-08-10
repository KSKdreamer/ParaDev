"""Local desktop operations shared by Python services and tests."""

from __future__ import annotations

import base64
import math
import os
import platform
import shutil
import stat
import subprocess
import tempfile
import time
import unicodedata
import zlib
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from heavenbase.utils import dget, dump_json, dumps_json, load_json, load_txt, touch_dir

from paradev.config import CM_PARADEV, DEFAULT_CONFIG

if TYPE_CHECKING:
    from paradev.sdk.project import Project

_MISSING = object()


def _default_config_value(key: str) -> object:
    value = dget(DEFAULT_CONFIG, key, default=_MISSING)
    if value is _MISSING:
        raise ValueError(f"Desktop config key is missing from DEFAULT_CONFIG: {key}.")
    return value


def _desktop_config_row(key: str, value_type: str, *, choices: Sequence[str] = (), minimum: int | None = None) -> dict[str, object]:
    row: dict[str, object] = {
        "key": key,
        "default": _default_config_value(key),
        "valueType": value_type,
    }
    if choices:
        row["choices"] = list(choices)
    if minimum is not None:
        row["minimum"] = minimum
    return row


BINARY_SOURCE_SCHEMA = "paradev.desktop.binary-source.v1"
AI_CHAT_SCHEMA = "paradev.desktop.ai-chat.v1"
_AI_CHAT_PROPOSAL_SCHEMA = "paradev.desktop.ai-chat-proposal.v1"
AI_CHAT_PROFILES_SCHEMA = "paradev.desktop.ai-chat-profiles.v1"
AI_CHAT_PROFILES_CONFIG_KEY = "paradev.ai.chat.profiles"
AI_CHAT_PROFILES_CONFIG_SCHEMA = "paradev.sdk.ai-chat-profile-overrides.v1"
CONFIG_VALUE_SCHEMA = "paradev.desktop.config-value.v1"
DEPENDENCY_SCHEMA = "paradev.desktop.dependency.v1"
DESKTOP_APP_CONFIG_KEY = "paradev.desktop.gui"
LLM_TEST_SCHEMA = "paradev.desktop.llm-test.v1"
_DEFAULT_AI_CHAT_MAX_TOKENS = 1_024
_CREATE_MODULE_AI_CHAT_MAX_TOKENS = 32_768
_MAX_AI_CHAT_PROPOSAL_MODULES = 256
_MAX_AI_CHAT_SOURCE_UPDATE_CONTROLS = 512
_MAX_AI_CHAT_SOURCE_UPDATE_FILES = 16
_MAX_SAFE_JSON_INTEGER = 9_007_199_254_740_991
MAX_AI_CHAT_SOURCE_CHARS = 24_000
MAX_PROJECT_BROWSER_CACHE_BYTES = 128 * 1024 * 1024
MAX_TEXT_SOURCE_BYTES = 2 * 1024 * 1024
PROJECT_BROWSER_SCHEMA = "paradev.sdk.project-browser.v1"
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
DESKTOP_CONFIG_ROWS: tuple[dict[str, object], ...] = (
    _desktop_config_row("paradev.project.name", "text"),
    _desktop_config_row("paradev.cli.output", "choice", choices=("yaml", "json")),
    _desktop_config_row("paradev.build.parallelism", "positive_int", minimum=1),
    _desktop_config_row("paradev.build.strict_metadata", "boolean"),
    _desktop_config_row("paradev.desktop.thumbnail_cache.max_kb", "positive_int", minimum=1),
    _desktop_config_row("paradev.hoi4.launch_mode", "choice", choices=("steam", "local")),
    _desktop_config_row("paradev.hoi4.game_root", "optional_text"),
    _desktop_config_row("paradev.ai.preset", "choice", choices=("system", "chat", "reason", "coder")),
    _desktop_config_row("paradev.ai.provider", "text"),
    _desktop_config_row("paradev.ai.gateway", "text"),
    _desktop_config_row("paradev.ai.model", "text"),
    _desktop_config_row("paradev.ai.key_env", "text"),
    _desktop_config_row("paradev.ai.base_url", "optional_text"),
    _desktop_config_row("paradev.ai.chat.default_role", "chat_profile"),
)
DESKTOP_CONFIG_KEYS: tuple[str, ...] = tuple(str(row["key"]) for row in DESKTOP_CONFIG_ROWS)
DESKTOP_CONFIG_DEFAULTS: Mapping[str, object] = {str(row["key"]): row["default"] for row in DESKTOP_CONFIG_ROWS}
DESKTOP_CONFIG_ROW_BY_KEY: Mapping[str, Mapping[str, object]] = {str(row["key"]): row for row in DESKTOP_CONFIG_ROWS}
DEFAULT_THUMBNAIL_CACHE_MAX_KB = int(DESKTOP_CONFIG_DEFAULTS["paradev.desktop.thumbnail_cache.max_kb"])
AI_PRESET_CONFIG_VALUES = set(str(value) for value in DESKTOP_CONFIG_ROW_BY_KEY["paradev.ai.preset"].get("choices", ()))
AI_CHAT_SOURCE_KIND_ROWS: tuple[dict[str, object], ...] = (
    {
        "id": "project",
        "labelKey": "config.models.sourceKind.project",
        "label": "Project",
        "frontendKinds": ["workspace"],
    },
    {
        "id": "selection",
        "labelKey": "config.models.sourceKind.selection",
        "label": "Selection",
        "frontendKinds": ["source"],
    },
    {
        "id": "diagnostics",
        "labelKey": "config.models.sourceKind.diagnostics",
        "label": "Diagnostics",
        "frontendKinds": ["diagnostics"],
    },
    {
        "id": "templates",
        "labelKey": "config.models.sourceKind.templates",
        "label": "Templates",
        "frontendKinds": ["templates"],
    },
)
AI_CHAT_SOURCE_KIND_VALUES: tuple[str, ...] = tuple(str(row["id"]) for row in AI_CHAT_SOURCE_KIND_ROWS)
AI_CHAT_SOURCE_KIND_FRONTEND_KINDS: Mapping[str, list[str]] = {str(row["id"]): [str(kind) for kind in row["frontendKinds"]] for row in AI_CHAT_SOURCE_KIND_ROWS}
HOI4_LAUNCH_MODE_CONFIG_VALUES = set(str(value) for value in DESKTOP_CONFIG_ROW_BY_KEY["paradev.hoi4.launch_mode"].get("choices", ()))
AI_CHAT_PROFILE_ROWS: tuple[dict[str, object], ...] = (
    {
        "id": "chat",
        "labelKey": "chat.profile.chat.label",
        "label": "Chat",
        "detailKey": "chat.profile.chat.detail",
        "detail": "General ParaDev and HoI4 modding help.",
        "promptKey": "chat.profile.chat.prompt",
        "prompt": "You are ParaDev AI. Help a Hearts of Iron IV modder use ParaDev. Keep answers practical, concise, and grounded in the Python SDK when actions are needed.",
        "sourceKinds": ["project"],
    },
    {
        "id": "explain",
        "labelKey": "chat.profile.explain.label",
        "label": "Explain HoI4 code",
        "detailKey": "chat.profile.explain.detail",
        "detail": "Explain PDX, localization, metadata, GUI, GFX, and generated artifacts.",
        "promptKey": "chat.profile.explain.prompt",
        "prompt": "Explain HoI4 code and ParaDev source files for a modder. Name the relevant file roles, likely game effect, and any SDK-backed next action.",
        "sourceKinds": ["project", "selection"],
    },
    {
        "id": "create-module",
        "labelKey": "chat.profile.createModule.label",
        "label": "Create content plan",
        "detailKey": "chat.profile.createModule.detail",
        "detail": "Plan new modules or collections through ParaDev templates before writing source files.",
        "promptKey": "chat.profile.createModule.prompt",
        "prompt": "Help create ParaDev modules and collections through the Python SDK. Choose exact authoring templates from Project.templates(), then use Project.create_modules(..., write=False) for a module batch or Project.scaffold_collection(..., write=False) for one collection. Never claim that chat created files; only an explicit reviewed apply action may write.",
        "sourceKinds": ["project", "templates"],
        "operationIds": ["module.draft", "module.create_batch", "collection.scaffold"],
    },
    {
        "id": "edit-selection",
        "labelKey": "chat.profile.editSelection.label",
        "label": "Edit selected source",
        "detailKey": "chat.profile.editSelection.detail",
        "detail": "Plan guarded edits using the selected source's Registry-owned Guided controls.",
        "promptKey": "chat.profile.editSelection.prompt",
        "prompt": "Help edit selected ParaDev module sources through Registry-owned Guided controls. Return only a dry Project.plan_source_form_updates(...) proposal; never invent paths or control ids, and never claim that chat wrote files. An explicit reviewed apply action is required.",
        "sourceKinds": ["project", "selection"],
    },
    {
        "id": "build",
        "labelKey": "chat.profile.build.label",
        "label": "Build/debug project",
        "detailKey": "chat.profile.build.detail",
        "detail": "Explain build commands, diagnostics, artifacts, and safe next actions.",
        "promptKey": "chat.profile.build.prompt",
        "prompt": "Help debug ParaDev SDK builds. Use Project.build(...) for build plans or artifact emission and desktop_project_build_command(...) or the GUI Build page for desktop compilation; explain diagnostics, artifacts, manifests, and safe next actions.",
        "sourceKinds": ["project", "diagnostics"],
        "operationIds": ["build.plan", "build.start"],
    },
)
DEFAULT_AI_CHAT_ROLE = "chat"


def desktop_config_rows() -> list[dict[str, object]]:
    """Return desktop-exposed `CM_PARADEV` config metadata rows.

    Returns:
        JSON-safe row copies used by CLI and GUI wrappers to render the
        SDK-owned config controls without mutating the desktop registry.
    """

    rows: list[dict[str, object]] = []
    for row in DESKTOP_CONFIG_ROWS:
        copied = dict(row)
        if "choices" in copied:
            copied["choices"] = list(copied["choices"])
        rows.append(copied)
    return rows


def render_desktop_typescript() -> str:
    """Render the desktop GUI TypeScript contract.

    Returns:
        Checked-in TypeScript source for the desktop shell's SDK-backed
        `CM_PARADEV` config key tuple plus open-path target catalog rows.
    """

    from .shell import OPEN_PATH_DEFAULT_TARGETS, OPEN_PATH_PLATFORM_VALUES, OPEN_PATH_TARGET_ROWS

    return "\n".join(
        [
            "/* Generated by `rtk uv run paradev desktop-api --typescript`; do not edit by hand. */",
            "",
            f"export const PARADEV_DESKTOP_CONFIG_KEYS = {dumps_json(list(DESKTOP_CONFIG_KEYS), indent=2)} as const;",
            "",
            "export type DesktopConfigKey = (typeof PARADEV_DESKTOP_CONFIG_KEYS)[number];",
            "",
            f"export const PARADEV_DESKTOP_CONFIG_ROWS = {dumps_json(desktop_config_rows(), indent=2)} as const;",
            "",
            "export type DesktopConfigRow = (typeof PARADEV_DESKTOP_CONFIG_ROWS)[number];",
            "",
            "export const PARADEV_DESKTOP_CONFIG_DEFAULTS = "
            f'{dumps_json(dict(DESKTOP_CONFIG_DEFAULTS), indent=2)} as const satisfies Record<DesktopConfigKey, DesktopConfigRow["default"]>;',
            "",
            f"export const PARADEV_DESKTOP_OPEN_PATH_PLATFORMS = {dumps_json(list(OPEN_PATH_PLATFORM_VALUES), indent=2)} as const;",
            "",
            "export type DesktopOpenPathPlatform = (typeof PARADEV_DESKTOP_OPEN_PATH_PLATFORMS)[number];",
            "",
            _render_open_path_target_rows_typescript(OPEN_PATH_TARGET_ROWS),
            "",
            'export type DesktopOpenPathTarget = (typeof PARADEV_DESKTOP_OPEN_PATH_TARGETS)[number]["id"];',
            "",
            "export const PARADEV_DESKTOP_OPEN_PATH_DEFAULT_TARGETS = "
            f"{dumps_json(dict(OPEN_PATH_DEFAULT_TARGETS), indent=2)} as const satisfies Record<DesktopOpenPathPlatform, DesktopOpenPathTarget>;",
            "",
            f"export const PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS = {dumps_json(list(AI_CHAT_SOURCE_KIND_ROWS), indent=2)} as const;",
            "",
            'export type DesktopAiChatSourceKind = (typeof PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS)[number]["id"];',
            "",
            f"export const PARADEV_DESKTOP_AI_CHAT_SOURCE_KINDS = {dumps_json(list(AI_CHAT_SOURCE_KIND_VALUES), indent=2)} as const satisfies readonly DesktopAiChatSourceKind[];",
            "",
            "export const PARADEV_DESKTOP_AI_CHAT_PROFILE_SOURCE_KIND_FRONTEND_KINDS = "
            f"{dumps_json(dict(AI_CHAT_SOURCE_KIND_FRONTEND_KINDS), indent=2)} as const satisfies Record<DesktopAiChatSourceKind, readonly string[]>;",
            "",
            f"export const PARADEV_DESKTOP_AI_CHAT_PROFILES = {dumps_json(_base_chat_profiles(), indent=2)} as const;",
            "",
            "export type DesktopAiChatProfile = (typeof PARADEV_DESKTOP_AI_CHAT_PROFILES)[number];",
            "",
        ]
    )


def _render_open_path_target_rows_typescript(rows: Sequence[Mapping[str, object]]) -> str:
    lines = ["export const PARADEV_DESKTOP_OPEN_PATH_TARGETS = ["]
    for row in rows:
        platforms = ", ".join(f'"{platform}"' for platform in row["platforms"])
        lines.extend(
            [
                "  {",
                f'    id: "{row["id"]}",',
                f'    labelKey: "{row["labelKey"]}",',
                f"    platforms: [{platforms}]",
                "  },",
            ]
        )
    lines.append("] as const;")
    return "\n".join(lines)


def desktop_source_path(project_root: str | Path, source_path: str | Path) -> Path:
    """Resolve a project-contained source path.

    Args:
        project_root: Active project root.
        source_path: Absolute or project-relative source path.

    Returns:
        Canonical source path inside the project root.

    Raises:
        ValueError: If either path is empty, missing, or outside the project.
    """

    root = _canonical_existing(project_root, "project root")
    raw_source = _required_path(source_path, "source path")
    candidate = raw_source if raw_source.is_absolute() else root / raw_source
    source = _canonical_existing(candidate, "source path")
    if not source.is_relative_to(root):
        raise ValueError("Source path is outside the active project root.")
    return source


def desktop_read_text_source(project_root: str | Path, source_path: str | Path) -> str:
    """Read one UTF-8 project source file with the desktop size limit.

    Args:
        project_root: Active project root.
        source_path: Absolute or project-relative source path.

    Returns:
        Source text.

    Raises:
        ValueError: If the source path is invalid, too large, or not a file.
        OSError: If the file cannot be decoded as UTF-8.
    """

    path = desktop_source_path(project_root, source_path)
    _require_file_under_limit(path, MAX_TEXT_SOURCE_BYTES, "Source")
    return load_txt(str(path), encoding="utf-8", strict=True)


def desktop_read_binary_source(project_root: str | Path, source_path: str | Path) -> dict[str, object]:
    """Read one project source file as a desktop binary-source payload.

    Args:
        project_root: Active project root.
        source_path: Absolute or project-relative source path.

    Returns:
        JSON-safe binary payload with path, MIME type, and byte integers.

    Raises:
        ValueError: If the source path is invalid, too large, or not a file.
    """

    from paradev.sdk.project import Project

    snapshot = Project.load(project_root).read_source_binary(
        source_path,
        include_content=True,
    )
    content = base64.b64decode(str(snapshot["content_base64"]), validate=True)
    return desktop_binary_source(str(snapshot["path"]), content)


def desktop_binary_source(path: str | Path, content: bytes | bytearray | Sequence[int]) -> dict[str, object]:
    """Return a JSON-safe desktop binary-source payload.

    Args:
        path: Source or cache path represented by the payload.
        content: Bytes or byte values.

    Returns:
        Payload matching the `paradev.desktop.binary-source.v1` contract.

    Raises:
        ValueError: If byte values are outside `0..255`.
    """

    data = _byte_list(content)
    return {
        "schema": BINARY_SOURCE_SCHEMA,
        "path": str(Path(path)),
        "mimeType": desktop_mime_type(path),
        "bytes": data,
    }


def desktop_browser_cache_path(project_root: str | Path) -> Path:
    """Return the project browser cache path used by the desktop shell.

    Args:
        project_root: Active project root.

    Returns:
        Canonical cache file path under `.paradev/.cache`.
    """

    root = _canonical_existing(project_root, "project root")
    return _project_cache_root(root) / "desktop" / "project-browser" / "browser.json"


def read_project_browser_cache(project_root: str | Path) -> dict[str, object] | None:
    """Read the cached unfiltered project browser payload for the root.

    Args:
        project_root: Active project root.

    Returns:
        Cached browser payload, or `None` when missing, invalid, or stale.

    Raises:
        ValueError: If the cache file exceeds the desktop size limit.
    """

    root = _canonical_existing(project_root, "project root")
    path = desktop_browser_cache_path(root)
    if not path.is_file():
        return None
    _require_file_under_limit(path, MAX_PROJECT_BROWSER_CACHE_BYTES, "Project browser cache")
    try:
        payload = load_json(str(path))
    except Exception:
        path.unlink(missing_ok=True)
        return None
    if _browser_cache_payload_matches(payload, root):
        return dict(payload)
    path.unlink(missing_ok=True)
    return None


def desktop_write_browser_cache(project_root: str | Path, payload: Mapping[str, object]) -> dict[str, object]:
    """Write an unfiltered project browser cache payload after validation.

    Args:
        project_root: Active project root.
        payload: Browser payload returned by `Project.browser(...)`.

    Returns:
        JSON-safe payload written to the cache.

    Raises:
        ValueError: If the payload is filtered, its root does not match the
            project root, or the encoded payload exceeds the desktop size
            limit.
    """

    root = _canonical_existing(project_root, "project root")
    if not _browser_cache_payload_matches(payload, root):
        raise ValueError("Project browser cache payload must be unfiltered and match the active project root.")
    encoded_size = len(dumps_json(dict(payload), compact=True).encode("utf-8"))
    if encoded_size > MAX_PROJECT_BROWSER_CACHE_BYTES:
        raise ValueError(f"Project browser cache payload is larger than {MAX_PROJECT_BROWSER_CACHE_BYTES} bytes.")
    path = desktop_browser_cache_path(root)
    touch_dir(str(path.parent))
    dump_json(dict(payload), str(path))
    return dict(payload)


def desktop_thumbnail_cache_path(project_root: str | Path, cache_key: str) -> Path:
    """Return the deterministic thumbnail cache path for a source key.

    Args:
        project_root: Active project root.
        cache_key: Stable source identifier, usually a source path.

    Returns:
        Cache PNG path under `.paradev/.cache/instance-thumbnails`.

    Raises:
        ValueError: If the project root is not a directory or the cache key is
            empty.
    """

    root = _canonical_existing(project_root, "project root")
    if not root.is_dir():
        raise ValueError("project root is not a directory.")
    key = _required_text(cache_key, "thumbnail cache key")
    return _project_cache_root(root) / "instance-thumbnails" / f"{_stable_hash(key.encode('utf-8')):016x}.png"


def desktop_read_thumbnail_cache(project_root: str | Path, cache_key: str) -> dict[str, object] | None:
    """Read one cached thumbnail payload.

    Args:
        project_root: Active project root.
        cache_key: Stable source identifier.

    Returns:
        JSON-safe PNG binary-source payload, or `None` when the valid cache
        key has no entry yet or its derived entry was stale and invalid.

    Raises:
        ValueError: If the cache path is not a regular file or is too large.
        OSError: If a stale invalid cache file cannot be removed safely.
    """

    path = desktop_thumbnail_cache_path(project_root, cache_key)
    max_bytes = _thumbnail_cache_max_bytes()
    for attempt in range(2):
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            return None
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("Thumbnail cache path is not a file.")
        if metadata.st_size > max_bytes:
            raise ValueError(f"Thumbnail cache file is larger than {max_bytes} bytes.")
        content = path.read_bytes()
        if len(content) > max_bytes:
            raise ValueError(f"Thumbnail cache file is larger than {max_bytes} bytes.")
        try:
            _require_valid_thumbnail_png(content)
        except ValueError:
            try:
                current = path.lstat()
            except FileNotFoundError:
                return None
            if _same_file_revision(metadata, current):
                path.unlink()
                return None
            if attempt == 0:
                continue
            raise ValueError("Thumbnail cache changed while being read.")
        return {
            **desktop_binary_source(path, content),
            "mimeType": "image/png",
        }
    raise AssertionError("thumbnail cache read retry loop exhausted")


def desktop_write_thumbnail_cache(project_root: str | Path, cache_key: str, content: bytes | bytearray | Sequence[int]) -> dict[str, object]:
    """Write one cached thumbnail payload.

    Args:
        project_root: Active project root.
        cache_key: Stable source identifier.
        content: PNG bytes or byte values.

    Returns:
        JSON-safe PNG binary-source payload.

    Raises:
        ValueError: If the content is empty, exceeds the desktop size limit,
            is not a structurally valid PNG, or targets a non-file cache
            entry.
    """

    data = bytes(_byte_list(content))
    if not data:
        raise ValueError("Thumbnail cache bytes cannot be empty.")
    max_bytes = _thumbnail_cache_max_bytes()
    if len(data) > max_bytes:
        raise ValueError(f"Thumbnail cache bytes are larger than {max_bytes} bytes.")
    _require_valid_thumbnail_png(data)
    path = desktop_thumbnail_cache_path(project_root, cache_key)
    touch_dir(str(path.parent))
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        pass
    else:
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("Thumbnail cache path is not a file.")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as target:
            temporary_path = Path(target.name)
            target.write(data)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return {
        **desktop_binary_source(path, data),
        "mimeType": "image/png",
    }


def desktop_read_app_config() -> object:
    """Read persisted desktop GUI settings from `CM_PARADEV`.

    Returns:
        Stored JSON-like value, or `None` when unset.
    """

    return _desktop_json_value(CM_PARADEV.get(DESKTOP_APP_CONFIG_KEY, default=None))


def desktop_write_app_config(config: Mapping[str, object]) -> None:
    """Persist desktop GUI settings through `CM_PARADEV`.

    Args:
        config: JSON-like desktop settings object.

    Raises:
        ValueError: If `config` is not a mapping.
    """

    if not isinstance(config, Mapping):
        raise ValueError("Desktop app config must be a JSON object.")
    CM_PARADEV.set(DESKTOP_APP_CONFIG_KEY, _desktop_json_value(config))


def desktop_read_config_value(key: str) -> dict[str, object]:
    """Read one desktop-exposed `CM_PARADEV` config value.

    Args:
        key: Supported dotted config key.

    Returns:
        JSON-safe config value payload.

    Raises:
        ValueError: If the key is not exposed to the desktop GUI or the stored
            value is invalid for that key.
    """

    clean_key = _desktop_config_key(key)
    value = _desktop_config_raw_value(clean_key)
    return {
        "schema": CONFIG_VALUE_SCHEMA,
        "key": clean_key,
        "value": _desktop_config_value(clean_key, value),
    }


def desktop_write_config_value(key: str, value: object) -> dict[str, object]:
    """Write one desktop-exposed `CM_PARADEV` config value.

    Args:
        key: Supported dotted config key.
        value: JSON-like value to validate and persist.

    Returns:
        JSON-safe config value payload after writing.

    Raises:
        ValueError: If the key is unsupported or the value is invalid.
    """

    clean_key = _desktop_config_key(key)
    clean_value = _desktop_config_value(clean_key, value)
    CM_PARADEV.set(clean_key, clean_value)
    return {
        "schema": CONFIG_VALUE_SCHEMA,
        "key": clean_key,
        "value": clean_value,
    }


def desktop_dependency_status(dependency_id: str) -> dict[str, object]:
    """Detect one desktop dependency used by ParaDev.

    Args:
        dependency_id: Stable dependency id. Currently `imagemagick`.

    Returns:
        JSON-safe status payload.

    Raises:
        ValueError: If the dependency id is unsupported.
    """

    dependency = _dependency_spec(dependency_id)
    path = _first_executable(dependency["commands"])
    version = _command_version(path) if path else ""
    install_command = _dependency_install_command(dependency_id)
    return {
        "schema": DEPENDENCY_SCHEMA,
        "id": dependency_id,
        "label": dependency["label"],
        "installed": bool(path),
        "status": "ready" if path else "missing",
        "path": path,
        "version": version,
        "installCommand": install_command,
        "installSupported": bool(install_command),
        "detail": dependency["detail"],
    }


def desktop_install_dependency(dependency_id: str) -> dict[str, object]:
    """Install one desktop dependency through the platform package manager.

    Args:
        dependency_id: Stable dependency id. Currently `imagemagick`.

    Returns:
        Fresh dependency status after the install command exits.

    Raises:
        ValueError: If the dependency id or platform is unsupported.
        OSError: If the installer command fails.
    """

    command = _dependency_install_command(dependency_id)
    if not command:
        raise ValueError(f"Installing {dependency_id} is not supported on this platform.")
    result = subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise OSError(f"Dependency install failed: {detail or result.returncode}")
    return desktop_dependency_status(dependency_id)


def desktop_test_llm_route(
    provider: str,
    model: str,
    gateway: str,
    key_env: str | None = None,
    base_url: str | None = None,
    preset: str | None = None,
) -> dict[str, object]:
    """Run a short HeavenBase LLM route test.

    Args:
        provider: HeavenBase provider id, such as `deepseek`.
        model: Canonical model id, such as `deepseek-v4-flash`.
        gateway: HeavenBase gateway id, such as `openai`.
        key_env: Optional API-key environment variable name to test. When
            omitted, the persisted `paradev.ai.key_env` config value is used.
        base_url: Optional LLM base URL override. When omitted, the persisted
            `paradev.ai.base_url` config value is used.
        preset: Optional HeavenBase route preset. When omitted, the persisted
            `paradev.ai.preset` config value is used.

    Returns:
        JSON-safe LLM route test payload.
    """

    clean_provider = _required_text(provider, "LLM provider")
    clean_model = _required_text(model, "LLM model")
    clean_gateway = _required_text(gateway, "LLM gateway")
    clean_key_env = _desktop_text_config_value("paradev.ai.key_env", key_env) if key_env is not None else None
    clean_base_url = _desktop_optional_text_config_value("paradev.ai.base_url", base_url) if base_url is not None else _llm_base_url()
    clean_preset = _llm_preset(preset)
    key_source = _llm_key_source(clean_provider, clean_key_env)
    api_key = _llm_api_key(clean_provider, clean_key_env)
    materialized_base_url = clean_base_url
    try:
        import heavenbase as hb

        llm_kwargs = {
            "preset": clean_preset,
            "model": clean_model,
            "provider": clean_provider,
            "gateway": clean_gateway,
            "cache": False,
            "temperature": 0,
            "max_tokens": 8,
        }
        if api_key:
            llm_kwargs["api_key"] = api_key
        if clean_base_url:
            llm_kwargs["base_url"] = clean_base_url
        llm = hb.LLM(**llm_kwargs)
        runtime = hb.LLMEngine().apply(llm.spec)
        materialized_base_url = str(runtime.get("base_url") or clean_base_url)
        text = str(llm.chat("Reply with exactly: hb-ok") or "").strip()
    except Exception as error:
        return _llm_test_payload(clean_provider, clean_model, clean_gateway, clean_preset, key_source, "error", "exception", str(error), materialized_base_url)
    if text == "hb-ok":
        return _llm_test_payload(clean_provider, clean_model, clean_gateway, clean_preset, key_source, "ready", "ok", "Received hb-ok.", materialized_base_url)
    if text:
        return _llm_test_payload(
            clean_provider,
            clean_model,
            clean_gateway,
            clean_preset,
            key_source,
            "warning",
            "unexpected_response",
            f"Received unexpected response: {text[:160]}",
            materialized_base_url,
        )
    return _llm_test_payload(
        clean_provider,
        clean_model,
        clean_gateway,
        clean_preset,
        key_source,
        "warning",
        "empty_response",
        f"{_llm_route_label(clean_provider, clean_model)} route returned an empty response.",
        materialized_base_url,
    )


def desktop_chat(
    provider: str,
    model: str,
    gateway: str,
    prompt: str,
    role: str = "chat",
    project_root: str = "",
    sources: Sequence[Mapping[str, object]] | None = None,
    key_env: str | None = None,
    base_url: str | None = None,
    preset: str | None = None,
) -> dict[str, object]:
    """Send one desktop AI chat prompt through HeavenBase.

    Args:
        provider: HeavenBase provider id, such as `deepseek`.
        model: Canonical model id, such as `deepseek-v4-flash`.
        gateway: HeavenBase gateway id, such as `openai`.
        prompt: User prompt to send.
        role: Stable ParaDev chat role id, such as `chat`, `explain`,
            `create-module`, or `edit-selection`. Structured authoring roles
            accept only validated SDK dry proposals.
        project_root: Optional active project root for GUI context.
        sources: Optional source/context descriptors owned by the SDK facade.
        key_env: Optional API-key environment variable name to test. When
            omitted, the persisted `paradev.ai.key_env` config value is used.
        base_url: Optional LLM base URL override. When omitted, the persisted
            `paradev.ai.base_url` config value is used.
        preset: Optional HeavenBase route preset. When omitted, the persisted
            `paradev.ai.preset` config value is used.

    Returns:
        JSON-safe desktop AI chat payload. A validated create-module response
        includes an optional `paradev.desktop.ai-chat-proposal.v1` proposal
        containing a normalized request and the exact SDK dry plan.
    """

    clean_provider = _required_text(provider, "AI provider")
    clean_model = _required_text(model, "AI model")
    clean_gateway = _required_text(gateway, "AI gateway")
    clean_prompt = _required_text(prompt, "AI prompt")
    clean_role = _required_text(role, "AI role")
    clean_project_root = _clean_chat_project_root(project_root)
    clean_key_env = _desktop_text_config_value("paradev.ai.key_env", key_env) if key_env is not None else None
    clean_base_url = _desktop_optional_text_config_value("paradev.ai.base_url", base_url) if base_url is not None else _llm_base_url()
    clean_preset = _llm_preset(preset)
    profile = _chat_profile(clean_role, clean_project_root)
    clean_sources, source_contexts = _chat_sources(clean_project_root, sources)
    effective_prompt = _chat_prompt(profile, clean_project_root, clean_prompt, source_contexts)
    proposal_project: Project | None = None
    module_templates: dict[str, Mapping[str, object]] = {}
    if clean_role == "create-module":
        if not clean_project_root:
            raise ValueError("The create-module AI role requires an active ParaDev project root.")
        from paradev.sdk.project import Project

        proposal_project = Project.load(clean_project_root)
        module_templates, template_catalog = _chat_module_template_catalog(proposal_project)
        effective_prompt = _chat_module_plan_prompt(effective_prompt, template_catalog)
    elif clean_role == "edit-selection":
        if not clean_project_root:
            raise ValueError("The edit-selection AI role requires an active ParaDev project root.")
        from paradev.sdk.project import Project

        proposal_project = Project.load(clean_project_root)
        source_forms, source_catalog = _chat_source_form_catalog(
            proposal_project,
            clean_sources,
        )
        effective_prompt = _chat_source_update_prompt(effective_prompt, source_catalog)
    key_source = _llm_key_source(clean_provider, clean_key_env)
    api_key = _llm_api_key(clean_provider, clean_key_env)
    materialized_base_url = clean_base_url
    proposal: dict[str, object] | None = None
    try:
        import heavenbase as hb

        llm_kwargs = {
            "preset": clean_preset,
            "model": clean_model,
            "provider": clean_provider,
            "gateway": clean_gateway,
            "cache": False,
            "temperature": 0,
            "max_tokens": (_CREATE_MODULE_AI_CHAT_MAX_TOKENS if proposal_project is not None else _DEFAULT_AI_CHAT_MAX_TOKENS),
        }
        if api_key:
            llm_kwargs["api_key"] = api_key
        if clean_base_url:
            llm_kwargs["base_url"] = clean_base_url
        llm = hb.LLM(**llm_kwargs)
        runtime = hb.LLMEngine().apply(llm.spec)
        materialized_base_url = str(runtime.get("base_url") or clean_base_url)
        if proposal_project is not None:
            structured = llm.chat(
                effective_prompt,
                response_format={"type": "json_object"},
                include="structured",
            )
            if clean_role == "edit-selection":
                reply, proposal = _chat_source_update_response(
                    proposal_project,
                    structured,
                    source_forms,
                )
            else:
                reply, proposal = _chat_module_plan_response(
                    proposal_project,
                    structured,
                    module_templates,
                )
        else:
            reply = str(llm.chat(effective_prompt) or "").strip()
    except Exception as error:
        return _chat_payload(
            clean_provider,
            clean_model,
            clean_gateway,
            clean_preset,
            key_source,
            clean_role,
            clean_project_root,
            clean_prompt,
            clean_sources,
            "",
            "error",
            str(error),
            materialized_base_url,
        )
    if not reply:
        return _chat_payload(
            clean_provider,
            clean_model,
            clean_gateway,
            clean_preset,
            key_source,
            clean_role,
            clean_project_root,
            clean_prompt,
            clean_sources,
            "",
            "warning",
            "AI route returned an empty response.",
            materialized_base_url,
        )
    return _chat_payload(
        clean_provider,
        clean_model,
        clean_gateway,
        clean_preset,
        key_source,
        clean_role,
        clean_project_root,
        clean_prompt,
        clean_sources,
        reply,
        "ready",
        "",
        materialized_base_url,
        proposal=proposal,
    )


def desktop_chat_profiles(project_root: str = "") -> dict[str, object]:
    """Return SDK-owned AI chat roles and prompt profiles.

    Args:
        project_root: Optional active project root for GUI context.

    Returns:
        JSON-safe profile catalog used by desktop chat surfaces.
    """

    clean_project_root = _clean_chat_project_root(project_root)
    return {
        "schema": AI_CHAT_PROFILES_SCHEMA,
        "defaultRole": _default_ai_chat_role(),
        "projectRoot": clean_project_root,
        "sourceKinds": list(AI_CHAT_SOURCE_KIND_VALUES),
        "sourceKindRows": list(AI_CHAT_SOURCE_KIND_ROWS),
        "profiles": _chat_profiles(clean_project_root),
    }


def desktop_write_chat_profile(profile_id: str, profile: Mapping[str, object], project_root: str = "") -> dict[str, object]:
    """Persist one SDK-owned AI chat profile override.

    Args:
        profile_id: Built-in role id to edit, such as `chat` or `explain`.
        profile: JSON-like profile fields to override.
        project_root: Optional active project root for the returned catalog.

    Returns:
        Fresh desktop AI chat profile catalog after writing.

    Raises:
        ValueError: If the profile id, payload, or stored override catalog is
            invalid.
    """

    clean_profile_id = _chat_profile_id(profile_id)
    clean_override = _chat_profile_override(clean_profile_id, profile)
    clean_project_root = _clean_chat_project_root(project_root)
    global_profiles, project_profiles = _chat_profile_override_catalog()
    if clean_project_root:
        project_profiles.setdefault(clean_project_root, {})[clean_profile_id] = clean_override
    else:
        global_profiles[clean_profile_id] = clean_override
    _write_chat_profile_override_catalog(global_profiles, project_profiles)
    return desktop_chat_profiles(project_root=project_root)


def desktop_reset_chat_profile(profile_id: str, project_root: str = "") -> dict[str, object]:
    """Remove one SDK-owned AI chat profile override.

    Args:
        profile_id: Built-in role id to reset, such as `chat` or `explain`.
        project_root: Optional active project root for the returned catalog.

    Returns:
        Fresh desktop AI chat profile catalog after removing the override.

    Raises:
        ValueError: If the profile id or stored override catalog is invalid.
    """

    clean_profile_id = _chat_profile_id(profile_id)
    clean_project_root = _clean_chat_project_root(project_root)
    global_profiles, project_profiles = _chat_profile_override_catalog()
    if clean_project_root:
        project_profile_overrides = project_profiles.get(clean_project_root, {})
        project_profile_overrides.pop(clean_profile_id, None)
        if project_profile_overrides:
            project_profiles[clean_project_root] = project_profile_overrides
        else:
            project_profiles.pop(clean_project_root, None)
    else:
        global_profiles.pop(clean_profile_id, None)
    _write_chat_profile_override_catalog(global_profiles, project_profiles)
    return desktop_chat_profiles(project_root=project_root)


def desktop_mime_type(path: str | Path) -> str:
    """Return the desktop MIME type for a source or cache path.

    Args:
        path: Source or cache path.

    Returns:
        MIME type used by desktop binary-source payloads.
    """

    suffix = Path(path).suffix.lower().lstrip(".")
    return {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "bmp": "image/bmp",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "dds": "image/vnd.ms-dds",
        "tga": "image/x-tga",
    }.get(suffix, "application/octet-stream")


def _browser_cache_payload_matches(payload: object, project_root: Path) -> bool:
    if not isinstance(payload, Mapping):
        return False
    if payload.get("schema") != PROJECT_BROWSER_SCHEMA:
        return False
    filters = payload.get("filters")
    if not isinstance(filters, Mapping) or filters:
        return False
    root_value = payload.get("root")
    if not isinstance(root_value, str) or not root_value.strip():
        return False
    try:
        return _canonical_existing(root_value, "project browser cache root") == project_root
    except ValueError:
        return False


def _byte_list(content: bytes | bytearray | Sequence[int]) -> list[int]:
    values = list(content)
    if any(not isinstance(value, int) or value < 0 or value > 255 for value in values):
        raise ValueError("Binary-source bytes must be integers in the range 0..255.")
    return values


def _canonical_existing(path: str | Path, label: str) -> Path:
    raw = _required_path(path, label)
    try:
        return raw.resolve(strict=True)
    except OSError as error:
        raise ValueError(f"Cannot resolve {label}: {error}") from error


def _project_cache_root(project_root: Path) -> Path:
    return project_root / ".paradev" / ".cache"


def _required_path(path: str | Path, label: str) -> Path:
    if isinstance(path, Path):
        raw = path
    elif isinstance(path, str):
        raw = Path(_required_text(path, label))
    else:
        raise ValueError(f"{label} must be a path string.")
    if not str(raw).strip():
        raise ValueError(f"{label} cannot be empty.")
    return raw


def _required_text(value: str, label: str) -> str:
    clean = value.strip() if isinstance(value, str) else ""
    if not clean:
        raise ValueError(f"{label} cannot be empty.")
    return clean


def _desktop_config_key(key: str) -> str:
    clean = _required_text(key, "desktop config key")
    if clean not in DESKTOP_CONFIG_DEFAULTS:
        raise ValueError(f"Unsupported desktop config key: {clean}.")
    return clean


def _desktop_config_raw_value(key: str) -> object:
    value = CM_PARADEV.get(key, default=DESKTOP_CONFIG_DEFAULTS[key])
    if isinstance(value, Mapping) and value.get("__HB_REMOVE__") is True:
        return DESKTOP_CONFIG_DEFAULTS[key]
    return value


def _desktop_config_value(key: str, value: object) -> object:
    row = DESKTOP_CONFIG_ROW_BY_KEY.get(key)
    if row is None:
        raise ValueError(f"Unsupported desktop config key: {key}.")
    value_type = str(row["valueType"])
    if value_type == "text":
        return _desktop_text_config_value(key, value)
    if value_type == "optional_text":
        return _desktop_optional_text_config_value(key, value)
    if value_type == "choice":
        clean = _desktop_text_config_value(key, value)
        choices = tuple(str(choice) for choice in row.get("choices", ()))
        if clean not in choices:
            if len(choices) == 2:
                raise ValueError(f"{key} must be either '{choices[0]}' or '{choices[1]}'.")
            raise ValueError(f"{key} must be one of: {', '.join(sorted(choices))}.")
        return clean
    if value_type == "positive_int":
        return _desktop_positive_int_config_value(key, value)
    if value_type == "boolean":
        if not isinstance(value, bool):
            raise ValueError(f"{key} must be a boolean.")
        return value
    if value_type == "chat_profile":
        return _chat_profile_id(value if isinstance(value, str) else "")
    raise ValueError(f"Unsupported desktop config key: {key}.")


def _desktop_text_config_value(key: str, value: object) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a non-empty string.")
    clean = value.strip()
    if not clean:
        raise ValueError(f"{key} must be a non-empty string.")
    return clean


def _desktop_optional_text_config_value(key: str, value: object) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string.")
    return value.strip()


def _desktop_positive_int_config_value(key: str, value: object) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{key} must be a positive integer.")
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{key} must be a positive integer.") from error
    if number < 1 or not math.isfinite(number):
        raise ValueError(f"{key} must be a positive integer.")
    return int(number + 0.5)


def _thumbnail_cache_max_bytes() -> int:
    value = CM_PARADEV.get(
        "paradev.desktop.thumbnail_cache.max_kb",
        default=DESKTOP_CONFIG_DEFAULTS["paradev.desktop.thumbnail_cache.max_kb"],
    )
    return int(_desktop_config_value("paradev.desktop.thumbnail_cache.max_kb", value)) * 1024


def _desktop_json_value(value: object) -> object:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Desktop app config contains unsupported non-finite float.")
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _desktop_json_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_desktop_json_value(item) for item in value]
    raise ValueError(f"Desktop app config contains unsupported value: {type(value).__name__}.")


def _require_file_under_limit(path: Path, limit: int, label: str) -> None:
    if not path.is_file():
        raise ValueError(f"{label} path is not a file.")
    size = path.stat().st_size
    if size > limit:
        raise ValueError(f"{label} file is larger than {limit} bytes.")


def _require_valid_thumbnail_png(content: bytes) -> None:
    invalid = ValueError("Thumbnail cache file is not a valid PNG.")
    if not content.startswith(_PNG_SIGNATURE):
        raise invalid

    cursor = len(_PNG_SIGNATURE)
    saw_header = False
    saw_data = False
    saw_end = False
    while cursor < len(content):
        if len(content) - cursor < 12:
            raise invalid
        chunk_length = int.from_bytes(content[cursor : cursor + 4], "big")
        chunk_type_start = cursor + 4
        chunk_data_start = chunk_type_start + 4
        chunk_data_end = chunk_data_start + chunk_length
        chunk_end = chunk_data_end + 4
        if chunk_end > len(content):
            raise invalid
        chunk_type = content[chunk_type_start:chunk_data_start]
        expected_crc = int.from_bytes(content[chunk_data_end:chunk_end], "big")
        actual_crc = zlib.crc32(content[chunk_type_start:chunk_data_end]) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            raise invalid

        if chunk_type == b"IHDR":
            if saw_header or cursor != len(_PNG_SIGNATURE) or chunk_length != 13:
                raise invalid
            width = int.from_bytes(content[chunk_data_start : chunk_data_start + 4], "big")
            height = int.from_bytes(content[chunk_data_start + 4 : chunk_data_start + 8], "big")
            if width < 1 or height < 1:
                raise invalid
            saw_header = True
        elif not saw_header:
            raise invalid

        if chunk_type == b"IDAT":
            saw_data = True
        elif chunk_type == b"IEND":
            if chunk_length != 0 or chunk_end != len(content):
                raise invalid
            saw_end = True
            cursor = chunk_end
            break
        cursor = chunk_end

    if cursor != len(content) or not (saw_header and saw_data and saw_end):
        raise invalid


def _same_file_revision(left: os.stat_result, right: os.stat_result) -> bool:
    return (left.st_dev, left.st_ino, left.st_size, left.st_mtime_ns) == (
        right.st_dev,
        right.st_ino,
        right.st_size,
        right.st_mtime_ns,
    )


def _stable_hash(content: bytes) -> int:
    value = 0xCBF29CE484222325
    for byte in content:
        value ^= byte
        value = (value * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return value


def _dependency_spec(dependency_id: str) -> dict[str, object]:
    clean_id = _required_text(dependency_id, "desktop dependency id")
    if clean_id == "imagemagick":
        return {
            "commands": ("magick", "convert"),
            "detail": "Required for asset inspection, conversion, and DDS/TGA/image workflows.",
            "label": "ImageMagick",
        }
    raise ValueError(f"Unsupported desktop dependency: {clean_id}")


def _first_executable(commands: object) -> str:
    if not isinstance(commands, Sequence) or isinstance(commands, str):
        return ""
    for command in commands:
        if not isinstance(command, str):
            continue
        path = shutil.which(command)
        if path:
            return path
    return ""


def _command_version(path: str) -> str:
    if not path:
        return ""
    result = subprocess.run([path, "-version"], check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = (result.stdout or result.stderr).strip()
    return output.splitlines()[0][:200] if output else ""


def _dependency_install_command(dependency_id: str) -> list[str]:
    _dependency_spec(dependency_id)
    system = platform.system().lower()
    if system == "darwin" and shutil.which("brew"):
        return ["brew", "install", "imagemagick"]
    if system == "windows" and shutil.which("winget"):
        return ["winget", "install", "--id", "ImageMagick.ImageMagick", "--exact"]
    if system == "linux":
        if shutil.which("apt-get") and shutil.which("sudo"):
            return ["sudo", "apt-get", "install", "-y", "imagemagick"]
        if shutil.which("dnf") and shutil.which("sudo"):
            return ["sudo", "dnf", "install", "-y", "ImageMagick"]
        if shutil.which("pacman") and shutil.which("sudo"):
            return ["sudo", "pacman", "-S", "--noconfirm", "imagemagick"]
        if shutil.which("brew"):
            return ["brew", "install", "imagemagick"]
    return []


def _llm_default_key_env(provider: str) -> str:
    key_map = {
        "anthropic": "ANTHROPIC_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }
    return key_map.get(provider, f"{provider.upper()}_API_KEY")


def _llm_key_env(provider: str, key_env: str | None = None) -> str:
    if key_env is not None:
        return key_env
    value = CM_PARADEV.get("paradev.ai.key_env", default=DESKTOP_CONFIG_DEFAULTS["paradev.ai.key_env"])
    try:
        return str(_desktop_config_value("paradev.ai.key_env", value))
    except ValueError:
        return _llm_default_key_env(provider)


def _llm_base_url(base_url: str | None = None) -> str:
    if base_url is not None:
        return base_url
    value = CM_PARADEV.get("paradev.ai.base_url", default=DESKTOP_CONFIG_DEFAULTS["paradev.ai.base_url"])
    try:
        return str(_desktop_config_value("paradev.ai.base_url", value))
    except ValueError:
        return str(DESKTOP_CONFIG_DEFAULTS["paradev.ai.base_url"])


def _llm_preset(preset: str | None = None) -> str:
    if preset is not None:
        return str(_desktop_config_value("paradev.ai.preset", preset))
    value = CM_PARADEV.get("paradev.ai.preset", default=DESKTOP_CONFIG_DEFAULTS["paradev.ai.preset"])
    try:
        return str(_desktop_config_value("paradev.ai.preset", value))
    except ValueError:
        return str(DESKTOP_CONFIG_DEFAULTS["paradev.ai.preset"])


def _llm_api_key(provider: str, key_env: str | None = None) -> str:
    return os.environ.get(_llm_key_env(provider, key_env), "")


def _llm_key_source(provider: str, key_env: str | None = None) -> str:
    key = _llm_key_env(provider, key_env)
    return key if os.environ.get(key) else f"{key} (missing)"


def _llm_route_label(provider: str, model: str) -> str:
    return f"{provider} / {model}"


def _llm_test_payload(
    provider: str,
    model: str,
    gateway: str,
    preset: str,
    key_source: str,
    status: str,
    result_code: str,
    detail: str,
    base_url: str,
) -> dict[str, object]:
    return {
        "schema": LLM_TEST_SCHEMA,
        "provider": provider,
        "model": model,
        "gateway": gateway,
        "preset": preset,
        "keySource": key_source,
        "baseUrl": base_url,
        "status": status,
        "resultCode": result_code,
        "detail": detail,
        "checkedAt": _utc_timestamp(),
    }


def _chat_payload(
    provider: str,
    model: str,
    gateway: str,
    preset: str,
    key_source: str,
    role: str,
    project_root: str,
    prompt: str,
    sources: Sequence[Mapping[str, object]],
    reply: str,
    status: str,
    detail: str,
    base_url: str,
    *,
    proposal: Mapping[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema": AI_CHAT_SCHEMA,
        "provider": provider,
        "model": model,
        "gateway": gateway,
        "preset": preset,
        "keySource": key_source,
        "baseUrl": base_url,
        "status": status,
        "role": role,
        "projectRoot": project_root,
        "prompt": prompt,
        "sources": [dict(source) for source in sources],
        "reply": reply,
        "detail": detail,
        "checkedAt": _utc_timestamp(),
    }
    if proposal is not None:
        payload["proposal"] = dict(proposal)
    return payload


def _chat_module_template_catalog(
    project: Project,
) -> tuple[dict[str, Mapping[str, object]], dict[str, object]]:
    payload = project.templates(authoring_ready=True)
    rows = payload.get("templates")
    if isinstance(rows, (str, bytes, bytearray)) or not isinstance(rows, Sequence):
        raise RuntimeError("Project.templates() returned an invalid template catalog.")
    source_roots = payload.get("source_roots")
    if isinstance(source_roots, (str, bytes, bytearray)) or not isinstance(source_roots, Sequence):
        raise RuntimeError("Project.templates() returned invalid source roots.")

    templates: dict[str, Mapping[str, object]] = {}
    prompt_rows: list[dict[str, object]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise RuntimeError("Project.templates() returned an invalid template row.")
        template_id = row.get("id")
        family = row.get("family")
        kind = row.get("kind", "module")
        args = row.get("args")
        form = row.get("form")
        if (
            not isinstance(template_id, str)
            or not template_id
            or not isinstance(family, str)
            or not family
            or kind not in {"module", "collection"}
            or not isinstance(args, Mapping)
        ):
            raise RuntimeError("Project.templates() returned an incomplete template row.")
        if not isinstance(form, Mapping):
            raise RuntimeError(f"Authoring template {template_id!r} has no form projection.")
        fields = form.get("fields")
        if isinstance(fields, (str, bytes, bytearray)) or not isinstance(fields, Sequence):
            raise RuntimeError(f"Authoring template {template_id!r} has invalid form fields.")
        form_fields: dict[str, Mapping[str, object]] = {}
        for field in fields:
            if not isinstance(field, Mapping):
                raise RuntimeError(f"Authoring template {template_id!r} has an invalid form field.")
            field_name = field.get("name")
            if not isinstance(field_name, str) or not field_name or field_name in form_fields:
                raise RuntimeError(f"Authoring template {template_id!r} has invalid form field names.")
            form_fields[field_name] = field
        if set(form_fields) != set(args):
            raise RuntimeError(f"Authoring template {template_id!r} form fields do not match its arguments.")
        templates[template_id] = row
        prompt_args: dict[str, dict[str, object]] = {}
        for name, spec in args.items():
            if not isinstance(name, str) or not isinstance(spec, Mapping):
                raise RuntimeError(f"Authoring template {template_id!r} has invalid arguments.")
            form_spec = form_fields[name]
            prompt_spec = {"type": str(form_spec.get("type", "string"))}
            for field in (
                "required",
                "default",
                "advanced",
                "label",
                "description",
                "description_source",
                "choices",
                "reference",
            ):
                if field in form_spec and form_spec[field] not in (False, "", (), []):
                    prompt_spec[field] = form_spec[field]
            prompt_args[name] = prompt_spec
        prompt_rows.append(
            {
                "template_id": template_id,
                "family": family,
                "kind": kind,
                "values": prompt_args,
            }
        )
    if not templates:
        raise ValueError("The active project has no authoring-ready templates.")
    return templates, {
        "operation_ids": ["module.create_batch", "collection.scaffold"],
        "maximum_modules": _MAX_AI_CHAT_PROPOSAL_MODULES,
        "source_roots": [dict(row) for row in source_roots if isinstance(row, Mapping)],
        "templates": prompt_rows,
    }


def _chat_module_plan_prompt(prompt: str, template_catalog: Mapping[str, object]) -> str:
    contract = (
        "Return exactly one JSON object with keys `reply` and `proposal`. "
        "`reply` must be a concise user-facing string. Use `proposal: null` when no concrete content was requested. "
        "For modules, proposal must be "
        '{"operation_id":"module.create_batch","source_root":"optional configured source root",'
        '"modules":[{"template_id":"exact catalog id","object_id":"one folder id","values":{"template_arg":"JSON scalar"}}]}. '
        "For a focus tree, decision category, or other collection, proposal must be "
        '{"operation_id":"collection.scaffold","source_root":"optional configured source root",'
        '"template_id":"exact catalog id","collection_id":"one collection id","values":{"template_arg":"JSON scalar"}}. '
        "Use only catalog templates and their declared value names. Values may be strings, booleans, integers, or finite numbers; "
        "Treat each field's type, label, description, default, advanced status, choices, and existing-object reference as authoritative, including units and examples. "
        "Never use null, arrays, or objects as values. Every module batch must resolve to one family, and the template kind must match the operation. "
        "Do not include write, force, plan_hash, or any other field. This response only requests a dry plan and never writes files."
    )
    return "\n\n".join((prompt, contract, "Authoritative ParaDev template catalog:\n" + dumps_json(template_catalog, indent=2)))


def _chat_module_plan_response(
    project: Project,
    value: object,
    templates: Mapping[str, Mapping[str, object]],
) -> tuple[str, dict[str, object] | None]:
    response = _chat_module_plan_mapping(value, "AI module-plan response", frozenset({"reply", "proposal"}))
    missing_response_fields = sorted({"reply", "proposal"} - set(response))
    if missing_response_fields:
        raise ValueError(f"AI module-plan response is missing required fields: {', '.join(missing_response_fields)}.")
    reply = response.get("reply")
    if not isinstance(reply, str) or not reply.strip():
        raise ValueError("AI module-plan response requires a non-empty reply string.")
    clean_reply = reply.strip()
    proposal_value = response.get("proposal")
    if proposal_value is None:
        return clean_reply, None

    if not isinstance(proposal_value, Mapping):
        raise ValueError("AI module-plan proposal must be a JSON object.")
    operation_id = proposal_value.get("operation_id")
    if operation_id == "collection.scaffold":
        return clean_reply, _chat_collection_plan_proposal(
            project,
            proposal_value,
            templates,
        )
    if operation_id != "module.create_batch":
        raise ValueError("AI module-plan proposal operation_id must be 'module.create_batch' or 'collection.scaffold'.")
    proposal = _chat_module_plan_mapping(
        proposal_value,
        "AI module-plan proposal",
        frozenset({"operation_id", "source_root", "modules"}),
    )
    source_root: str | None = None
    if "source_root" in proposal:
        raw_source_root = proposal["source_root"]
        if not isinstance(raw_source_root, str) or not raw_source_root.strip():
            raise ValueError("AI module-plan proposal source_root must be a non-empty string when provided.")
        source_root = raw_source_root.strip()
    modules = proposal.get("modules")
    if isinstance(modules, (str, bytes, bytearray)) or not isinstance(modules, Sequence):
        raise ValueError("AI module-plan proposal modules must be a JSON array.")
    if not modules:
        raise ValueError("AI module-plan proposal must contain at least one module.")
    if len(modules) > _MAX_AI_CHAT_PROPOSAL_MODULES:
        raise ValueError(f"AI module-plan proposal cannot contain more than {_MAX_AI_CHAT_PROPOSAL_MODULES} modules.")

    requests: list[dict[str, object]] = []
    family_id = ""
    seen_modules: set[tuple[str, str]] = set()
    for index, value in enumerate(modules):
        request = _chat_module_plan_mapping(
            value,
            f"AI module-plan request {index}",
            frozenset({"template_id", "object_id", "values"}),
        )
        template_id = request.get("template_id")
        if not isinstance(template_id, str) or not template_id.strip():
            raise ValueError(f"AI module-plan request {index} requires a non-empty template_id.")
        clean_template_id = template_id.strip()
        template = templates.get(clean_template_id)
        if template is None:
            raise ValueError(f"AI module-plan request {index} uses unknown or unavailable template_id {clean_template_id!r}.")
        if template.get("kind", "module") != "module":
            raise ValueError(f"AI module-plan request {index} requires a module template, not {clean_template_id!r}.")
        template_family = template.get("family")
        if not isinstance(template_family, str) or not template_family:
            raise RuntimeError(f"Authoring template {clean_template_id!r} has no family.")
        if family_id and template_family != family_id:
            raise ValueError("AI module-plan proposal must use templates from exactly one module family.")
        family_id = template_family

        object_id = request.get("object_id")
        if not isinstance(object_id, str) or not object_id.strip():
            raise ValueError(f"AI module-plan request {index} requires a non-empty object_id.")
        clean_object_id = object_id.strip()
        module_key = (template_family, unicodedata.normalize("NFC", clean_object_id).casefold())
        if module_key in seen_modules:
            raise ValueError(f"AI module-plan proposal duplicates module id {template_family}/{clean_object_id}.")
        seen_modules.add(module_key)

        raw_values = request.get("values", {})
        if not isinstance(raw_values, Mapping):
            raise ValueError(f"AI module-plan request {index} values must be a JSON object.")
        template_args = template.get("args")
        if not isinstance(template_args, Mapping):
            raise RuntimeError(f"Authoring template {clean_template_id!r} has invalid arguments.")
        clean_values: dict[str, object] = {}
        for key, item in raw_values.items():
            if not isinstance(key, str) or key not in template_args:
                raise ValueError(f"AI module-plan request {index} uses unknown template value {str(key)!r}.")
            if (
                not isinstance(item, (str, bool, int, float))
                or isinstance(item, float)
                and (not math.isfinite(item) or item.is_integer() and abs(item) > _MAX_SAFE_JSON_INTEGER)
                or isinstance(item, int)
                and not isinstance(item, bool)
                and abs(item) > _MAX_SAFE_JSON_INTEGER
            ):
                raise ValueError(
                    f"AI module-plan request {index} value {key!r} must be a JSON scalar other than null " "(string, boolean, integer, or finite number)."
                )
            clean_values[key] = item
        requests.append(
            {
                "template_id": clean_template_id,
                "object_id": clean_object_id,
                "values": clean_values,
            }
        )

    plan = project.create_modules(
        requests,
        source_root=source_root,
        write=False,
    )
    _require_chat_module_dry_plan(plan, requests, family_id)
    return clean_reply, {
        "schema": _AI_CHAT_PROPOSAL_SCHEMA,
        "operationId": "module.create_batch",
        "familyId": family_id,
        "sourceRoot": str(plan["source_root"]),
        "requests": requests,
        "plan": plan,
    }


def _chat_collection_plan_proposal(
    project: Project,
    value: object,
    templates: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    proposal = _chat_module_plan_mapping(
        value,
        "AI collection-plan proposal",
        frozenset({"operation_id", "source_root", "template_id", "collection_id", "values"}),
    )
    template_id = proposal.get("template_id")
    if not isinstance(template_id, str) or not template_id.strip():
        raise ValueError("AI collection-plan proposal requires a non-empty template_id.")
    clean_template_id = template_id.strip()
    template = templates.get(clean_template_id)
    if template is None:
        raise ValueError(f"AI collection-plan proposal uses unknown or unavailable template_id {clean_template_id!r}.")
    if template.get("kind", "module") != "collection":
        raise ValueError(f"AI collection-plan proposal requires a collection template, not {clean_template_id!r}.")
    family_id = template.get("family")
    if not isinstance(family_id, str) or not family_id:
        raise RuntimeError(f"Authoring template {clean_template_id!r} has no family.")

    collection_id = proposal.get("collection_id")
    if not isinstance(collection_id, str) or not collection_id.strip():
        raise ValueError("AI collection-plan proposal requires a non-empty collection_id.")
    clean_collection_id = collection_id.strip()
    source_root: str | None = None
    if "source_root" in proposal:
        raw_source_root = proposal["source_root"]
        if not isinstance(raw_source_root, str) or not raw_source_root.strip():
            raise ValueError("AI collection-plan proposal source_root must be a non-empty string when provided.")
        source_root = raw_source_root.strip()

    raw_values = proposal.get("values", {})
    if not isinstance(raw_values, Mapping):
        raise ValueError("AI collection-plan proposal values must be a JSON object.")
    template_args = template.get("args")
    if not isinstance(template_args, Mapping):
        raise RuntimeError(f"Authoring template {clean_template_id!r} has invalid arguments.")
    clean_values: dict[str, object] = {}
    for key, item in raw_values.items():
        if not isinstance(key, str) or key not in template_args:
            raise ValueError(f"AI collection-plan proposal uses unknown template value {str(key)!r}.")
        if (
            not isinstance(item, (str, bool, int, float))
            or isinstance(item, float)
            and (not math.isfinite(item) or item.is_integer() and abs(item) > _MAX_SAFE_JSON_INTEGER)
            or isinstance(item, int)
            and not isinstance(item, bool)
            and abs(item) > _MAX_SAFE_JSON_INTEGER
        ):
            raise ValueError(
                f"AI collection-plan proposal value {key!r} must be a JSON scalar other than null " "(string, boolean, integer, or finite number)."
            )
        clean_values[key] = item

    plan = project.scaffold_collection(
        clean_template_id,
        clean_collection_id,
        source_root=source_root,
        values=clean_values,
        write=False,
        force=False,
    )
    _require_chat_collection_dry_plan(
        plan,
        template_id=clean_template_id,
        collection_id=clean_collection_id,
        family_id=family_id,
    )
    plan_values = plan.get("values")
    if not isinstance(plan_values, Mapping) or any(not isinstance(key, str) or not isinstance(item, str) for key, item in plan_values.items()):
        raise RuntimeError("Project.scaffold_collection() returned invalid normalized values.")
    normalized_values = {key: plan_values[key] for key in clean_values if key in plan_values}
    if len(normalized_values) != len(clean_values):
        raise RuntimeError("Project.scaffold_collection() omitted requested normalized values.")
    return {
        "schema": _AI_CHAT_PROPOSAL_SCHEMA,
        "operationId": "collection.scaffold",
        "familyId": family_id,
        "sourceRoot": str(plan["source_root"]),
        "request": {
            "template_id": clean_template_id,
            "collection_id": clean_collection_id,
            "values": dict(normalized_values),
        },
        "plan": plan,
    }


def _chat_source_form_catalog(
    project: Project,
    sources: Sequence[Mapping[str, object]],
) -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    selected_sources = [source for source in sources if source.get("kind") == "source"]
    if not selected_sources:
        raise ValueError("The edit-selection AI role requires at least one selected source file.")
    if len(selected_sources) > _MAX_AI_CHAT_SOURCE_UPDATE_FILES:
        raise ValueError("The edit-selection AI role supports at most " f"{_MAX_AI_CHAT_SOURCE_UPDATE_FILES} selected source files.")

    catalog: dict[str, dict[str, object]] = {}
    prompt_rows: list[dict[str, object]] = []
    total_controls = 0
    for index, source in enumerate(selected_sources):
        if "content" in source:
            raise ValueError("Apply or discard unsaved source drafts before requesting an AI edit proposal.")
        path = source.get("path")
        relative_path = source.get("relativePath")
        if not isinstance(path, str) or not path or not isinstance(relative_path, str) or not relative_path:
            raise RuntimeError(f"Selected AI source {index + 1} has no canonical project path.")
        if relative_path in catalog:
            raise ValueError(f"The edit-selection AI role received duplicate source {relative_path!r}.")
        form = project.source_form(path)
        if form is None:
            raise ValueError(f"Selected source {relative_path!r} has no Registry-owned Guided form.")
        family = form.get("family")
        module_id = form.get("module_id")
        source_format = form.get("source_format")
        sections = form.get("sections")
        if (
            not isinstance(family, str)
            or not family
            or not isinstance(module_id, str)
            or not module_id
            or source_format not in {"json", "loc", "pdx"}
            or not isinstance(sections, Sequence)
            or isinstance(sections, (str, bytes, bytearray))
        ):
            raise RuntimeError(f"Selected source {relative_path!r} returned an incomplete Guided form.")
        controls = _chat_source_form_controls(sections, relative_path)
        if not controls:
            raise ValueError(f"Selected source {relative_path!r} has no editable Guided controls.")
        total_controls += len(controls)
        if total_controls > _MAX_AI_CHAT_SOURCE_UPDATE_CONTROLS:
            raise ValueError(
                "The selected Guided forms expose more than " f"{_MAX_AI_CHAT_SOURCE_UPDATE_CONTROLS} editable controls. Select fewer source files."
            )
        control_index = {str(control["id"]): control for control in controls}
        coverage = form.get("coverage")
        clean_coverage = (
            dict(coverage)
            if isinstance(coverage, Mapping)
            else {
                "truncated": False,
                "shown_controls": len(controls),
                "total_controls": len(controls),
            }
        )
        catalog[relative_path] = {
            "path": path,
            "source_path": relative_path,
            "family": family,
            "module_id": module_id,
            "source_format": source_format,
            "coverage": clean_coverage,
            "controls": control_index,
        }
        prompt_rows.append(
            {
                "source_path": relative_path,
                "module_id": module_id,
                "family": family,
                "source_format": source_format,
                "coverage": clean_coverage,
                "controls": controls,
            }
        )
    return catalog, {
        "operation_id": "module.source_form_update_batch",
        "maximum_files": _MAX_AI_CHAT_SOURCE_UPDATE_FILES,
        "sources": prompt_rows,
    }


def _chat_source_form_controls(
    sections: Sequence[object],
    relative_path: str,
) -> list[dict[str, object]]:
    controls: list[dict[str, object]] = []
    stack = list(reversed(sections))
    seen_ids: set[str] = set()
    while stack:
        section = stack.pop()
        if not isinstance(section, Mapping):
            raise RuntimeError(f"Selected source {relative_path!r} returned an invalid Guided section.")
        child_sections = section.get("sections", ())
        if isinstance(child_sections, (str, bytes, bytearray)) or not isinstance(
            child_sections,
            Sequence,
        ):
            raise RuntimeError(f"Selected source {relative_path!r} returned invalid nested Guided sections.")
        stack.extend(reversed(child_sections))
        section_controls = section.get("controls", ())
        if isinstance(section_controls, (str, bytes, bytearray)) or not isinstance(
            section_controls,
            Sequence,
        ):
            raise RuntimeError(f"Selected source {relative_path!r} returned invalid Guided controls.")
        for control in section_controls:
            if not isinstance(control, Mapping):
                raise RuntimeError(f"Selected source {relative_path!r} returned an invalid Guided control.")
            control_id = control.get("id")
            control_kind = control.get("control")
            if control_kind == "readonly":
                continue
            if (
                not isinstance(control_id, str)
                or not control_id
                or control_id in seen_ids
                or control_kind not in {"text", "number", "boolean", "choice"}
                or "patch" not in control
            ):
                raise RuntimeError(f"Selected source {relative_path!r} returned an invalid editable Guided control.")
            seen_ids.add(control_id)
            prompt_control: dict[str, object] = {
                "id": control_id,
                "label": _chat_source_form_text(
                    control.get("label"),
                    f"Guided control {control_id!r} label",
                ),
                "control": control_kind,
                "current": _chat_proposal_scalar(
                    control.get("value"),
                    f"Guided control {control_id!r} current value",
                ),
            }
            for key in ("description", "description_source", "min", "max", "step"):
                if key not in control:
                    continue
                value = control[key]
                prompt_control[key] = (
                    _chat_source_form_text(
                        value,
                        f"Guided control {control_id!r} {key}",
                    )
                    if key == "description"
                    else value
                )
            choices = control.get("choices")
            if choices is not None:
                if isinstance(choices, (str, bytes, bytearray)) or not isinstance(
                    choices,
                    Sequence,
                ):
                    raise RuntimeError(f"Guided control {control_id!r} returned invalid choices.")
                prompt_choices: list[dict[str, object]] = []
                for choice in choices:
                    if not isinstance(choice, Mapping):
                        raise RuntimeError(f"Guided control {control_id!r} returned an invalid choice.")
                    prompt_choices.append(
                        {
                            "label": _chat_source_form_text(
                                choice.get("label"),
                                f"Guided control {control_id!r} choice label",
                            ),
                            "value": _chat_proposal_scalar(
                                choice.get("value"),
                                f"Guided control {control_id!r} choice value",
                            ),
                        }
                    )
                prompt_control["choices"] = prompt_choices
            controls.append(prompt_control)
    return controls


def _chat_source_form_text(value: object, label: str) -> object:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, Mapping):
        clean = {key.strip(): item.strip() for key, item in value.items() if isinstance(key, str) and key.strip() and isinstance(item, str) and item.strip()}
        if clean:
            return clean
    raise RuntimeError(f"{label} must be non-empty localized text.")


def _chat_source_update_prompt(
    prompt: str,
    source_catalog: Mapping[str, object],
) -> str:
    contract = (
        "Return exactly one JSON object with keys `reply` and `proposal`. "
        "`reply` must be a concise user-facing string. Use `proposal: null` when no concrete edit was requested. "
        "An edit proposal must be "
        '{"operation_id":"module.source_form_update_batch","updates":['
        '{"source_path":"exact catalog source_path","values":{"exact control id":"JSON scalar"}}]}. '
        "Use only source paths and editable control ids from the catalog. Treat control type, current value, label, description, bounds, and choices as authoritative. "
        "Values may be strings, booleans, safe integers, or finite numbers; never use null, arrays, or objects. "
        "Do not include source text, write, force, plan hashes, revision fields, or any other field. "
        "This response requests a guarded dry plan and never writes files."
    )
    return "\n\n".join(
        (
            prompt,
            contract,
            "Authoritative Registry-owned Guided source catalog:\n" + dumps_json(source_catalog, indent=2),
        )
    )


def _chat_source_update_response(
    project: Project,
    value: object,
    source_catalog: Mapping[str, Mapping[str, object]],
) -> tuple[str, dict[str, object] | None]:
    response = _chat_module_plan_mapping(
        value,
        "AI source-update response",
        frozenset({"reply", "proposal"}),
    )
    missing = sorted({"reply", "proposal"} - set(response))
    if missing:
        raise ValueError("AI source-update response is missing required fields: " f"{', '.join(missing)}.")
    reply = response.get("reply")
    if not isinstance(reply, str) or not reply.strip():
        raise ValueError("AI source-update response requires a non-empty reply string.")
    clean_reply = reply.strip()
    proposal_value = response.get("proposal")
    if proposal_value is None:
        return clean_reply, None
    proposal = _chat_module_plan_mapping(
        proposal_value,
        "AI source-update proposal",
        frozenset({"operation_id", "updates"}),
    )
    if proposal.get("operation_id") != "module.source_form_update_batch":
        raise ValueError("AI source-update proposal operation_id must be " "'module.source_form_update_batch'.")
    updates = proposal.get("updates")
    if isinstance(updates, (str, bytes, bytearray)) or not isinstance(
        updates,
        Sequence,
    ):
        raise ValueError("AI source-update proposal updates must be a JSON array.")
    if not updates:
        raise ValueError("AI source-update proposal must contain at least one update.")
    if len(updates) > _MAX_AI_CHAT_SOURCE_UPDATE_FILES:
        raise ValueError("AI source-update proposal cannot contain more than " f"{_MAX_AI_CHAT_SOURCE_UPDATE_FILES} updates.")

    planner_updates: list[dict[str, object]] = []
    review_requests: list[dict[str, object]] = []
    seen_paths: set[str] = set()
    family_id = ""
    for index, update_value in enumerate(updates):
        update = _chat_module_plan_mapping(
            update_value,
            f"AI source-update request {index}",
            frozenset({"source_path", "values"}),
        )
        source_path = update.get("source_path")
        if not isinstance(source_path, str) or not source_path.strip():
            raise ValueError(f"AI source-update request {index} requires a non-empty source_path.")
        clean_source_path = source_path.strip()
        source = source_catalog.get(clean_source_path)
        if source is None:
            raise ValueError(f"AI source-update request {index} uses unknown or unselected " f"source_path {clean_source_path!r}.")
        if clean_source_path in seen_paths:
            raise ValueError(f"AI source-update proposal repeats source_path {clean_source_path!r}.")
        seen_paths.add(clean_source_path)
        source_family = source.get("family")
        if not isinstance(source_family, str) or not source_family:
            raise RuntimeError(f"Guided source catalog row {clean_source_path!r} has no family.")
        if family_id and source_family != family_id:
            raise ValueError("AI source-update proposal must target exactly one module family.")
        family_id = source_family
        controls = source.get("controls")
        if not isinstance(controls, Mapping):
            raise RuntimeError(f"Guided source catalog row {clean_source_path!r} has invalid controls.")
        raw_values = update.get("values")
        if not isinstance(raw_values, Mapping) or not raw_values:
            raise ValueError(f"AI source-update request {index} values must be a non-empty JSON object.")
        clean_values: dict[str, object] = {}
        control_labels: dict[str, object] = {}
        for control_id, replacement in raw_values.items():
            if not isinstance(control_id, str) or control_id not in controls:
                raise ValueError(f"AI source-update request {index} uses unknown Guided control " f"{str(control_id)!r}.")
            clean_values[control_id] = _chat_proposal_scalar(
                replacement,
                f"AI source-update request {index} value {control_id!r}",
            )
            control = controls[control_id]
            if not isinstance(control, Mapping):
                raise RuntimeError(f"Guided source control {control_id!r} is invalid.")
            control_labels[control_id] = control["label"]
        planner_updates.append(
            {
                "source_path": source["path"],
                "values": clean_values,
            }
        )
        review_requests.append(
            {
                "source_path": clean_source_path,
                "module_id": source["module_id"],
                "values": clean_values,
                "control_labels": control_labels,
            }
        )

    plan = project.plan_source_form_updates(planner_updates)
    _require_chat_source_update_dry_plan(
        plan,
        requests=review_requests,
        family_id=family_id,
    )
    return clean_reply, {
        "schema": _AI_CHAT_PROPOSAL_SCHEMA,
        "operationId": "module.source_form_update_batch",
        "familyId": family_id,
        "requests": review_requests,
        "plan": plan,
    }


def _chat_proposal_scalar(value: object, label: str) -> str | bool | int | float:
    if isinstance(value, (str, bool)):
        return value
    if isinstance(value, int):
        if abs(value) <= _MAX_SAFE_JSON_INTEGER:
            return value
        raise ValueError(f"{label} must be a safe JSON integer.")
    if isinstance(value, float):
        if math.isfinite(value) and (not value.is_integer() or abs(value) <= _MAX_SAFE_JSON_INTEGER):
            return value
        raise ValueError(f"{label} must be a finite safe JSON number.")
    raise ValueError(f"{label} must be a JSON scalar other than null " "(string, boolean, integer, or finite number).")


def _require_chat_source_update_dry_plan(
    plan: Mapping[str, object],
    *,
    requests: Sequence[Mapping[str, object]],
    family_id: str,
) -> None:
    if plan.get("schema") != "paradev.source-form-update-batch.v1":
        raise RuntimeError("Project.plan_source_form_updates() returned an unsupported schema.")
    updates = plan.get("updates")
    source_edits = plan.get("source_edits")
    counts = plan.get("counts")
    if (
        isinstance(updates, (str, bytes, bytearray))
        or not isinstance(updates, Sequence)
        or len(updates) != len(requests)
        or isinstance(source_edits, (str, bytes, bytearray))
        or not isinstance(source_edits, Sequence)
        or not isinstance(counts, Mapping)
        or counts.get("requested") != len(requests)
    ):
        raise RuntimeError("Project.plan_source_form_updates() returned an inconsistent batch.")
    changed = 0
    for index, (request, update) in enumerate(zip(requests, updates)):
        if not isinstance(update, Mapping):
            raise RuntimeError(f"Project.plan_source_form_updates() returned an invalid row at index {index}.")
        if (
            update.get("family") != family_id
            or update.get("module_id") != request.get("module_id")
            or update.get("relative_path") != request.get("source_path")
        ):
            raise RuntimeError(f"Project.plan_source_form_updates() row {index} does not match the proposal.")
        changes = update.get("changes")
        if isinstance(changes, (str, bytes, bytearray)) or not isinstance(
            changes,
            Sequence,
        ):
            raise RuntimeError(f"Project.plan_source_form_updates() row {index} has invalid changes.")
        changed += int(bool(update.get("changed")))
        requested_values = request.get("values")
        if not isinstance(requested_values, Mapping):
            raise RuntimeError(f"AI source-update request {index} has invalid normalized values.")
        for change in changes:
            if not isinstance(change, Mapping):
                raise RuntimeError(f"Project.plan_source_form_updates() row {index} has an invalid change.")
            control_id = change.get("control_id")
            if not isinstance(control_id, str) or control_id not in requested_values or change.get("value") != requested_values[control_id]:
                raise RuntimeError(f"Project.plan_source_form_updates() row {index} change does not match the proposal.")
    if (
        counts.get("changed") != changed
        or counts.get("unchanged") != len(requests) - changed
        or len(source_edits) != changed
        or plan.get("changed") is not bool(changed)
    ):
        raise RuntimeError("Project.plan_source_form_updates() returned inconsistent change counts.")


def _chat_module_plan_mapping(
    value: object,
    label: str,
    allowed_fields: frozenset[str],
) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object.")
    unknown_fields = sorted(str(key) for key in value if not isinstance(key, str) or key not in allowed_fields)
    if unknown_fields:
        raise ValueError(f"{label} has unsupported fields: {', '.join(unknown_fields)}.")
    return value


def _require_chat_module_dry_plan(
    plan: Mapping[str, object],
    requests: Sequence[Mapping[str, object]],
    family_id: str,
) -> None:
    if plan.get("applied") is not False or plan.get("written") is not False:
        raise RuntimeError("Project.create_modules(..., write=False) returned a non-dry module plan.")
    if plan.get("requested_count") != len(requests):
        raise RuntimeError("Project.create_modules() returned a module count that does not match the proposal.")
    source_root = plan.get("source_root")
    if not isinstance(source_root, str) or not source_root:
        raise RuntimeError("Project.create_modules() returned an invalid source root.")
    rows = plan.get("modules")
    if isinstance(rows, (str, bytes, bytearray)) or not isinstance(rows, Sequence) or len(rows) != len(requests):
        raise RuntimeError("Project.create_modules() returned modules that do not match the proposal.")
    for index, (request, row) in enumerate(zip(requests, rows)):
        if not isinstance(row, Mapping):
            raise RuntimeError(f"Project.create_modules() returned an invalid module row at index {index}.")
        if row.get("template_id") != request["template_id"] or row.get("object_id") != request["object_id"] or row.get("family") != family_id:
            raise RuntimeError(f"Project.create_modules() module row {index} does not match the proposal.")
        plan_values = row.get("values")
        if not isinstance(plan_values, Mapping):
            raise RuntimeError(f"Project.create_modules() module row {index} has invalid values.")
        request_values = request["values"]
        if not isinstance(request_values, Mapping):
            raise RuntimeError(f"AI module-plan request {index} has invalid normalized values.")
        for key, value in request_values.items():
            if plan_values.get(key) != str(value):
                raise RuntimeError(f"Project.create_modules() module row {index} value {key!r} does not match the proposal.")


def _require_chat_collection_dry_plan(
    plan: Mapping[str, object],
    *,
    template_id: str,
    collection_id: str,
    family_id: str,
) -> None:
    if plan.get("schema") != "paradev.sdk.collection_scaffold.v1":
        raise RuntimeError("Project.scaffold_collection() returned an unsupported plan schema.")
    if plan.get("kind") != "collection" or plan.get("written") is not False or plan.get("blocked") not in {True, False}:
        raise RuntimeError("Project.scaffold_collection(..., write=False) returned a non-dry collection plan.")
    if (
        plan.get("template_id") != template_id
        or plan.get("collection_id") != collection_id
        or plan.get("object_id") != collection_id
        or plan.get("family") != family_id
    ):
        raise RuntimeError("Project.scaffold_collection() returned collection identity that does not match the proposal.")
    source_root = plan.get("source_root")
    if not isinstance(source_root, str) or not source_root:
        raise RuntimeError("Project.scaffold_collection() returned an invalid source root.")
    plan_hash = plan.get("plan_hash")
    if not isinstance(plan_hash, str) or len(plan_hash) != 64:
        raise RuntimeError("Project.scaffold_collection() returned an invalid plan hash.")


def _chat_profile(role: str, project_root: str = "") -> Mapping[str, object]:
    for profile in _chat_profiles(project_root):
        if profile["id"] == role:
            return profile
    supported = ", ".join(str(profile["id"]) for profile in AI_CHAT_PROFILE_ROWS)
    raise ValueError(f"Unsupported AI chat role: {role}. Supported roles: {supported}.")


def _chat_profiles(project_root: str = "") -> list[dict[str, object]]:
    overrides = _chat_profile_overrides(project_root)
    profiles: list[dict[str, object]] = []
    for profile in AI_CHAT_PROFILE_ROWS:
        profile_id = str(profile["id"])
        override = overrides.get(profile_id, {})
        merged = dict(profile)
        merged.update(override)
        if "label" in override:
            merged.pop("labelKey", None)
        if "detail" in override:
            merged.pop("detailKey", None)
        if "prompt" in override:
            merged.pop("promptKey", None)
        merged["id"] = profile_id
        profiles.append(_chat_profile_with_operation_cards(merged))
    return profiles


def _base_chat_profiles() -> list[dict[str, object]]:
    return [_chat_profile_with_operation_cards(profile) for profile in AI_CHAT_PROFILE_ROWS]


def _chat_profile_with_operation_cards(profile: Mapping[str, object]) -> dict[str, object]:
    merged = dict(profile)
    operation_cards = _chat_profile_operation_cards(merged)
    if operation_cards:
        merged["operationCards"] = operation_cards
    return merged


def _chat_profile_operation_cards(profile: Mapping[str, object]) -> list[dict[str, object]]:
    from paradev.sdk import get_frontend_api_action

    operation_ids = profile.get("operationIds", [])
    if isinstance(operation_ids, (str, bytes, bytearray)) or not isinstance(operation_ids, Sequence):
        return []
    cards: list[dict[str, object]] = []
    for operation_id in operation_ids:
        action_detail = get_frontend_api_action(str(operation_id))
        operation = action_detail["operation"]
        action = action_detail["action"]
        bindings = operation.get("bindings", {}) if isinstance(operation, Mapping) else {}
        sdk_label = _chat_operation_sdk_label(operation, bindings)
        rest_label = _chat_operation_rest_label(operation, bindings)
        cards.append(
            {
                "id": str(operation_id),
                "title": str(action.get("title") or operation_id) if isinstance(action, Mapping) else str(operation_id),
                "summary": str(operation.get("summary", "")) if isinstance(operation, Mapping) else "",
                "mutates": operation.get("mutates") is True if isinstance(operation, Mapping) else False,
                "sdk": sdk_label,
                "rest": rest_label,
            }
        )
    return cards


def _chat_operation_sdk_label(operation: Mapping[str, object], bindings: object) -> str:
    if isinstance(bindings, Mapping):
        sdk_binding = bindings.get("sdk", {})
        if isinstance(sdk_binding, Mapping) and isinstance(sdk_binding.get("call"), str):
            return str(sdk_binding["call"])
    return str(operation.get("sdk", ""))


def _chat_operation_rest_label(operation: Mapping[str, object], bindings: object) -> str:
    if isinstance(bindings, Mapping):
        rest_binding = bindings.get("rest", {})
        if isinstance(rest_binding, Mapping) and rest_binding.get("method") and rest_binding.get("path"):
            return f"{rest_binding['method']} {rest_binding['path']}"
    return str(operation.get("rest", ""))


def _clean_chat_project_root(project_root: str) -> str:
    return project_root.strip() if isinstance(project_root, str) else ""


def _chat_profile_overrides(project_root: str = "") -> dict[str, dict[str, object]]:
    global_profiles, project_profiles = _chat_profile_override_catalog()
    clean_project_root = _clean_chat_project_root(project_root)
    if not clean_project_root:
        return global_profiles
    merged_profiles = dict(global_profiles)
    merged_profiles.update(project_profiles.get(clean_project_root, {}))
    return merged_profiles


def _chat_profile_override_catalog() -> tuple[dict[str, dict[str, object]], dict[str, dict[str, dict[str, object]]]]:
    raw = CM_PARADEV.get(AI_CHAT_PROFILES_CONFIG_KEY, default=None)
    if raw is None:
        return {}, {}
    if not isinstance(raw, Mapping):
        raise ValueError("AI chat profile overrides must be a JSON object.")
    if raw.get("__HB_REMOVE__") is True:
        return {}, {}
    schema = raw.get("schema")
    if schema != AI_CHAT_PROFILES_CONFIG_SCHEMA:
        raise ValueError(f"AI chat profile overrides must use schema {AI_CHAT_PROFILES_CONFIG_SCHEMA}.")
    global_profiles = _chat_profile_override_map(raw.get("profiles", {}), "AI chat profile overrides")
    projects_raw = raw.get("projects", {})
    if not isinstance(projects_raw, Mapping):
        raise ValueError("AI chat profile overrides projects must be a JSON object.")
    project_profiles: dict[str, dict[str, dict[str, object]]] = {}
    for project_root, project_payload in projects_raw.items():
        clean_project_root = _clean_chat_project_root(str(project_root))
        if not clean_project_root:
            raise ValueError("AI chat profile project root cannot be empty.")
        if not isinstance(project_payload, Mapping):
            raise ValueError("AI chat profile project override must be a JSON object.")
        profiles = _chat_profile_override_map(project_payload.get("profiles", {}), "AI chat profile project overrides")
        if profiles:
            project_profiles[clean_project_root] = profiles
    return global_profiles, project_profiles


def _write_chat_profile_override_catalog(
    global_profiles: Mapping[str, Mapping[str, object]], project_profiles: Mapping[str, Mapping[str, Mapping[str, object]]]
) -> None:
    clean_global_profiles = {str(profile_id): dict(override) for profile_id, override in global_profiles.items() if override}
    clean_project_profiles = {
        clean_project_root: {"profiles": {str(profile_id): dict(override) for profile_id, override in profiles.items() if override}}
        for project_root, profiles in project_profiles.items()
        if (clean_project_root := _clean_chat_project_root(str(project_root))) and profiles
    }
    if not clean_global_profiles and not clean_project_profiles:
        CM_PARADEV.unset(AI_CHAT_PROFILES_CONFIG_KEY)
        return
    payload: dict[str, object] = {
        "schema": AI_CHAT_PROFILES_CONFIG_SCHEMA,
        "profiles": clean_global_profiles,
    }
    if clean_project_profiles:
        payload["projects"] = clean_project_profiles
    CM_PARADEV.set(AI_CHAT_PROFILES_CONFIG_KEY, payload)


def _chat_profile_override_map(value: object, label: str) -> dict[str, dict[str, object]]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must include a profiles object.")
    return {_chat_profile_id(str(profile_id)): _chat_profile_override(str(profile_id), override) for profile_id, override in value.items()}


def _chat_profile_id(profile_id: str) -> str:
    clean_profile_id = _required_text(profile_id, "AI chat profile id")
    if clean_profile_id not in {str(profile["id"]) for profile in AI_CHAT_PROFILE_ROWS}:
        supported = ", ".join(str(profile["id"]) for profile in AI_CHAT_PROFILE_ROWS)
        raise ValueError(f"Unsupported AI chat role: {clean_profile_id}. Supported roles: {supported}.")
    return clean_profile_id


def _default_ai_chat_role() -> str:
    value = _desktop_config_raw_value("paradev.ai.chat.default_role")
    return str(_desktop_config_value("paradev.ai.chat.default_role", value))


def _chat_profile_override(profile_id: str, profile: object) -> dict[str, object]:
    if not isinstance(profile, Mapping):
        raise ValueError("AI chat profile override must be a JSON object.")
    _chat_profile_id(profile_id)
    clean: dict[str, object] = {}
    for key, value in profile.items():
        if key == "id":
            if str(value) != profile_id:
                raise ValueError("AI chat profile override id must match the selected profile id.")
            continue
        if key in {"label", "detail", "prompt"}:
            clean[key] = _required_text(value, f"AI chat profile {key}") if isinstance(value, str) else ""
            if not clean[key]:
                raise ValueError(f"AI chat profile {key} cannot be empty.")
            continue
        if key == "sourceKinds":
            clean[key] = _chat_profile_source_kinds(value)
            continue
        raise ValueError(f"Unsupported AI chat profile field: {key}.")
    return clean


def _chat_profile_source_kinds(value: object) -> list[str]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise ValueError("AI chat profile sourceKinds must be a list of strings.")
    source_kinds: list[str] = []
    for index, item in enumerate(value):
        clean = item.strip() if isinstance(item, str) else ""
        if not clean:
            raise ValueError(f"AI chat profile sourceKinds entry {index + 1} cannot be empty.")
        if clean not in AI_CHAT_SOURCE_KIND_VALUES:
            supported = ", ".join(AI_CHAT_SOURCE_KIND_VALUES)
            raise ValueError(f"Unsupported AI chat source kind: {clean}. Supported source kinds: {supported}.")
        source_kinds.append(clean)
    return source_kinds


def _chat_prompt(profile: Mapping[str, object], project_root: str, prompt: str, source_contexts: Sequence[str]) -> str:
    parts = [str(profile["label"]), str(profile["prompt"])]
    if project_root:
        parts.append(f"Active ParaDev project: {project_root}")
    if source_contexts:
        parts.append("Attached sources:\n" + "\n\n".join(source_contexts))
    parts.extend(("User request:", prompt))
    return "\n\n".join(parts)


def _chat_sources(project_root: str, sources: Sequence[Mapping[str, object]] | None) -> tuple[list[dict[str, object]], list[str]]:
    if sources is None:
        return [], []
    if isinstance(sources, (str, bytes, bytearray)) or not isinstance(sources, Sequence):
        raise ValueError("AI chat sources must be a list of JSON objects.")
    clean_sources: list[dict[str, object]] = []
    contexts: list[str] = []
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            raise ValueError("AI chat source entries must be JSON objects.")
        clean_source, context = _chat_source(project_root, source, index)
        clean_sources.append(clean_source)
        if context:
            contexts.append(context)
    return clean_sources, contexts


def _chat_source(project_root: str, source: Mapping[str, object], index: int) -> tuple[dict[str, object], str]:
    kind = _required_text(source.get("kind"), f"AI chat source {index + 1} kind") if isinstance(source.get("kind"), str) else ""
    if not kind:
        raise ValueError("AI chat source kind cannot be empty.")
    label = _chat_source_text(source, "label") or kind
    clean: dict[str, object] = {"kind": kind, "label": label}
    for key in ("familyId", "moduleId", "entityId"):
        if value := _chat_source_text(source, key):
            clean[key] = value
    if detail := _chat_source_text(source, "detail"):
        clean["detail"] = detail
    metadata_content = _chat_source_content_text(source)
    if metadata_content is not None:
        content, truncated = _chat_source_content(metadata_content)
        clean["content"] = content
        clean["contentChars"] = len(metadata_content)
        clean["truncated"] = truncated or source.get("truncated") is True
    source_path = _chat_source_text(source, "path") or _chat_source_text(source, "sourcePath")
    if kind == "source" or source_path:
        if not source_path:
            raise ValueError("AI chat source path cannot be empty.")
        if not project_root:
            raise ValueError("AI chat source path requires an active project root.")
        path = desktop_source_path(project_root, source_path)
        text = metadata_content if metadata_content is not None else desktop_read_text_source(project_root, path)
        relative_path = path.relative_to(Path(project_root).resolve(strict=True)).as_posix()
        content, truncated = _chat_source_content(text)
        path_payload = {
            "path": str(path),
            "relativePath": relative_path,
            "contentChars": len(text),
            "truncated": truncated,
        }
        if metadata_content is not None:
            path_payload["content"] = content
        clean.update(path_payload)
        return clean, _chat_source_file_context(label, relative_path, content, truncated)
    return clean, _chat_source_metadata_context(clean)


def _chat_source_text(source: Mapping[str, object], key: str) -> str:
    value = source.get(key)
    return value.strip() if isinstance(value, str) else ""


def _chat_source_content_text(source: Mapping[str, object]) -> str | None:
    value = source.get("content")
    return value if isinstance(value, str) else None


def _chat_source_content(text: str) -> tuple[str, bool]:
    if len(text) <= MAX_AI_CHAT_SOURCE_CHARS:
        return text, False
    return text[:MAX_AI_CHAT_SOURCE_CHARS], True


def _chat_source_file_context(label: str, relative_path: str, content: str, truncated: bool) -> str:
    suffix = "\n[truncated]" if truncated else ""
    return f"Source: {label}\nPath: {relative_path}\n```text\n{content}{suffix}\n```"


def _chat_source_metadata_context(source: Mapping[str, object]) -> str:
    content = source.get("content")
    fields = [f"{key}: {value}" for key, value in source.items() if key not in {"content", "kind"}]
    suffix = "\n".join(fields) if fields else "No additional metadata."
    if isinstance(content, str) and content:
        truncated = "\n[truncated]" if source.get("truncated") is True else ""
        suffix = f"{suffix}\n```text\n{content}{truncated}\n```"
    return f"Context: {source['kind']}\n{suffix}"


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
