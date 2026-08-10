from __future__ import annotations

from pathlib import Path
import json
import plistlib
import stat
import sys

import pytest

from paradev import gui, gui_assets, gui_macos


def test_gui_host_assets_resolve_from_the_source_checkout() -> None:
    assert Path(gui_assets.gui_host_file("macos.js")).is_file()
    assert Path(gui_assets.gui_host_file("macos_app.js")).is_file()
    assert Path(gui_assets.gui_host_file("icon.icns")).stat().st_size > 1000
    with pytest.raises(ValueError, match="file name"):
        gui_assets.gui_host_file("nested/macos.js")


def test_macos_hosts_accept_loopback_http_urls_only() -> None:
    standalone = Path(gui_assets.gui_host_file("macos.js")).read_text(encoding="utf-8")
    app = Path(gui_assets.gui_host_file("macos_app.js")).read_text(encoding="utf-8")

    assert 'ObjC.unwrap(url.scheme) !== "http"' in standalone
    assert 'unwrap(url.scheme) === "http"' in app
    assert '["127.0.0.1", "localhost", "::1"]' in standalone
    assert '["127.0.0.1", "localhost", "::1"]' in app


def test_macos_app_surfaces_bounded_server_failure_and_terminates() -> None:
    app = Path(gui_assets.gui_host_file("macos_app.js")).read_text(encoding="utf-8")

    assert "const SERVER_ERROR_LIMIT = 8192" in app
    assert "task.standardError = errorHandle" in app
    assert "readServerFile(serverErrorPath, SERVER_ERROR_LIMIT)" in app
    assert "Server details:" in app
    assert "showFailure(visibleMessage);" in app
    assert "function quit()" in app
    assert "applicationQuitting = true;\n  stopServer();\n  removeServerFiles();\n  return true;" in app
    assert "if (!applicationQuitting) $.NSApplication.sharedApplication.terminate(null);" in app
    assert '"applicationWillTerminate:"' not in app
    assert '"applicationShouldTerminate:"' not in app
    assert "app.delegate = applicationDelegate" not in app
    assert 'ObjC.import("signal")' in app
    assert 'environment.setObjectForKey(serverReadyPath, "PARADEV_GUI_READY_FILE")' in app
    assert "readabilityHandler" not in app
    assert "$.kill(serverProcessIdentifier, $.SIGTERM);" in app
    assert "serverProcessIdentifier = serverTask.processIdentifier;" in app
    assert "serverTask.terminate" not in app
    assert "serverTask.interrupt" not in app
    assert "app.terminate(null);" in app


def test_macos_app_uses_dynamic_owned_server_identity() -> None:
    app = Path(gui_assets.gui_host_file("macos_app.js")).read_text(encoding="utf-8")

    assert '"--port",\n        "0",\n        "--ready-json"' in app
    assert 'const SERVER_READY_SCHEMA = "paradev.gui-server-ready.v1"' in app
    assert "`${url}/_paradev/app-instance`" in app
    assert "`X-ParaDev-Instance: ${nonce}`" in app
    assert 'Object.keys(response).sort().join(",") === "nonce,schema"' in app
    assert 'runCaptured(python, ["-m", module, "--print-bind"])' not in app


def test_macos_app_bundle_installation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gui_macos.sys, "platform", "darwin")

    def compile_applet(_source: Path, destination: Path) -> None:
        executable = destination / "Contents" / "MacOS" / "applet"
        script = destination / "Contents" / "Resources" / "Scripts" / "main.scpt"
        executable.parent.mkdir(parents=True)
        script.parent.mkdir(parents=True)
        executable.write_bytes(b"mock applet")
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
        script.write_bytes(b"mock compiled JavaScript")
        (destination / "Contents" / "Info.plist").write_bytes(b"")

    monkeypatch.setattr(gui_macos, "_compile_macos_applet", compile_applet)
    monkeypatch.setattr(gui_macos, "_run_packager", lambda *_args: None)

    target = tmp_path / "ParaDev.app"
    installed = gui_macos.install_macos_app(target, python_executable=sys.executable)
    assert installed == str(target.resolve())
    executable = target / "Contents" / "MacOS" / "applet"
    assert executable.stat().st_size > 0
    assert executable.stat().st_mode & stat.S_IXUSR
    assert (target / "Contents" / "Resources" / "Scripts" / "main.scpt").stat().st_size > 0
    assert (target / "Contents" / "Resources" / "ParaDev.icns").stat().st_size > 1000
    with (target / "Contents" / "Info.plist").open("rb") as stream:
        info = plistlib.load(stream)
    assert info["CFBundleIdentifier"] == "top.ahvn.paradev"
    assert info["CFBundleExecutable"] == "applet"
    assert info["CFBundleIconFile"] == "ParaDev"
    assert info["ParaDevPythonExecutable"] == str(Path(sys.executable).absolute())
    assert info["ParaDevPythonModule"] == "paradev.gui_macos"
    assert info["OSAAppletStayOpen"] is True

    with pytest.raises(FileExistsError, match="replace=True"):
        gui_macos.install_macos_app(target, python_executable=sys.executable)
    marker = target / "old-marker"
    marker.write_text("old", encoding="utf-8")
    assert gui_macos.install_macos_app(target, replace=True, python_executable=sys.executable) == str(target.resolve())
    assert not marker.exists()

    runtime_link = tmp_path / "python-link"
    runtime_link.symlink_to(sys.executable)
    linked_target = tmp_path / "Linked.app"
    gui_macos.install_macos_app(linked_target, python_executable=runtime_link)
    with (linked_target / "Contents" / "Info.plist").open("rb") as stream:
        linked_info = plistlib.load(stream)
    assert linked_info["ParaDevPythonExecutable"] == str(runtime_link.absolute())


def test_macos_app_bind_is_loopback_only() -> None:
    assert gui_macos.resolve_app_bind() == ("127.0.0.1", 4817)


def test_macos_private_server_preserves_port_zero_and_emits_owned_ready_document(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    calls: list[dict[str, object]] = []

    def fake_serve_gui(**kwargs: object) -> None:
        calls.append(kwargs)
        ready_callback = kwargs["ready_callback"]
        assert callable(ready_callback)
        ready_callback("127.0.0.1", 53291)

    monkeypatch.setattr(gui_macos, "token_urlsafe", lambda _size: "owned_nonce_abcdefghijklmnopqrstuvwxyz012345")
    monkeypatch.setattr(gui, "_serve_gui", fake_serve_gui)

    assert gui_macos.main(["--serve", "--host", "127.0.0.1", "--port", "0", "--ready-json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert calls[0]["host"] == "127.0.0.1"
    assert calls[0]["port"] == 0
    assert calls[0]["open_mode"] is None
    assert calls[0]["instance_nonce"] == payload["nonce"]
    assert payload == {
        "schema": "paradev.gui-server-ready.v1",
        "host": "127.0.0.1",
        "port": 53291,
        "nonce": "owned_nonce_abcdefghijklmnopqrstuvwxyz012345",
    }

    ready_file = tmp_path / "ready.json"
    monkeypatch.setenv("PARADEV_GUI_READY_FILE", str(ready_file))
    calls.clear()
    assert gui_macos.main(["--serve", "--host", "127.0.0.1", "--port", "0", "--ready-json"]) == 0
    assert capsys.readouterr().out == ""
    assert json.loads(ready_file.read_text(encoding="utf-8")) == payload


def test_macos_installed_app_release_smoke_is_lifecycle_complete() -> None:
    script = Path("scripts/smoke-macos-installed-app.bash")
    source = script.read_text(encoding="utf-8")

    assert script.stat().st_mode & stat.S_IXUSR
    assert '"${RUNTIME}/bin/paradev" dashboard --install-app --yes' in source
    assert "/usr/bin/codesign --verify --deep --strict" in source
    assert 'HOME="${SMOKE_HOME}" /usr/bin/open -n "${APP}"' in source
    assert "FOREIGN_PORT=4817" in source
    assert '"${RUNTIME}/bin/python" -m http.server "${FOREIGN_PORT}"' in source
    assert 'SERVER_PORT="$(/usr/sbin/lsof' in source
    assert 'if [[ "${SERVER_PORT}" == "${FOREIGN_PORT}" ]]' in source
    assert 'kill -0 "${APP_PID}"' in source
    assert '"app_exited_after_quit": True' in source
    assert "foreign_listener_survived" in source
    assert "server_exited_after_quit" in source
