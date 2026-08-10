from __future__ import annotations

from pathlib import Path

import pytest

from paradev.desktop import shell


def test_desktop_project_picker_returns_selected_macos_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project = tmp_path / "PIHC3"
    project.mkdir()
    observed: list[list[str]] = []

    monkeypatch.setattr(shell.shutil, "which", lambda name: "/usr/bin/osascript" if name == "osascript" else None)

    def fake_cmd(command: list[str], **kwargs: object) -> dict[str, object]:
        observed.append(command)
        assert kwargs["include"] == ("ok", "out", "err")
        return {"ok": True, "out": f"{project}/", "err": ""}

    monkeypatch.setattr(shell, "cmd", fake_cmd)

    assert shell.desktop_select_project_path(platform="macos") == str(project.resolve())
    assert observed == [
        [
            "/usr/bin/osascript",
            "-e",
            'POSIX path of (choose folder with prompt "Open a ParaDev project")',
        ]
    ]


def test_desktop_project_picker_treats_macos_cancel_as_no_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(shell.shutil, "which", lambda _name: "/usr/bin/osascript")
    monkeypatch.setattr(
        shell,
        "cmd",
        lambda *_args, **_kwargs: {"ok": False, "out": "", "err": "User canceled. (-128)"},
    )

    assert shell.desktop_select_project_path(platform="macos") is None


def test_desktop_project_package_picker_returns_selected_macos_zip(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    package = tmp_path / "PIHC3-0.2.3-project.zip"
    package.touch()
    observed: list[list[str]] = []

    monkeypatch.setattr(shell.shutil, "which", lambda name: "/usr/bin/osascript" if name == "osascript" else None)

    def fake_cmd(command: list[str], **kwargs: object) -> dict[str, object]:
        observed.append(command)
        assert kwargs["include"] == ("ok", "out", "err")
        return {"ok": True, "out": f"{package}\n", "err": ""}

    monkeypatch.setattr(shell, "cmd", fake_cmd)

    assert shell.desktop_select_project_package_path(platform="macos") == str(package.resolve())
    assert observed == [
        [
            "/usr/bin/osascript",
            "-e",
            ('POSIX path of (choose file of type {"public.zip-archive"} ' 'with prompt "Install a ParaDev project package")'),
        ]
    ]


def test_desktop_project_package_picker_handles_cancel_and_invalid_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(shell.shutil, "which", lambda _name: "/usr/bin/osascript")
    monkeypatch.setattr(
        shell,
        "cmd",
        lambda *_args, **_kwargs: {"ok": False, "out": "", "err": "User canceled. (-128)"},
    )
    assert shell.desktop_select_project_package_path(platform="macos") is None

    invalid = tmp_path / "PIHC3-project.txt"
    invalid.touch()
    monkeypatch.setattr(
        shell,
        "cmd",
        lambda *_args, **_kwargs: {"ok": True, "out": str(invalid), "err": ""},
    )
    with pytest.raises(RuntimeError, match="non-ZIP file path"):
        shell.desktop_select_project_package_path(platform="macos")


def test_desktop_project_picker_surfaces_platform_and_picker_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ValueError, match="currently supports macOS"):
        shell.desktop_select_project_path(platform="linux")

    monkeypatch.setattr(shell.shutil, "which", lambda _name: "/usr/bin/osascript")
    monkeypatch.setattr(
        shell,
        "cmd",
        lambda *_args, **_kwargs: {"ok": False, "out": "", "err": "Automation denied"},
    )
    with pytest.raises(RuntimeError, match="Automation denied"):
        shell.desktop_select_project_path(platform="macos")
