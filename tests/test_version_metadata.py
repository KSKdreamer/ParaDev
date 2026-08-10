"""Contracts for canonical ParaDev product version metadata."""

# heaven-style-scan: standalone-control-plane

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from types import ModuleType

import pytest
from heavenbase.utils import dumps_json, loads_json

ROOT = Path(__file__).resolve().parents[1]
SYNC_SCRIPT = ROOT / "scripts" / "sync-env.py"


def _load_sync_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("paradev_sync_env", SYNC_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_version_fixture(root: Path, *, version: str = "0.1.0.000dev") -> None:
    files = {
        "src/paradev/version.py": f'__version__ = "{version}"\n',
        "requirements.txt": "heavenbase==0.1.2.2\n",
        "requirements-dev.txt": "pytest==9.0.2\n",
        ".python-version": "3.12.13\n",
        "pyproject.toml": """
[project]
name = "paradev"
requires-python = ">=3.10"
dynamic = ["version", "dependencies", "optional-dependencies"]

[tool.setuptools.dynamic]
dependencies = { file = ["requirements.txt"] }
optional-dependencies.dev = { file = ["requirements-dev.txt"] }

[tool.poetry]
version = "9.9.9"
""".lstrip(),
        "apps/desktop/package.json": dumps_json(
            {"name": "@paradev/desktop", "version": "9.9.9"},
            indent=2,
        )
        + "\n",
        "apps/desktop/package-lock.json": dumps_json(
            {
                "name": "@paradev/desktop",
                "version": "9.9.9",
                "lockfileVersion": 3,
                "packages": {
                    "": {
                        "name": "@paradev/desktop",
                        "version": "9.9.9",
                    }
                },
            },
            indent=2,
        )
        + "\n",
        "src/paradev/resources/release/project-packages.json": dumps_json(
            {
                "schema": "paradev.release.project-package-catalog.v1",
                "paradev_version": "9.9.9",
                "desktop_version": "9.9.9",
                "packages": [{"id": "sample-1.0.0"}],
            },
            indent=2,
        )
        + "\n",
    }
    for relative_path, text in files.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


@pytest.mark.unit
def test_desktop_version_mapping_keeps_development_builds_pre_release() -> None:
    sync_module = _load_sync_module()

    assert sync_module._desktop_version("0.1.0.000dev") == "0.1.0-0"
    assert sync_module._desktop_version("0.1.0.000dev4") == "0.1.0-4"
    assert sync_module._desktop_version("0.1.0.dev4") == "0.1.0-4"
    assert sync_module._desktop_version("0.1.0") == "0.1.0"
    with pytest.raises(ValueError, match="MAJOR.MINOR.PATCH"):
        sync_module._desktop_version("0.1.0.1")


@pytest.mark.unit
def test_version_sync_updates_every_generated_product_consumer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_version_fixture(tmp_path)
    sync_module = _load_sync_module()
    monkeypatch.setattr(sync_module, "ROOT", str(tmp_path))

    sync_module.generate()

    assert 'version = "0.1.0.000dev"' in (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    package = loads_json((tmp_path / "apps/desktop/package.json").read_text(encoding="utf-8"))
    package_lock = loads_json((tmp_path / "apps/desktop/package-lock.json").read_text(encoding="utf-8"))
    project_packages = loads_json((tmp_path / "src/paradev/resources/release/project-packages.json").read_text(encoding="utf-8"))
    assert package["version"] == "0.1.0-0"
    assert package_lock["version"] == "0.1.0-0"
    assert package_lock["packages"][""]["version"] == "0.1.0-0"
    assert project_packages["paradev_version"] == "0.1.0.000dev"
    assert project_packages["desktop_version"] == "0.1.0-0"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("relative_path", "synced_version", "drifted_version"),
    (
        ("pyproject.toml", 'version = "0.1.0.000dev"', 'version = "0.1.0"'),
        (
            "apps/desktop/package.json",
            '"version": "0.1.0-0"',
            '"version": "0.1.0"',
        ),
        (
            "src/paradev/resources/release/project-packages.json",
            '"desktop_version": "0.1.0-0"',
            '"desktop_version": "0.1.0"',
        ),
    ),
)
def test_version_check_reports_drift_without_modifying_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    relative_path: str,
    synced_version: str,
    drifted_version: str,
) -> None:
    _write_version_fixture(tmp_path)
    sync_module = _load_sync_module()
    monkeypatch.setattr(sync_module, "ROOT", str(tmp_path))
    sync_module.generate()
    metadata_path = tmp_path / relative_path
    drifted = metadata_path.read_text(encoding="utf-8").replace(
        synced_version,
        drifted_version,
    )
    metadata_path.write_text(drifted, encoding="utf-8")

    with pytest.raises(SystemExit) as error:
        sync_module.generate(check=True)

    assert error.value.code == 1
    assert f"Generated metadata out of date: {relative_path}" in capsys.readouterr().err
    assert metadata_path.read_text(encoding="utf-8") == drifted


@pytest.mark.unit
def test_repository_product_versions_are_synced_and_backend_reports_canonical(
    capsys: pytest.CaptureFixture[str],
) -> None:
    sync_module = _load_sync_module()

    sync_module.generate(check=True)

    package_version = sync_module._package_version()
    package = loads_json((ROOT / "apps/desktop/package.json").read_text(encoding="utf-8"))
    backend_source = (ROOT / "src/paradev/desktop/backend.py").read_text(encoding="utf-8")
    assert package["version"] == sync_module._desktop_version(package_version)
    assert re.search(r'"paradevVersion":\s*paradev\.__version__', backend_source)
    assert "Generated metadata is up to date." in capsys.readouterr().out
