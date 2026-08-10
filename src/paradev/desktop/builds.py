"""Desktop build lifecycle facade shared by Python and native-web surfaces."""

from __future__ import annotations

import atexit
import os
import signal
import subprocess
import sys
import tempfile
import time
import uuid
import warnings
from collections.abc import Mapping
from pathlib import Path
from threading import Lock
from typing import Any, cast

from heavenbase.utils import deepcopy, loads_json

from .shell import desktop_project_build_command

BUILD_RUN_SCHEMA = "paradev.desktop.build-run.v1"
BUILD_RUNS_SCHEMA = "paradev.desktop.build-runs.v1"
_BUILD_TERMINATION_GRACE_SECONDS = 2.0
_BUILD_REAP_POLL_SECONDS = 0.02
_BUILD_TERMINAL_RETENTION_LIMIT = 256
_DesktopBuildProjectKey = tuple[str, tuple[int, int] | None]


class DesktopBuildRegistry:
    """In-process registry for desktop build runs.

    The native-web bridge is hosted by a long-lived Python process, so it can
    use this registry directly and keep process ownership in one place.
    """

    def __init__(self) -> None:
        self._processes: dict[str, dict[str, object]] = {}
        self._finished: dict[str, dict[str, object]] = {}
        self._finished_project_keys: dict[str, _DesktopBuildProjectKey] = {}
        self._finished_sequences: dict[str, int] = {}
        self._next_terminal_sequence = 0
        self._closed = False
        self._lock = Lock()

    def start(
        self,
        project_root: str | Path,
        *,
        mode: str | None = None,
        profile: str | None = None,
        strict_metadata: bool | None = None,
        parallelism: int | None = None,
        target: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        """Start a ParaDev project build.

        Args:
            project_root: Project root passed to `paradev build`.
            mode: Build mode, either `cached` or `full`.
            profile: Optional build profile.
            strict_metadata: Whether unknown metadata blocks the build.
            parallelism: Optional build worker count.
            target: Optional partial-build target mapping.

        Returns:
            JSON-safe running `paradev.desktop.build-run.v1` payload.

        Raises:
            OSError: If the build process or output files cannot be created.
            RuntimeError: If this registry has been closed.
            ValueError: If the request is invalid or conflicts with an active
                build.
        """

        with self._lock:
            self._reap_finished()
            if self._closed:
                raise RuntimeError("Desktop build registry is closed.")
            project_root_text = _required_text(project_root, "project root")
            project_key = _desktop_build_project_key(project_root_text)
            normalized_target = _desktop_build_target(target)
            project_processes = [record for record in self._processes.values() if _same_desktop_build_project(record.get("project_key"), project_key)]
            if normalized_target is None and project_processes:
                raise ValueError("Cannot start a full ParaDev build while another build is running.")
            if normalized_target is not None and any(record.get("target") is None for record in project_processes):
                raise ValueError("Cannot start a partial ParaDev build while a full build is running.")
            if normalized_target is not None and any(_same_desktop_build_target(record.get("target"), normalized_target) for record in project_processes):
                raise ValueError("A ParaDev build for this target is already running.")

            build_mode = _optional_text(mode, "mode") or "cached"
            run_id = _desktop_run_id()
            output_path = _desktop_build_output_path(f"{run_id}.json")
            error_path = _desktop_build_output_path(f"{run_id}.stderr.log")
            progress_path = _desktop_build_output_path(f"{run_id}.progress.jsonl")
            command = _installed_build_command(
                desktop_project_build_command(
                    project_root_text,
                    mode=build_mode,
                    profile=profile,
                    strict_metadata=strict_metadata,
                    parallelism=parallelism,
                    target=normalized_target,
                    progress_jsonl=progress_path,
                )
            )
            started_at_ms = _unix_time_millis()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            created_paths: list[Path] = []
            try:
                with output_path.open("xb") as stdout:
                    created_paths.append(output_path)
                    with error_path.open("xb") as stderr:
                        created_paths.append(error_path)
                        process = subprocess.Popen(
                            command,
                            cwd=project_root_text,
                            stdout=stdout,
                            stderr=stderr,
                            start_new_session=os.name != "nt",
                        )
            except BaseException:
                _remove_desktop_build_paths(*created_paths)
                raise
            record: dict[str, object] = {
                "command": command,
                "error_path": error_path,
                "mode": build_mode,
                "output_path": output_path,
                "process": process,
                "project_key": project_key,
                "progress_path": progress_path,
                "project_root": project_root_text,
                "run_id": run_id,
                "started_at_ms": started_at_ms,
                "target": normalized_target,
            }
            self._processes[run_id] = record
            return _desktop_build_payload(record, "running")

    def status(self, run_id: str | None = None) -> dict[str, object]:
        """Return one build run status.

        Args:
            run_id: Exact run identifier. When omitted, the oldest active
                build is selected for compatibility with the original facade.

        Returns:
            JSON-safe build-run payload, including a retained terminal payload
            for an exact run id, or an idle payload when no run matches.

        Raises:
            OSError: If the child process cannot be inspected.
            ValueError: If an explicit `run_id` is empty or not text.
        """

        with self._lock:
            self._reap_finished()
            run_id = _optional_text(run_id, "build run id")
            if run_id is not None and run_id in self._finished:
                return deepcopy(self._finished[run_id])
            key = self._select_key(run_id)
            if key is None:
                return _desktop_idle_build_payload()
            record = self._processes[key]
            return _desktop_build_payload(record, "running")

    def runs(self, project_root: str | Path | None = None) -> dict[str, object]:
        """List all active and the newest retained terminal build runs.

        Args:
            project_root: Optional filesystem-equivalent project-root filter.

        Returns:
            JSON-safe `paradev.desktop.build-runs.v1` payload sorted by start
            time and run id. Terminal history retains at most the newest 256
            runs; active runs are never evicted.

        Raises:
            OSError: If a child process cannot be inspected.
            ValueError: If `project_root` is empty or not path-like text.
        """

        with self._lock:
            self._reap_finished()
            project_root_text = _optional_text(project_root, "project root")
            project_key = _desktop_build_project_key(project_root_text) if project_root_text is not None else None
            runs = [
                _desktop_build_payload(record, "running")
                for record in self._processes.values()
                if project_key is None or _same_desktop_build_project(record.get("project_key"), project_key)
            ]
            for run_id, payload in self._finished.items():
                if project_key is None:
                    runs.append(deepcopy(payload))
                    continue
                retained_project_key = self._finished_project_keys.get(run_id)
                if retained_project_key is None:
                    retained_project_key = _desktop_build_project_key(_required_text(payload.get("projectRoot"), "project root"))
                if _same_desktop_build_project(retained_project_key, project_key):
                    runs.append(deepcopy(payload))
            runs.sort(key=lambda payload: (int(payload["startedAtMs"]), str(payload["runId"])))
            return {"schema": BUILD_RUNS_SCHEMA, "runs": runs}

    def interrupt(self, run_id: str | None = None) -> dict[str, object]:
        """Interrupt one build run and retain its final payload.

        Args:
            run_id: Exact run identifier. When omitted, the oldest active
                build is selected for compatibility with the original facade.

        Returns:
            JSON-safe interrupted or already-terminal build-run payload, or an
            idle payload when no run matches.

        Raises:
            OSError: If the child process cannot be signalled or inspected.
            subprocess.SubprocessError: If the child cannot be reaped within
                the bounded termination window.
            ValueError: If an explicit `run_id` is empty or not text.
        """

        with self._lock:
            self._reap_finished()
            run_id = _optional_text(run_id, "build run id")
            if run_id is not None and run_id in self._finished:
                return deepcopy(self._finished[run_id])
            key = self._select_key(run_id)
            if key is None:
                return _desktop_idle_build_payload()
            record = self._processes[key]
            process = cast(Any, record["process"])
            exit_code = _reaped_build_exit_code(process)
            if exit_code is not None:
                return self._retain_terminal(key, "completed" if exit_code == 0 else "failed", exit_code)
            exit_code = _interrupt_and_reap_build_process(process)
            return self._retain_terminal(key, "interrupted", exit_code)

    def close(self) -> None:
        """Stop and reap every active build process.

        The registry becomes permanently closed before signalling children.
        Repeated calls are safe and retry any child whose earlier cleanup
        failed. Once every child is reaped, registry-owned temporary output,
        stderr, and progress files are removed best-effort.

        Raises:
            RuntimeError: If one or more children cannot be stopped and reaped
                within their bounded termination windows.
        """

        with self._lock:
            self._closed = True
            remaining = set(self._processes)
            cleanup_errors: dict[str, str] = {}
            for key in sorted(remaining):
                process = cast(Any, self._processes[key]["process"])
                try:
                    exit_code = _reaped_build_exit_code(process)
                except OSError as error:
                    cleanup_errors[key] = str(error)
                    continue
                if exit_code is not None:
                    self._retain_terminal(key, "completed" if exit_code == 0 else "failed", exit_code)
                    remaining.remove(key)
                    cleanup_errors.pop(key, None)
            for key in sorted(remaining):
                process = cast(Any, self._processes[key]["process"])
                try:
                    _terminate_build_process(process)
                except OSError as error:
                    cleanup_errors[key] = str(error)
            self._reap_interrupted_until(remaining, time.monotonic() + _BUILD_TERMINATION_GRACE_SECONDS, cleanup_errors)
            for key in sorted(remaining):
                process = cast(Any, self._processes[key]["process"])
                try:
                    _kill_build_process(process)
                except OSError as error:
                    cleanup_errors[key] = str(error)
            self._reap_interrupted_until(remaining, time.monotonic() + _BUILD_TERMINATION_GRACE_SECONDS, cleanup_errors)
            if remaining:
                errors = [f"{key}: {cleanup_errors.get(key, 'timed out while reaping child process')}" for key in sorted(remaining)]
                raise RuntimeError("Cannot close ParaDev build registry: " + "; ".join(errors))
            for payload in self._finished.values():
                _remove_desktop_build_temp_files(payload)

    def _select_key(self, run_id: str | None) -> str | None:
        if run_id is not None:
            return run_id if run_id in self._processes else None
        return min(
            self._processes,
            key=lambda key: (int(self._processes[key]["started_at_ms"]), key),
            default=None,
        )

    def _reap_finished(self) -> None:
        for key, record in list(self._processes.items()):
            process = cast(Any, record["process"])
            if (exit_code := _reaped_build_exit_code(process)) is not None:
                self._retain_terminal(key, "completed" if exit_code == 0 else "failed", exit_code)

    def _retain_terminal(self, key: str, status: str, exit_code: int | None) -> dict[str, object]:
        """Move one owned process record into retained terminal history."""

        record = self._processes[key]
        terminal_sequence = self._next_terminal_sequence
        payload = _desktop_build_payload(
            record,
            status,
            exit_code=exit_code,
            finished_at_ms=_unix_time_millis(),
            terminal_sequence=terminal_sequence,
        )
        self._finished[key] = payload
        self._finished_project_keys[key] = cast(_DesktopBuildProjectKey, record["project_key"])
        self._finished_sequences[key] = terminal_sequence
        self._next_terminal_sequence += 1
        self._processes.pop(key)
        self._prune_terminal_history()
        return deepcopy(payload)

    def _prune_terminal_history(self) -> None:
        """Retain only the deterministically newest terminal payloads."""

        overflow = len(self._finished) - _BUILD_TERMINAL_RETENTION_LIMIT
        if overflow <= 0:
            return
        oldest = sorted(
            self._finished,
            key=lambda run_id: (
                self._finished_sequences.get(run_id, -1),
                int(self._finished[run_id].get("finishedAtMs") or 0),
                int(self._finished[run_id].get("startedAtMs") or 0),
                run_id,
            ),
        )[:overflow]
        for run_id in oldest:
            payload = self._finished.pop(run_id)
            self._finished_project_keys.pop(run_id, None)
            self._finished_sequences.pop(run_id, None)
            _remove_desktop_build_temp_files(payload)

    def _reap_interrupted_until(self, remaining: set[str], deadline: float, errors: dict[str, str]) -> None:
        """Poll a shutdown cohort until every child exits or the shared deadline passes."""

        while remaining:
            for key in sorted(remaining):
                process = cast(Any, self._processes[key]["process"])
                try:
                    exit_code = _reaped_build_exit_code(process)
                except OSError as error:
                    errors[key] = str(error)
                    continue
                if exit_code is not None:
                    self._retain_terminal(key, "interrupted", exit_code)
                    remaining.remove(key)
                    errors.pop(key, None)
            now = time.monotonic()
            if not remaining or now >= deadline:
                return
            time.sleep(min(_BUILD_REAP_POLL_SECONDS, deadline - now))


_BUILD_REGISTRY: DesktopBuildRegistry | None = None
_BUILD_REGISTRY_OWNER_PID: int | None = None
_BUILD_REGISTRY_ACCESS_LOCK = Lock()


def _module_build_registry() -> DesktopBuildRegistry:
    """Return the current process's lazily created facade registry."""

    global _BUILD_REGISTRY, _BUILD_REGISTRY_OWNER_PID
    current_pid = os.getpid()
    with _BUILD_REGISTRY_ACCESS_LOCK:
        if _BUILD_REGISTRY is None or _BUILD_REGISTRY_OWNER_PID != current_pid:
            _BUILD_REGISTRY = DesktopBuildRegistry()
            _BUILD_REGISTRY_OWNER_PID = current_pid
        return _BUILD_REGISTRY


def _reset_module_build_registry_after_fork() -> None:
    """Drop copied registry state without signalling the parent's children."""

    global _BUILD_REGISTRY, _BUILD_REGISTRY_ACCESS_LOCK, _BUILD_REGISTRY_OWNER_PID
    _BUILD_REGISTRY = None
    _BUILD_REGISTRY_OWNER_PID = None
    _BUILD_REGISTRY_ACCESS_LOCK = Lock()


def _close_module_build_registry_at_exit() -> None:
    """Best-effort cleanup for the registry owned by this interpreter."""

    registry = _BUILD_REGISTRY
    if registry is None or _BUILD_REGISTRY_OWNER_PID != os.getpid():
        return
    try:
        registry.close()
    except Exception as error:  # pragma: no cover - interpreter-exit safety net
        warnings.warn(f"Cannot close ParaDev build registry during interpreter exit: {error}", RuntimeWarning, stacklevel=1)


_register_at_fork = getattr(os, "register_at_fork", None)
if _register_at_fork is not None:
    _register_at_fork(after_in_child=_reset_module_build_registry_after_fork)
atexit.register(_close_module_build_registry_at_exit)


def desktop_start_build(
    project_root: str | Path,
    *,
    mode: str | None = None,
    profile: str | None = None,
    strict_metadata: bool | None = None,
    parallelism: int | None = None,
    target: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Start a ParaDev build through the desktop Python facade.

    Args:
        project_root: Project root passed to `paradev build`.
        mode: Build mode, either `cached` or `full`. Empty values default to
            `cached`.
        profile: Optional build profile.
        strict_metadata: Whether to pass strict metadata flags.
        parallelism: Optional build worker count.
        target: Optional target mapping with `kind`, `id`, and optional
            `family` keys.

    Returns:
        JSON-safe `paradev.desktop.build-run.v1` status payload.
    """

    return _module_build_registry().start(
        project_root,
        mode=mode,
        profile=profile,
        strict_metadata=strict_metadata,
        parallelism=parallelism,
        target=target,
    )


def desktop_build_status(run_id: str | None = None) -> dict[str, object]:
    """Return status for a desktop build run.

    Args:
        run_id: Exact run id, or `None` to select the oldest active run with a
            stable run-id tie-break for compatibility callers.

    Returns:
        JSON-safe active, retained terminal, or idle build-run payload.

    Raises:
        OSError: If an owned child process cannot be inspected.
        ValueError: If an explicit `run_id` is empty or not text.
    """

    return _module_build_registry().status(run_id)


def desktop_build_runs(project_root: str | Path | None = None) -> dict[str, object]:
    """List desktop build runs retained by the Python facade.

    Args:
        project_root: Optional filesystem-equivalent project-root filter.

    Returns:
        JSON-safe `paradev.desktop.build-runs.v1` payload.
    """

    return _module_build_registry().runs(project_root)


def desktop_interrupt_build(run_id: str | None = None) -> dict[str, object]:
    """Interrupt a desktop build run.

    Args:
        run_id: Exact run id, or `None` to select the oldest active run with a
            stable run-id tie-break for compatibility callers.

    Returns:
        JSON-safe interrupted, retained terminal, or idle build-run payload.

    Raises:
        OSError: If an owned child process cannot be signalled or inspected.
        subprocess.SubprocessError: If the owned process group cannot be
            reaped within the bounded termination window.
        ValueError: If an explicit `run_id` is empty or not text.
    """

    return _module_build_registry().interrupt(run_id)


def _desktop_run_id() -> str:
    return f"bridge-build-{uuid.uuid4().hex[:12]}"


def _desktop_build_output_path(name: str) -> Path:
    root = Path(tempfile.gettempdir()) / "paradev-build"
    root.mkdir(parents=True, exist_ok=True)
    return root / name


def _desktop_idle_build_payload() -> dict[str, object]:
    return {
        "schema": BUILD_RUN_SCHEMA,
        "status": "idle",
        "progress": None,
        "terminalSequence": None,
    }


def _desktop_build_payload(
    record: Mapping[str, object],
    status: str,
    *,
    exit_code: int | None = None,
    finished_at_ms: int | None = None,
    terminal_sequence: int | None = None,
) -> dict[str, object]:
    return {
        "schema": BUILD_RUN_SCHEMA,
        "command": list(cast(list[str], record["command"])),
        "errorPath": str(record["error_path"]),
        "errorSummary": _desktop_error_summary(cast(Path, record["error_path"])) if status == "failed" else None,
        "exitCode": exit_code,
        "finishedAtMs": finished_at_ms,
        "mode": str(record["mode"]),
        "outputPath": str(record["output_path"]),
        "progress": _desktop_latest_progress(cast(Path, record["progress_path"])),
        "progressPath": str(record["progress_path"]),
        "projectRoot": str(record["project_root"]),
        "runId": str(record["run_id"]),
        "startedAtMs": int(record["started_at_ms"]),
        "status": status,
        "target": deepcopy(record.get("target")),
        "terminalSequence": terminal_sequence,
    }


def _desktop_latest_progress(path: Path) -> dict[str, object] | None:
    if not path.is_file():
        return None
    try:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError:
        return None
    if not lines:
        return None
    try:
        value = loads_json(lines[-1])
    except (TypeError, ValueError):
        return None
    return dict(value) if isinstance(value, dict) else None


def _desktop_error_summary(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return None
    if not text:
        return None
    return text[-1000:]


def _terminate_build_process(process: Any) -> None:
    pid = getattr(process, "pid", None)
    if os.name != "nt" and isinstance(pid, int):
        try:
            os.killpg(pid, signal.SIGTERM)
            return
        except ProcessLookupError:
            return
        except OSError:
            pass
    process.terminate()


def _kill_build_process(process: Any) -> None:
    pid = getattr(process, "pid", None)
    if os.name != "nt" and isinstance(pid, int):
        try:
            os.killpg(pid, signal.SIGKILL)
            return
        except ProcessLookupError:
            return
        except OSError:
            pass
    process.kill()


def _build_process_group_active(process: Any) -> bool:
    """Return whether a POSIX build process group still has live members."""

    pid = getattr(process, "pid", None)
    if os.name == "nt" or not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.killpg(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # A group that exists but is momentarily unsignalable is still active.
        # Treating EPERM as terminal can publish an interrupted build while one
        # of its descendants continues mutating the output directory.
        return True
    return True


def _reaped_build_exit_code(process: Any) -> int | None:
    """Return the leader exit code only after its whole process group exits."""

    exit_code = process.poll()
    if exit_code is None or _build_process_group_active(process):
        return None
    return int(exit_code)


def _wait_for_build_process_group_exit(process: Any, deadline: float) -> bool:
    """Poll one POSIX process group until it exits or a deadline passes."""

    while _build_process_group_active(process):
        now = time.monotonic()
        if now >= deadline:
            return False
        time.sleep(min(_BUILD_REAP_POLL_SECONDS, deadline - now))
    return True


def _interrupt_and_reap_build_process(process: Any) -> int:
    """Signal one owned build process group and reap it within a fixed bound."""

    termination_deadline = time.monotonic() + _BUILD_TERMINATION_GRACE_SECONDS
    _terminate_build_process(process)
    try:
        exit_code = int(process.wait(timeout=max(0.0, termination_deadline - time.monotonic())))
    except subprocess.TimeoutExpired:
        exit_code = None
    else:
        if _wait_for_build_process_group_exit(process, termination_deadline):
            return exit_code

    kill_deadline = time.monotonic() + _BUILD_TERMINATION_GRACE_SECONDS
    _kill_build_process(process)
    if exit_code is None:
        exit_code = int(process.wait(timeout=max(0.0, kill_deadline - time.monotonic())))
    if not _wait_for_build_process_group_exit(process, kill_deadline):
        raise subprocess.TimeoutExpired("ParaDev build process group", _BUILD_TERMINATION_GRACE_SECONDS)
    return exit_code


def _desktop_build_target(value: Mapping[str, object] | None) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError("build target must be a mapping.")
    target = {
        "kind": _required_text(value.get("kind"), "target.kind"),
        "id": _required_text(value.get("id"), "target.id"),
    }
    if family := _optional_text(value.get("family"), "target.family"):
        target["family"] = family
    return target


def _desktop_build_project_key(project_root: str) -> _DesktopBuildProjectKey:
    """Return a read-only comparable identity for one requested project root."""

    lexical = Path(os.path.abspath(Path(project_root).expanduser()))
    try:
        canonical = lexical.resolve()
    except (OSError, RuntimeError) as error:
        raise ValueError(f"project root could not be resolved safely: {project_root}.") from error
    try:
        metadata = canonical.stat()
    except OSError:
        identity = None
    else:
        identity = (metadata.st_dev, metadata.st_ino)
    return os.path.normcase(str(canonical)), identity


def _same_desktop_build_project(left: object, right: _DesktopBuildProjectKey) -> bool:
    if not isinstance(left, tuple) or len(left) != 2:
        return False
    left_path, left_identity = left
    right_path, right_identity = right
    return left_path == right_path or (left_identity is not None and left_identity == right_identity)


def _same_desktop_build_target(left: object, right: Mapping[str, object]) -> bool:
    if not isinstance(left, Mapping) or left.get("kind") != right.get("kind") or left.get("id") != right.get("id"):
        return False
    if left.get("kind") != "collection":
        return True
    left_family = left.get("family")
    right_family = right.get("family")
    return left_family is None or right_family is None or left_family == right_family


def _remove_desktop_build_temp_files(payload: Mapping[str, object]) -> None:
    """Best-effort removal of files no longer reachable through retained history."""

    paths = [payload.get(field) for field in ("outputPath", "errorPath", "progressPath")]
    _remove_desktop_build_paths(*(Path(path) for path in paths if isinstance(path, str) and path))


def _remove_desktop_build_paths(*paths: Path) -> None:
    """Best-effort removal for one registry-owned build's temporary files."""

    for path in paths:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass


def _required_text(value: object, name: str) -> str:
    if isinstance(value, Path):
        value = str(value)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value.strip()


def _optional_text(value: object, name: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, name)


def _unix_time_millis() -> int:
    return int(time.time() * 1000)


def _installed_build_command(command: list[str]) -> list[str]:
    """Run native-web builds with the Python runtime hosting ParaDev.

    ``desktop_project_build_command`` remains the development command contract
    and therefore starts with ``uv run paradev``. The wheel-hosted app cannot
    assume either command is on ``PATH``; its own interpreter and
    ``paradev.__main__`` are the authoritative installed runtime instead.
    Custom registry commands used by embedders and tests pass through.
    """

    prefix = ["uv", "run", "paradev"]
    if command[: len(prefix)] != prefix:
        return command
    return [sys.executable, "-m", "paradev", *command[len(prefix) :]]
