"""Installed GUI launcher for ParaDev's React desktop application."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
import socket
import sys
import threading
import time
from urllib.parse import urlsplit
import webbrowser

from heavenbase.utils import cmd, exists_dir, exists_file, exists_path, is_macos, pj

from .gui_assets import gui_host_file, gui_root
from .version import __version__

_LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")
_MUTATING_METHODS = frozenset({"DELETE", "PATCH", "POST", "PUT"})
_CHROMIUM_APPS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)


def _loopback_host(value: str) -> str:
    host = value.strip().lower()
    if host not in _LOOPBACK_HOSTS:
        choices = ", ".join(_LOOPBACK_HOSTS)
        raise argparse.ArgumentTypeError(f"host must be loopback-only ({choices})")
    return host


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer") from exc
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 0 and 65535")
    return port


def build_parser(*, prog: str = "paradev-gui") -> argparse.ArgumentParser:
    """Build the ParaDev GUI launcher parser.

    Args:
        prog (str): Command name displayed in launcher help and errors.

    Returns:
        argparse.ArgumentParser: Configured ParaDev dashboard parser.
    """

    parser = argparse.ArgumentParser(prog=prog, description="Launch the ParaDev desktop application.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--host", default="127.0.0.1", type=_loopback_host, help="loopback host (default: %(default)s)")
    parser.add_argument("--port", default=0, type=_port, help="loopback port; 0 selects a free port (default: %(default)s)")
    window = parser.add_mutually_exclusive_group()
    window.add_argument("--app", action="store_const", const="app", dest="open_mode", help="open in a Chromium app window instead of the system WebView")
    window.add_argument("--browser", action="store_const", const="browser", dest="open_mode", help="open in the default browser")
    parser.set_defaults(open_mode="auto")
    parser.add_argument("--no-open", action="store_true", help="serve the GUI without opening a window")
    parser.add_argument("--install-app", action="store_true", help="install ~/Applications/ParaDev.app for Finder and Dock launch")
    parser.add_argument("--yes", action="store_true", help="replace an existing installed application without prompting")
    return parser


def _packaged_gui_root() -> str:
    return gui_root()


def _runtime_config_script() -> str:
    return """window.__PARADEV_RUNTIME_CONFIG__ = Object.freeze({
  nativeBridgeBaseUrl: window.location.origin
});
"""


def _host_name(authority: str) -> str:
    try:
        return (urlsplit(f"//{authority}").hostname or "").casefold()
    except ValueError:
        return ""


def _build_gui_app(static_root: str | None = None, *, instance_nonce: str | None = None):
    """Compose the existing REST surface with packaged React assets."""

    from fastapi import Header, Request
    from fastapi.responses import JSONResponse, PlainTextResponse, Response
    from fastapi.staticfiles import StaticFiles
    from .api import build_app

    root = pj(static_root or _packaged_gui_root(), abs=True)
    if not exists_dir(root) or not exists_file(pj(root, "index.html")):
        raise RuntimeError(f"ParaDev GUI assets are missing from {root}. Reinstall ParaDev or rebuild the desktop assets.")

    app = build_app()

    @app.middleware("http")
    async def protect_local_mutations(request: Request, call_next):
        origin = request.headers.get("origin")
        host = request.headers.get("host", "").lower()
        if _host_name(host) not in _LOOPBACK_HOSTS:
            return PlainTextResponse("Invalid host header", status_code=400)
        if request.method in _MUTATING_METHODS and origin:
            origin_authority = urlsplit(origin).netloc.lower()
            if not origin_authority or origin_authority != host:
                return PlainTextResponse("Cross-origin local mutations are not allowed.", status_code=403)
        response: Response = await call_next(request)
        response.headers.setdefault("x-content-type-options", "nosniff")
        response.headers.setdefault("referrer-policy", "no-referrer")
        return response

    @app.get("/paradev-runtime-config.js", include_in_schema=False)
    async def runtime_config() -> Response:
        return Response(
            _runtime_config_script(),
            media_type="text/javascript",
            headers={"Cache-Control": "no-store"},
        )

    if instance_nonce is not None:

        @app.get("/_paradev/app-instance", include_in_schema=False)
        async def app_instance(x_paradev_instance: str | None = Header(default=None)) -> Response:
            if x_paradev_instance != instance_nonce:
                return PlainTextResponse("Not found", status_code=404)
            return JSONResponse(
                {"schema": "paradev.gui-server-ready.v1", "nonce": instance_nonce},
                headers={"Cache-Control": "no-store"},
            )

    app.mount("/", StaticFiles(directory=root, html=True), name="gui")
    return app


def _server_socket(host: str, port: int) -> socket.socket:
    family = socket.AF_INET6 if host == "::1" else socket.AF_INET
    sock = socket.socket(family, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        address: tuple[object, ...] = (host, port, 0, 0) if family == socket.AF_INET6 else (host, port)
        sock.bind(address)
        sock.listen(2048)
        sock.setblocking(False)
        return sock
    except BaseException:
        sock.close()
        raise


def _app_browser_candidates() -> tuple[str, ...]:
    candidates = [binary for binary in _CHROMIUM_APPS if exists_path(binary)]
    candidates.extend(("google-chrome", "chromium", "chromium-browser", "microsoft-edge", "brave-browser"))
    return tuple(candidates)


def _open_app_window(url: str) -> bool:
    for executable in _app_browser_candidates():
        try:
            cmd([executable, f"--app={url}", "--window-size=1360,900"], wait=False, include="handle")
        except OSError:
            continue
        return True
    return False


def _open_webview(url: str) -> bool:
    """Open the macOS system WebView host when it is available."""

    if not is_macos():
        return False
    from .gui_macos import default_macos_app_path

    installed = default_macos_app_path()
    if exists_path(installed):
        try:
            opened = cmd(
                ["/usr/bin/open", "-na", installed, "--args", url],
                include="ok",
            )
        except OSError:
            pass
        else:
            if opened:
                return True

    script = gui_host_file("macos.js")
    icon = gui_host_file("icon.icns")
    if not exists_file(script):
        return False
    try:
        process = cmd(
            ["/usr/bin/osascript", "-l", "JavaScript", script, url, icon],
            wait=False,
            include="handle",
            start_new_session=True,
        )
    except OSError:
        return False
    time.sleep(0.2)
    return process.poll() is None


def _open_window(url: str, mode: str) -> str:
    """Open a GUI host and return the mode that accepted the launch."""

    if mode == "auto" and _open_webview(url):
        return "webview"
    if mode == "app" and _open_app_window(url):
        return "app"
    webbrowser.open(url, new=1)
    return "browser"


def _open_when_ready(server: object, url: str, open_mode: str) -> None:
    deadline = time.monotonic() + 15.0
    while not getattr(server, "started", False) and time.monotonic() < deadline:
        if getattr(server, "should_exit", False):
            return
        time.sleep(0.05)
    if not getattr(server, "started", False):
        return
    _open_window(url, open_mode)


def _serve_gui(
    *,
    host: str,
    port: int,
    open_mode: str | None,
    instance_nonce: str | None = None,
    ready_callback: Callable[[str, int], None] | None = None,
) -> None:
    import uvicorn

    app = _build_gui_app(instance_nonce=instance_nonce)
    config = uvicorn.Config(app, host=host, port=port, log_level="info", access_log=False)
    server = uvicorn.Server(config)
    sock = _server_socket(host, port)
    actual_port = int(sock.getsockname()[1])
    url_host = f"[{host}]" if ":" in host else host
    url = f"http://{url_host}:{actual_port}"
    if ready_callback is None:
        print(f"ParaDev is available at {url}")
    else:
        ready_callback(host, actual_port)
    if open_mode is not None:
        threading.Thread(target=_open_when_ready, args=(server, url, open_mode), daemon=True).start()
    try:
        server.run(sockets=[sock])
    finally:
        sock.close()


def main(argv: Sequence[str] | None = None, *, prog: str = "paradev-gui") -> int:
    """Launch the installed ParaDev GUI on a loopback-only application host.

    Args:
        argv (Sequence[str] | None): Optional command arguments. Defaults to process arguments when
            omitted.
        prog (str): Command name displayed in launcher help and errors.

    Returns:
        int: Process-style exit code.
    """

    arguments = build_parser(prog=prog).parse_args(argv)
    try:
        if arguments.install_app:
            from .gui_macos import default_macos_app_path, install_macos_app

            target = default_macos_app_path()
            replace = exists_path(target)
            if replace and not arguments.yes:
                if not sys.stdin.isatty():
                    print(f"error: {target} already exists; pass --yes to replace it", file=sys.stderr)
                    return 1
                answer = input(f"{target} already exists. Replace it? [y/N] ").strip().casefold()
                if answer not in {"y", "yes"}:
                    print("application installation cancelled")
                    return 0
            installed = install_macos_app(replace=replace)
            print(f"installed ParaDev application at {installed}")
            return 0
        open_mode = None if arguments.no_open else arguments.open_mode
        _serve_gui(host=arguments.host, port=arguments.port, open_mode=open_mode)
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        print(f"error: could not launch ParaDev: {exc}", file=sys.stderr)
        return 1
    return 0


from .gui_api import (  # noqa: E402
    GUI_API_TABLE_SCHEMA,
    GuiApiRow,
    GuiApiTable,
    get_gui_api_selection,
    get_gui_api_table,
    render_gui_api_reference_markdown,
)

__all__ = [
    "build_parser",
    "main",
    "GUI_API_TABLE_SCHEMA",
    "GuiApiRow",
    "GuiApiTable",
    "get_gui_api_selection",
    "get_gui_api_table",
    "render_gui_api_reference_markdown",
]
