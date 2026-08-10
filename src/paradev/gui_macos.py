"""Install and serve the native macOS ParaDev application."""

# heaven-style-scan: standalone-control-plane

from __future__ import annotations

__all__ = ["default_macos_app_path", "install_macos_app", "main", "resolve_app_bind"]

import argparse
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
from secrets import token_urlsafe

from .gui_assets import gui_host_file

_APP_NAME = "ParaDev.app"
_BUNDLE_ID = "top.ahvn.paradev"
_DEFAULT_PORT = 4817
_HOST_MODULE = "paradev.gui_macos"
_READY_SCHEMA = "paradev.gui-server-ready.v1"
_READY_FILE_ENV = "PARADEV_GUI_READY_FILE"


def default_macos_app_path() -> str:
    """Return the user-local installation path for the ParaDev application."""

    return str((Path.home() / "Applications" / _APP_NAME).resolve())


def resolve_app_bind() -> tuple[str, int]:
    """Return the loopback-only bind used by a Finder-launched application."""

    return "127.0.0.1", _DEFAULT_PORT


def _bundle_plist(python_executable: str) -> dict[str, object]:
    """Return the generated application property list."""

    from .version import __version__

    version = ".".join(re.findall(r"\d+", __version__)[:3]) or "0.1.0"
    return {
        "CFBundleAllowMixedLocalizations": True,
        "CFBundleDevelopmentRegion": "en",
        "CFBundleDisplayName": "ParaDev",
        "CFBundleExecutable": "applet",
        "CFBundleIconFile": "ParaDev",
        "CFBundleIconName": "ParaDev",
        "CFBundleIdentifier": _BUNDLE_ID,
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": "ParaDev",
        "CFBundlePackageType": "APPL",
        "CFBundleSignature": "aplt",
        "CFBundleShortVersionString": version,
        "CFBundleSupportedPlatforms": ["MacOSX"],
        "CFBundleVersion": version,
        "LSApplicationCategoryType": "public.app-category.developer-tools",
        "LSMinimumSystemVersion": "12.0",
        "LSRequiresCarbon": True,
        "NSHighResolutionCapable": True,
        "OSAAppletShowStartupScreen": False,
        "OSAAppletStayOpen": True,
        "ParaDevPythonExecutable": python_executable,
        "ParaDevPythonModule": _HOST_MODULE,
    }


def _run_packager(command: list[str], description: str) -> None:
    """Run one required system application-packaging command."""

    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise RuntimeError(f"{description} is unavailable: {exc}") from exc
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit status {result.returncode}"
        raise RuntimeError(f"{description} failed: {detail}")


def _compile_macos_applet(source: Path, destination: Path) -> None:
    """Compile the JavaScript host as a LaunchServices applet."""

    _run_packager(
        ["/usr/bin/osacompile", "-s", "-l", "JavaScript", "-o", str(destination), str(source)],
        "JavaScript application compiler",
    )


def install_macos_app(
    destination: str | os.PathLike[str] | None = None,
    *,
    replace: bool = False,
    python_executable: str | os.PathLike[str] | None = None,
) -> str:
    """Install a Finder-launchable ParaDev application bundle."""

    if sys.platform != "darwin":
        raise RuntimeError("the ParaDev .app installer is available only on macOS")
    target = Path(destination or default_macos_app_path()).expanduser().resolve()
    if target.suffix.lower() != ".app":
        raise ValueError(f"macOS application destination must end in .app: {target}")
    if target.exists() and not replace:
        raise FileExistsError(f"{target} already exists; pass replace=True to replace it")

    launcher_source = Path(gui_host_file("macos_app.js"))
    icon_source = Path(gui_host_file("icon.icns"))
    missing = [str(path) for path in (launcher_source, icon_source) if not path.is_file()]
    if missing:
        raise RuntimeError(f"macOS application assets are missing: {missing!r}; reinstall ParaDev")

    # Preserve virtual-environment launcher symlinks. Resolving `.venv/bin/python`
    # would discard the environment that contains ParaDev.
    runtime = Path(python_executable or sys.executable).expanduser().absolute()
    if not runtime.is_file():
        raise RuntimeError(f"Python runtime does not exist: {runtime}")

    target.parent.mkdir(parents=True, exist_ok=True)
    stage_root = Path(tempfile.mkdtemp(prefix=".paradev-app-", dir=target.parent))
    staged = stage_root / _APP_NAME
    previous = stage_root / "previous.app"
    try:
        _compile_macos_applet(launcher_source, staged)
        resources = staged / "Contents" / "Resources"
        shutil.copyfile(icon_source, resources / "ParaDev.icns")
        with (staged / "Contents" / "Info.plist").open("wb") as stream:
            plistlib.dump(_bundle_plist(str(runtime)), stream, sort_keys=True)
        _run_packager(
            ["/usr/bin/codesign", "--force", "--deep", "--sign", "-", str(staged)],
            "application code signing",
        )

        if target.exists():
            os.replace(target, previous)
        try:
            os.replace(staged, target)
        except BaseException:
            if previous.exists() and not target.exists():
                os.replace(previous, target)
            raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)
    return str(target)


def _serve(host: str, port: int, *, ready_json: bool = False) -> None:
    """Run the child GUI service owned by the application process."""

    from .gui import _serve_gui

    nonce = token_urlsafe(32) if ready_json else None

    def announce(actual_host: str, actual_port: int) -> None:
        document = json.dumps(
            {
                "schema": _READY_SCHEMA,
                "host": actual_host,
                "port": actual_port,
                "nonce": nonce,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        ready_file = os.environ.get(_READY_FILE_ENV)
        if not ready_file:
            print(document, flush=True)
            return
        destination = Path(ready_file)
        staged = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
        staged.write_text(f"{document}\n", encoding="utf-8")
        os.replace(staged, destination)

    _serve_gui(
        host=host,
        port=port,
        open_mode=None,
        instance_nonce=nonce,
        ready_callback=announce if ready_json else None,
    )


def main(argv: list[str] | None = None) -> int:
    """Run the private macOS application-host protocol."""

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--print-bind", action="store_true")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--ready-json", action="store_true")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    args = parser.parse_args(argv)
    host, port = resolve_app_bind()
    if args.print_bind:
        print(json.dumps({"host": host, "port": port}, sort_keys=True), flush=True)
        return 0
    if args.serve:
        _serve(
            args.host or host,
            port if args.port is None else args.port,
            ready_json=args.ready_json,
        )
        return 0
    parser.error("expected --print-bind or --serve")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
