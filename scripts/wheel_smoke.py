#!/usr/bin/env python3
"""Smoke the installed ParaDev GUI host in a disposable Python runtime."""

# heaven-style-scan: standalone-control-plane

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

EVIDENCE_SCHEMA = "paradev.wheel-gui-smoke.v1"
BUILD_RUN_SCHEMA = "paradev.desktop.build-run.v1"
BUILD_SUMMARY_SCHEMA = "paradev.build.summary.v1"
DESKTOP_STATE_SCHEMA = "paradev.desktop.state.v1"
_TERMINAL_BUILD_STATUSES = frozenset({"completed", "failed", "interrupted"})
_ASSET_PATTERN = re.compile(rb"(?:src|href)=['\"](/assets/[^'\"]+)['\"]")
_OUTPUT_CONTROL_FILES = frozenset({".paradev-publication.json"})


class SmokeError(RuntimeError):
    """Raised when installed GUI smoke evidence is incomplete or unsafe."""


@dataclass(frozen=True)
class BuildSpec:
    """One explicit build requested from the installed GUI host."""

    label: str
    mode: str
    target: dict[str, str] | None = None


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", required=True, type=Path, help="ParaDev wheel to install and smoke.")
    parser.add_argument("--project", required=True, type=Path, help="ParaDev project opened by the installed app.")
    parser.add_argument("--copy-project", action="store_true", help="Build a disposable copy of the project, intended for small CI fixtures.")
    parser.add_argument("--expect-project-id", help="Optional exact project ID expected after discovery.")
    parser.add_argument("--clean", action="store_true", help="Run a clean whole-project build.")
    parser.add_argument("--cached", action="store_true", help="Run a cached whole-project build.")
    parser.add_argument("--family", action="append", default=[], metavar="ID", help="Run a safe partial build for one family; repeatable.")
    parser.add_argument("--module", action="append", default=[], metavar="ID", help="Run a safe partial build for one module; repeatable.")
    parser.add_argument("--workers", type=int, help="Optional build worker count, at least 1.")
    parser.add_argument("--strict-metadata", action="store_true", help="Treat unknown metadata keys as build blockers.")
    parser.add_argument("--timeout-seconds", type=float, default=2400.0, help="Timeout for each build (default: %(default)s).")
    parser.add_argument("--startup-timeout-seconds", type=float, default=60.0, help="Timeout for GUI startup (default: %(default)s).")
    parser.add_argument("--poll-seconds", type=float, default=0.5, help="Build-status polling interval (default: %(default)s).")
    parser.add_argument("--evidence", type=Path, help="Optional new JSON evidence file; existing files are not replaced.")
    parser.add_argument("--uv", default="uv", help=argparse.SUPPRESS)
    parser.add_argument("--python", default=sys.executable, help=argparse.SUPPRESS)
    return parser


def _real_file(path: Path, label: str, *, allow_symlink: bool = False) -> Path:
    if (path.is_symlink() and not allow_symlink) or not path.is_file():
        raise SmokeError(f"{label} must be a regular local file, not a symlink: {path}")
    resolved = path.absolute() if allow_symlink else path.resolve(strict=True)
    if resolved.stat().st_size <= 0:
        raise SmokeError(f"{label} is empty: {resolved}")
    return resolved


def _real_project(path: Path) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise SmokeError(f"project must be a real local directory, not a symlink: {path}")
    resolved = path.resolve(strict=True)
    if not (resolved / "paradev.yaml").is_file():
        raise SmokeError(f"project does not contain paradev.yaml: {resolved}")
    return resolved


def _nonblank(values: Sequence[str], label: str) -> tuple[str, ...]:
    normalized = tuple(value.strip() for value in values)
    if any(not value for value in normalized):
        raise SmokeError(f"{label} IDs must not be empty.")
    if len(set(normalized)) != len(normalized):
        raise SmokeError(f"{label} IDs must not be repeated.")
    return normalized


def _build_specs(args: argparse.Namespace) -> tuple[BuildSpec, ...]:
    families = _nonblank(args.family, "family")
    modules = _nonblank(args.module, "module")
    specs: list[BuildSpec] = []
    if args.clean:
        specs.append(BuildSpec("clean whole project", "full"))
    if args.cached:
        specs.append(BuildSpec("cached whole project", "cached"))
    specs.extend(BuildSpec(f"family {family}", "cached", {"kind": "family", "id": family}) for family in families)
    specs.extend(BuildSpec(f"module {module}", "cached", {"kind": "module", "id": module}) for module in modules)
    return tuple(specs)


def _runtime_environment(*, home: Path, runtime_temp: Path, runtime_bin: Path, mod_root: Path, project: Path) -> dict[str, str]:
    environment = {
        "HOME": str(home),
        "PARADEV_ROOT": str(home / ".paradev"),
        "PARADEV_PROJECTS": str(project),
        "PARADEV_HOI4_MOD_ROOT": str(mod_root),
        "PATH": str(runtime_bin),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUTF8": "1",
        "TMPDIR": str(runtime_temp),
    }
    if os.name == "nt":
        app_data = home / "AppData"
        environment.update(
            {
                "APPDATA": str(app_data / "Roaming"),
                "LOCALAPPDATA": str(app_data / "Local"),
                "TEMP": str(runtime_temp),
                "TMP": str(runtime_temp),
                "USERPROFILE": str(home),
            }
        )
        for name in ("COMSPEC", "PATHEXT", "SystemDrive", "SystemRoot", "WINDIR"):
            if value := os.environ.get(name):
                environment[name] = value
    return environment


def _runtime_executable(venv: Path, name: str) -> Path:
    candidates = (venv / "bin" / name, venv / "Scripts" / f"{name}.exe", venv / "Scripts" / name)
    for candidate in candidates:
        if candidate.is_file():
            # Keep the venv-owned launcher path. Resolving a POSIX Python
            # symlink here would target the base interpreter and install the
            # wheel outside the disposable environment.
            return candidate.absolute()
    raise SmokeError(f"installed runtime is missing {name!r} under {venv}")


def _runtime_identity(
    python: Path,
    *,
    venv: Path,
    environment: Mapping[str, str],
    working_directory: Path,
) -> dict[str, str]:
    program = """
import json
from importlib.metadata import version
from pathlib import Path
import paradev

print(json.dumps({
    "paradev_version": version("paradev"),
    "heavenbase_version": version("heavenbase"),
    "fastmcp_version": version("fastmcp"),
    "mcp_version": version("mcp"),
    "module_path": str(Path(paradev.__file__).resolve()),
}))
"""
    result = subprocess.run(
        [str(python), "-c", program],
        cwd=working_directory,
        env=dict(environment),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
    )
    if result.returncode != 0:
        raise SmokeError(f"installed runtime identity probe failed with exit {result.returncode}: {result.stderr.strip()}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise SmokeError("installed runtime identity probe returned invalid JSON") from error
    if not isinstance(payload, dict):
        raise SmokeError("installed runtime identity probe must return a JSON object")
    module_value = payload.pop("module_path", None)
    if not isinstance(module_value, str):
        raise SmokeError("installed runtime identity probe returned no ParaDev module path")
    module_path = Path(module_value).resolve(strict=True)
    venv_root = venv.resolve(strict=True)
    if venv_root not in module_path.parents:
        raise SmokeError(f"installed runtime imported ParaDev outside the disposable venv: {module_path}")
    expected_keys = {"paradev_version", "heavenbase_version", "fastmcp_version", "mcp_version"}
    if set(payload) != expected_keys or not all(isinstance(value, str) and value for value in payload.values()):
        raise SmokeError(f"installed runtime identity is incomplete: {payload!r}")
    return {**payload, "package_location": "isolated_venv"}


def _run_install(command: Sequence[str], *, label: str, timeout_seconds: float) -> None:
    result = subprocess.run(
        list(command),
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout_seconds,
    )
    if result.returncode == 0:
        return
    detail = (result.stderr or result.stdout).strip()
    raise SmokeError(f"{label} failed with exit {result.returncode}: {detail[-4000:]}")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _http(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: Mapping[str, object] | None = None,
    timeout_seconds: float = 30.0,
) -> tuple[int, Mapping[str, str], bytes]:
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(f"{base_url}{path}", data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310
            return int(response.status), {key.lower(): value for key, value in response.headers.items()}, response.read()
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace").strip()
        raise SmokeError(f"{method} {path} returned HTTP {error.code}: {detail}") from error
    except URLError as error:
        raise SmokeError(f"{method} {path} failed: {error.reason}") from error


def _json_response(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: Mapping[str, object] | None = None,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    status, _headers, body = _http(base_url, path, method=method, payload=payload, timeout_seconds=timeout_seconds)
    if status != 200:
        raise SmokeError(f"{method} {path} returned unexpected HTTP {status}")
    try:
        decoded = json.loads(body)
    except json.JSONDecodeError as error:
        raise SmokeError(f"{method} {path} returned invalid JSON") from error
    if not isinstance(decoded, dict):
        raise SmokeError(f"{method} {path} must return a JSON object")
    return decoded


def _tail(path: Path, limit: int = 8000) -> str:
    try:
        return path.read_bytes()[-limit:].decode("utf-8", errors="replace").strip()
    except OSError:
        return ""


def _wait_for_host(base_url: str, process: subprocess.Popen[bytes], stderr_path: Path, timeout_seconds: float) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise SmokeError(f"installed GUI exited during startup with {process.returncode}: {_tail(stderr_path)}")
        try:
            if _json_response(base_url, "/health", timeout_seconds=2.0).get("status") == "ok":
                return
        except SmokeError:
            time.sleep(0.1)
    raise SmokeError(f"installed GUI did not become healthy within {timeout_seconds:g} seconds: {_tail(stderr_path)}")


def _verify_frontend(base_url: str) -> dict[str, object]:
    status, _headers, index = _http(base_url, "/")
    if status != 200 or b"paradev-runtime-config.js" not in index:
        raise SmokeError("installed GUI did not serve the packaged frontend entry page")
    assets = sorted(set(match.decode("utf-8") for match in _ASSET_PATTERN.findall(index)))
    if not assets:
        raise SmokeError("installed GUI entry page does not reference a packaged asset")
    asset_status, _asset_headers, asset_body = _http(base_url, assets[0])
    if asset_status != 200 or not asset_body:
        raise SmokeError(f"installed GUI asset is unavailable: {assets[0]}")
    runtime_status, runtime_headers, runtime_body = _http(base_url, "/paradev-runtime-config.js")
    if runtime_status != 200 or "no-store" not in runtime_headers.get("cache-control", "").lower() or b"window.location.origin" not in runtime_body:
        raise SmokeError("installed GUI runtime bootstrap is missing its same-origin no-store contract")
    return {"asset_count": len(assets), "probed_asset": assets[0], "same_origin_runtime": True}


def _verify_project_state(base_url: str, project: Path, expected_project_id: str | None) -> dict[str, object]:
    query = urlencode({"include_browser": "false"})
    payload = _json_response(base_url, f"/desktop/state?{query}")
    if payload.get("schema") != DESKTOP_STATE_SCHEMA:
        raise SmokeError(f"installed GUI returned unsupported desktop state: {payload.get('schema')!r}")
    active = payload.get("active_project")
    if not isinstance(active, Mapping):
        raise SmokeError("installed GUI did not discover an active project")
    active_root = active.get("root")
    if not isinstance(active_root, str) or Path(active_root).resolve(strict=True) != project:
        raise SmokeError(f"installed GUI opened a different project: {active_root!r}")
    project_id = active.get("project_id")
    if not isinstance(project_id, str) or not project_id:
        raise SmokeError("installed GUI active project has no project ID")
    if expected_project_id is not None and project_id != expected_project_id:
        raise SmokeError(f"installed GUI opened project {project_id!r}, expected {expected_project_id!r}")
    if payload.get("browser") is not None:
        raise SmokeError("desktop-state launch probe unexpectedly hydrated the large project browser")
    output_root = active.get("output_root")
    if not isinstance(output_root, str) or not Path(output_root).is_absolute():
        raise SmokeError(f"installed GUI active project has no absolute output root: {output_root!r}")
    return {
        "project_id": project_id,
        "project_root": str(project),
        "browser_deferred": True,
        "_output_root": output_root,
    }


def _load_build_summary(path_value: object, *, runtime_root: Path) -> dict[str, object]:
    if not isinstance(path_value, str) or not path_value:
        raise SmokeError("completed build did not return an output path")
    path = Path(path_value).resolve(strict=True)
    if runtime_root not in path.parents:
        raise SmokeError(f"completed build output escaped the disposable runtime: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SmokeError(f"completed build output is not valid JSON: {path}") from error
    if not isinstance(payload, dict) or payload.get("schema") != BUILD_SUMMARY_SCHEMA:
        raise SmokeError(f"completed build output has an unsupported schema: {payload!r}")
    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise SmokeError("completed build output has no summary object")
    if summary.get("blocked") is not False or summary.get("error_count") != 0:
        raise SmokeError(f"completed build summary is blocked or contains errors: {summary!r}")
    return {
        key: summary.get(key)
        for key in (
            "module_count",
            "collection_count",
            "artifact_count",
            "diagnostic_count",
            "error_count",
            "blocked",
        )
    }


def _output_snapshot(root: Path) -> dict[str, object]:
    """Return one deterministic path-and-byte digest for game-ready mod files."""

    if root.is_symlink() or not root.is_dir():
        raise SmokeError(f"generated mod root must be a real directory: {root}")
    publication_markers: list[Path] = []
    for current, directory_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in directory_names:
            directory = current_path / name
            if directory.is_symlink():
                raise SmokeError(f"generated mod output contains a symlinked directory: {directory}")
        if ".paradev-publication.json" in file_names:
            marker = current_path / ".paradev-publication.json"
            metadata = marker.lstat()
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
                raise SmokeError(f"generated mod output contains an invalid publication marker: {marker}")
            publication_markers.append(marker)
    if len(publication_markers) > 1:
        raise SmokeError(f"generated mod container has multiple ParaDev publication roots: {root}")
    publication_root = publication_markers[0].parent if publication_markers else root
    digest = hashlib.sha256()
    file_count = 0
    byte_count = 0
    control_file_count = 0
    control_byte_count = 0
    for current, directory_names, file_names in os.walk(publication_root, followlinks=False):
        current_path = Path(current)
        directory_names.sort()
        file_names.sort()
        for name in directory_names:
            directory = current_path / name
            if directory.is_symlink():
                raise SmokeError(f"generated mod output contains a symlinked directory: {directory}")
        for name in file_names:
            path = current_path / name
            metadata = path.lstat()
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
                raise SmokeError(f"generated mod output contains a non-regular file: {path}")
            if name in _OUTPUT_CONTROL_FILES:
                control_file_count += 1
                control_byte_count += metadata.st_size
                continue
            relative_bytes = path.relative_to(publication_root).as_posix().encode("utf-8")
            content_digest = hashlib.sha256()
            with path.open("rb") as handle:
                while chunk := handle.read(1024 * 1024):
                    content_digest.update(chunk)
            digest.update(len(relative_bytes).to_bytes(8, "big"))
            digest.update(relative_bytes)
            digest.update(metadata.st_size.to_bytes(8, "big"))
            digest.update(content_digest.digest())
            file_count += 1
            byte_count += metadata.st_size
    return {
        "schema": "paradev.output-snapshot.v1",
        "sha256": digest.hexdigest(),
        "file_count": file_count,
        "byte_count": byte_count,
        "control_file_count": control_file_count,
        "control_byte_count": control_byte_count,
    }


def _publication_evidence(
    mod_root: Path,
    *,
    clean_baseline: Mapping[str, object] | None,
    establish_baseline: bool,
) -> tuple[dict[str, object], Mapping[str, object] | None]:
    snapshot = _output_snapshot(mod_root)
    baseline = snapshot if establish_baseline else clean_baseline
    if clean_baseline is not None and snapshot != clean_baseline:
        raise SmokeError(
            "generated mod output differs from the clean whole-project baseline " f"(clean={clean_baseline.get('sha256')}, current={snapshot.get('sha256')})"
        )
    return (
        {
            **snapshot,
            "matches_clean_baseline": baseline is not None,
        },
        baseline,
    )


def _run_build(
    base_url: str,
    project: Path,
    spec: BuildSpec,
    *,
    runtime_root: Path,
    workers: int | None,
    strict_metadata: bool,
    timeout_seconds: float,
    poll_seconds: float,
) -> dict[str, object]:
    started_at = time.monotonic()
    request: dict[str, object] = {
        "projectRoot": str(project),
        "mode": spec.mode,
        "strictMetadata": strict_metadata,
    }
    if workers is not None:
        request["parallelism"] = workers
    if spec.target is not None:
        request["target"] = dict(spec.target)
    started = _json_response(base_url, "/desktop/builds", method="POST", payload=request)
    if started.get("schema") != BUILD_RUN_SCHEMA or started.get("status") != "running":
        raise SmokeError(f"{spec.label} did not start a desktop build: {started!r}")
    run_id = started.get("runId")
    if not isinstance(run_id, str) or not run_id:
        raise SmokeError(f"{spec.label} returned no build run ID")
    try:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            query = urlencode({"run_id": run_id})
            status = _json_response(base_url, f"/desktop/builds/status?{query}")
            state = status.get("status")
            if state in _TERMINAL_BUILD_STATUSES:
                if state != "completed" or status.get("exitCode") != 0:
                    detail = status.get("errorSummary") or f"exit {status.get('exitCode')!r}"
                    raise SmokeError(f"{spec.label} finished as {state}: {detail}")
                return {
                    "label": spec.label,
                    "mode": spec.mode,
                    "target": spec.target or {"kind": "project", "id": None},
                    "elapsed_seconds": round(time.monotonic() - started_at, 3),
                    "summary": _load_build_summary(status.get("outputPath"), runtime_root=runtime_root),
                }
            if state != "running":
                raise SmokeError(f"{spec.label} returned unexpected build status {state!r}")
            time.sleep(poll_seconds)
        raise SmokeError(f"{spec.label} timed out after {timeout_seconds:g} seconds")
    except BaseException as error:
        try:
            _json_response(base_url, "/desktop/builds/interrupt", method="POST", payload={"runId": run_id})
        except SmokeError as cleanup_error:
            raise SmokeError(f"{spec.label} failed and its build could not be interrupted: {cleanup_error}") from error
        raise


def _terminate(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def _validate_args(args: argparse.Namespace) -> None:
    if args.workers is not None and args.workers < 1:
        raise SmokeError("--workers must be at least 1")
    if args.timeout_seconds < 10:
        raise SmokeError("--timeout-seconds must be at least 10")
    if args.startup_timeout_seconds < 1:
        raise SmokeError("--startup-timeout-seconds must be at least 1")
    if not 0.05 <= args.poll_seconds <= 30:
        raise SmokeError("--poll-seconds must be between 0.05 and 30")


def _publish_evidence(path: Path | None, payload: Mapping[str, object]) -> None:
    if path is None:
        return
    output = path.expanduser().absolute()
    if output.exists() or output.is_symlink():
        raise SmokeError(f"evidence path already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(output)


def run(args: argparse.Namespace) -> dict[str, object]:
    """Run the isolated installed-GUI smoke.

    Args:
        args (argparse.Namespace): Validated command-line arguments containing
            the wheel, project, optional build scopes, timeouts, and evidence
            destination.

    Returns:
        dict[str, object]: JSON-safe smoke evidence for the installed runtime,
        packaged frontend, project discovery, and requested build scopes.

    Raises:
        SmokeError: If installation, launch, frontend delivery, project
            discovery, or any requested build is incomplete or inconsistent.
    """

    _validate_args(args)
    wheel = _real_file(args.wheel.expanduser().absolute(), "wheel")
    source_project = _real_project(args.project.expanduser().absolute())
    specs = _build_specs(args)
    uv = shutil.which(args.uv) if not Path(args.uv).is_absolute() else args.uv
    if not uv or not Path(uv).is_file():
        raise SmokeError(f"uv executable was not found: {args.uv}")
    python = _real_file(Path(args.python).expanduser().absolute(), "build Python", allow_symlink=True)

    with tempfile.TemporaryDirectory(prefix="paradev-wheel-gui-smoke-") as temporary_root:
        root = Path(temporary_root).resolve(strict=True)
        project = root / "project" if args.copy_project else source_project
        if args.copy_project:
            shutil.copytree(source_project, project, symlinks=True)
        venv = root / "venv"
        home = root / "home"
        runtime_temp = root / "tmp"
        runtime_bin = root / "bin"
        mod_root = root / "mod"
        for directory in (home, runtime_temp, runtime_bin, mod_root):
            directory.mkdir()
        _run_install(
            [str(uv), "venv", "--python", str(python), str(venv)],
            label="clean virtual environment creation",
            timeout_seconds=args.startup_timeout_seconds,
        )
        venv_python = _runtime_executable(venv, "python")
        _run_install(
            [str(uv), "pip", "install", "--python", str(venv_python), str(wheel)],
            label="wheel installation",
            timeout_seconds=max(args.startup_timeout_seconds, 300.0),
        )
        gui = _runtime_executable(venv, "paradev-gui")
        environment = _runtime_environment(
            home=home,
            runtime_temp=runtime_temp,
            runtime_bin=runtime_bin,
            mod_root=mod_root,
            project=project,
        )
        runtime_identity = _runtime_identity(
            venv_python,
            venv=venv,
            environment=environment,
            working_directory=root,
        )
        stdout_path = root / "gui.stdout.log"
        stderr_path = root / "gui.stderr.log"
        port = _free_port()
        base_url = f"http://127.0.0.1:{port}"
        with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
            process = subprocess.Popen(
                [str(gui), "--no-open", "--host", "127.0.0.1", "--port", str(port)],
                cwd=root,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                start_new_session=os.name != "nt",
            )
            try:
                _wait_for_host(base_url, process, stderr_path, args.startup_timeout_seconds)
                frontend = _verify_frontend(base_url)
                project_state = _verify_project_state(base_url, project, args.expect_project_id)
                publication_root = Path(str(project_state.pop("_output_root")))
                project_state["project_copy"] = bool(args.copy_project)
                if args.copy_project:
                    project_state["project_root"] = "disposable_copy"
                    project_state["source_project_root"] = str(source_project)
                builds: list[dict[str, object]] = []
                clean_baseline: Mapping[str, object] | None = None
                for spec in specs:
                    build = _run_build(
                        base_url,
                        project,
                        spec,
                        runtime_root=root,
                        workers=args.workers,
                        strict_metadata=args.strict_metadata,
                        timeout_seconds=args.timeout_seconds,
                        poll_seconds=args.poll_seconds,
                    )
                    publication, clean_baseline = _publication_evidence(
                        publication_root,
                        clean_baseline=clean_baseline,
                        establish_baseline=spec.mode == "full" and spec.target is None,
                    )
                    build["publication"] = publication
                    builds.append(build)
            finally:
                _terminate(process)

        evidence = {
            "schema": EVIDENCE_SCHEMA,
            "wheel": {
                "name": wheel.name,
                "bytes": wheel.stat().st_size,
                "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
            },
            "runtime": {
                **runtime_identity,
                "isolated_home": True,
                "isolated_temp": True,
                "developer_path_available": False,
                "uv_available_to_app": False,
            },
            "frontend": frontend,
            "project": project_state,
            "builds": builds,
            "ok": True,
        }
        _publish_evidence(args.evidence, evidence)
        return evidence


def main(argv: Sequence[str] | None = None) -> int:
    """Run the installed ParaDev wheel GUI smoke command.

    Args:
        argv (Sequence[str] | None): Optional command arguments. Uses process
            arguments when omitted.

    Returns:
        int: Process exit code. Returns `0` after complete evidence and `1`
        after a contextual smoke failure.
    """

    try:
        evidence = run(_parser().parse_args(argv))
    except (OSError, SmokeError, subprocess.SubprocessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
