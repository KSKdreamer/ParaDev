from __future__ import annotations

import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

import pytest
from fastapi.testclient import TestClient

import paradev.gui as gui


def _write_frontend(root: Path) -> Path:
    root.mkdir()
    (root / "index.html").write_text(
        '<!doctype html><html><body><div id="root">ParaDev</div></body></html>',
        encoding="utf-8",
    )
    return root


def test_gui_app_serves_existing_rest_api_and_frontend(tmp_path: Path) -> None:
    app = gui._build_gui_app(_write_frontend(tmp_path / "gui"))

    with TestClient(app, base_url="http://127.0.0.1") as client:
        assert client.get("/health").status_code == 200
        response = client.get("/")

    assert response.status_code == 200
    assert "ParaDev" in response.text


def test_gui_app_exposes_no_store_same_origin_runtime_config(tmp_path: Path) -> None:
    app = gui._build_gui_app(_write_frontend(tmp_path / "gui"))

    with TestClient(app, base_url="http://127.0.0.1:4817") as client:
        response = client.get("/paradev-runtime-config.js")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert "window.location.origin" in response.text
    assert "__PARADEV_RUNTIME_CONFIG__" in response.text


def test_gui_app_instance_probe_requires_the_launch_nonce(tmp_path: Path) -> None:
    nonce = "owned-launch-nonce"
    app = gui._build_gui_app(_write_frontend(tmp_path / "gui"), instance_nonce=nonce)

    with TestClient(app, base_url="http://127.0.0.1") as client:
        assert client.get("/_paradev/app-instance").status_code == 404
        assert client.get("/_paradev/app-instance", headers={"X-ParaDev-Instance": "foreign"}).status_code == 404
        response = client.get("/_paradev/app-instance", headers={"X-ParaDev-Instance": nonce})
        openapi = client.get("/openapi.json").json()

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json() == {"schema": "paradev.gui-server-ready.v1", "nonce": nonce}
    assert "/_paradev/app-instance" not in openapi["paths"]


def test_gui_app_rejects_untrusted_hosts_and_cross_origin_mutations(tmp_path: Path) -> None:
    app = gui._build_gui_app(_write_frontend(tmp_path / "gui"))

    with TestClient(app, base_url="http://127.0.0.1:4817") as client:
        untrusted_host = client.get("/health", headers={"host": "paradev.example"})
        cross_origin = client.post(
            "/desktop/open-path",
            headers={"origin": "https://paradev.example"},
            json={"path": "/tmp/PIHC3", "target": "folder"},
        )

    assert untrusted_host.status_code == 400
    assert cross_origin.status_code == 403


def test_gui_app_accepts_ipv6_loopback_host(tmp_path: Path) -> None:
    app = gui._build_gui_app(_write_frontend(tmp_path / "gui"))

    with TestClient(app, base_url="http://127.0.0.1:4817") as client:
        response = client.get("/health", headers={"host": "[::1]:4817"})

    assert response.status_code == 200


def test_gui_app_reports_missing_frontend_assets(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="GUI assets are missing"):
        gui._build_gui_app(tmp_path / "missing")


def test_gui_main_runs_loopback_server_without_opening_window(monkeypatch: pytest.MonkeyPatch) -> None:
    observed: dict[str, object] = {}

    def fake_serve_gui(*, host: str, port: int, open_mode: str | None) -> None:
        observed.update(host=host, port=port, open_mode=open_mode)

    monkeypatch.setattr(gui, "_serve_gui", fake_serve_gui)

    assert gui.main(["--no-open", "--port", "4817"]) == 0
    assert observed == {"host": "127.0.0.1", "port": 4817, "open_mode": None}


def test_gui_parser_rejects_non_loopback_bind() -> None:
    with pytest.raises(SystemExit):
        gui.build_parser().parse_args(["--host", "0.0.0.0"])


def test_gui_parser_prefers_webview_and_keeps_explicit_fallbacks() -> None:
    parser = gui.build_parser()

    assert parser.parse_args([]).open_mode == "auto"
    assert parser.parse_args(["--app"]).open_mode == "app"
    assert parser.parse_args(["--browser"]).open_mode == "browser"
    with pytest.raises(SystemExit):
        parser.parse_args(["--app", "--browser"])


def test_gui_parser_uses_the_calling_command_name() -> None:
    parser = gui.build_parser(prog="paradev dashboard")

    assert parser.prog == "paradev dashboard"


def test_gui_host_prefers_webview_and_keeps_explicit_fallbacks(monkeypatch: pytest.MonkeyPatch) -> None:
    opened: list[tuple[str, int]] = []
    monkeypatch.setattr(gui, "_open_webview", lambda _url: True)
    monkeypatch.setattr(gui.webbrowser, "open", lambda url, new=0: opened.append((url, new)))
    assert gui._open_window("http://127.0.0.1:4817", "auto") == "webview"
    assert opened == []

    monkeypatch.setattr(gui, "_open_webview", lambda _url: False)
    monkeypatch.setattr(gui, "_open_app_window", lambda _url: False)
    assert gui._open_window("http://127.0.0.1:4817", "auto") == "browser"
    assert gui._open_window("http://127.0.0.1:4817", "app") == "browser"
    assert opened == [("http://127.0.0.1:4817", 1), ("http://127.0.0.1:4817", 1)]


def test_gui_install_app_is_a_standalone_launcher_action(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import paradev.gui_macos as macos

    target = tmp_path / "ParaDev.app"
    calls: list[bool] = []
    monkeypatch.setattr(macos, "default_macos_app_path", lambda: str(target))
    monkeypatch.setattr(macos, "install_macos_app", lambda *, replace=False: calls.append(replace) or str(target))
    monkeypatch.setattr(gui, "_serve_gui", lambda **_kwargs: pytest.fail("installer must not start the server"))

    assert gui.main(["--install-app"]) == 0
    assert calls == [False]

    target.mkdir()
    assert gui.main(["--install-app", "--yes"]) == 0
    assert calls == [False, True]


def test_desktop_html_loads_runtime_config_before_application() -> None:
    html = Path("apps/desktop/index.html").read_text(encoding="utf-8")

    runtime_config = html.index('src="/paradev-runtime-config.js"')
    application = html.index('src="/src/main.tsx"')
    assert runtime_config < application


def test_packaged_gui_contains_built_frontend() -> None:
    root = Path(gui._packaged_gui_root())

    assert (root / "index.html").is_file()
    assert (root / "paradev-runtime-config.js").is_file()
    assert any((root / "assets").iterdir())


def test_gui_package_data_uses_owned_resource_groups() -> None:
    config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    setuptools = config["tool"]["setuptools"]

    assert setuptools["include-package-data"] is False
    assert setuptools["package-data"]["paradev"] == [
        "api/*.pyi",
        "resources/README.md",
        "resources/gui/*",
        "resources/gui/assets/*",
        "resources/release/project-packages.json",
    ]
    assert setuptools["data-files"]["share/paradev/gui/host"] == [
        "apps/desktop/host/*.js",
        "apps/desktop/host/icon.icns",
    ]


def test_gui_distribution_has_no_tauri_packaging_or_runtime_adapter() -> None:
    retired_paths = (
        Path("apps/desktop/src-tauri"),
        Path("scripts/build-tauri.bash"),
        Path("scripts/build-sidecar.bash"),
        Path("requirements-bundle.txt"),
        Path(".github/workflows/windows-desktop-package.yml"),
    )
    assert not any(path.exists() for path in retired_paths)

    package = json.loads(Path("apps/desktop/package.json").read_text(encoding="utf-8"))
    dependency_names = {
        *package.get("dependencies", {}),
        *package.get("devDependencies", {}),
    }
    assert not any(name.startswith("@tauri-apps/") for name in dependency_names)
    assert "tauri" not in Path("apps/desktop/package-lock.json").read_text(encoding="utf-8").casefold()

    production_sources = (
        path for path in Path("apps/desktop/src").rglob("*") if path.is_file() and path.suffix in {".ts", ".tsx"} and ".test." not in path.name
    )
    packaged_sources = (path for path in Path("src/paradev/resources/gui").rglob("*") if path.is_file() and path.suffix in {".css", ".html", ".js", ".json"})
    for path in (*production_sources, *packaged_sources):
        text = path.read_text(encoding="utf-8").casefold()
        assert "tauri" not in text, path
        assert "__tauri_internals__" not in text, path
