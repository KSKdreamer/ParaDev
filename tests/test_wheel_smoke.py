from __future__ import annotations

# heaven-style-scan: standalone-control-plane

import argparse
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
from types import ModuleType

import pytest

HELPER = Path("scripts/wheel_smoke.py")
RELEASE_WORKFLOW = Path(".github/workflows/release.yml")


def _load_helper() -> ModuleType:
    name = "paradev_test_wheel_smoke_helper"
    spec = importlib.util.spec_from_file_location(name, HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _args(**overrides: object) -> argparse.Namespace:
    values: dict[str, object] = {
        "clean": False,
        "cached": False,
        "family": [],
        "module": [],
        "workers": None,
        "timeout_seconds": 2400.0,
        "startup_timeout_seconds": 60.0,
        "poll_seconds": 0.5,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_wheel_smoke_build_specs_preserve_safe_matrix_order() -> None:
    helper = _load_helper()

    specs = helper._build_specs(
        _args(
            clean=True,
            cached=True,
            family=["technology", "military_industrial_organization"],
            module=["technology/TECHNOLOGY_FIREARM_I"],
        )
    )

    assert [(spec.label, spec.mode, spec.target) for spec in specs] == [
        ("clean whole project", "full", None),
        ("cached whole project", "cached", None),
        ("family technology", "cached", {"kind": "family", "id": "technology"}),
        (
            "family military_industrial_organization",
            "cached",
            {"kind": "family", "id": "military_industrial_organization"},
        ),
        (
            "module technology/TECHNOLOGY_FIREARM_I",
            "cached",
            {"kind": "module", "id": "technology/TECHNOLOGY_FIREARM_I"},
        ),
    ]


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"family": ["technology", " technology "]}, "family IDs must not be repeated"),
        ({"module": ["  "]}, "module IDs must not be empty"),
        ({"workers": 0}, "--workers must be at least 1"),
        ({"poll_seconds": 0.01}, "--poll-seconds must be between"),
    ],
)
def test_wheel_smoke_rejects_ambiguous_or_unsafe_inputs(
    overrides: dict[str, object],
    message: str,
) -> None:
    helper = _load_helper()
    args = _args(**overrides)

    with pytest.raises(helper.SmokeError, match=message):
        if "family" in overrides or "module" in overrides:
            helper._build_specs(args)
        else:
            helper._validate_args(args)


def test_wheel_smoke_runtime_environment_hides_developer_tools(tmp_path: Path) -> None:
    helper = _load_helper()
    home = tmp_path / "home"
    runtime_temp = tmp_path / "tmp"
    runtime_bin = tmp_path / "bin"
    mod_root = tmp_path / "mod"
    project = tmp_path / "project"

    environment = helper._runtime_environment(
        home=home,
        runtime_temp=runtime_temp,
        runtime_bin=runtime_bin,
        mod_root=mod_root,
        project=project,
    )

    assert environment["HOME"] == str(home)
    assert environment["PARADEV_ROOT"] == str(home / ".paradev")
    assert environment["PARADEV_PROJECTS"] == str(project)
    assert environment["PARADEV_HOI4_MOD_ROOT"] == str(mod_root)
    assert environment["PATH"] == str(runtime_bin)
    assert "PYTHONPATH" not in environment
    assert "VIRTUAL_ENV" not in environment


def test_wheel_smoke_runtime_identity_is_loaded_from_disposable_venv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _load_helper()
    venv = tmp_path / "venv"
    module = venv / "lib" / "python3.12" / "site-packages" / "paradev" / "__init__.py"
    module.parent.mkdir(parents=True)
    module.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        helper.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout=(
                '{"paradev_version":"0.1.0.0.dev0","heavenbase_version":"0.1.2.2",'
                '"fastmcp_version":"4.0.0b2","mcp_version":"2.0.0",'
                f'"module_path":{helper.json.dumps(str(module))}}}'
            ),
            stderr="",
        ),
    )

    assert helper._runtime_identity(
        tmp_path / "venv" / "bin" / "python",
        venv=venv,
        environment={"PATH": str(tmp_path / "bin")},
        working_directory=tmp_path,
    ) == {
        "paradev_version": "0.1.0.0.dev0",
        "heavenbase_version": "0.1.2.2",
        "fastmcp_version": "4.0.0b2",
        "mcp_version": "2.0.0",
        "package_location": "isolated_venv",
    }


def test_wheel_smoke_keeps_venv_python_launcher_path(tmp_path: Path) -> None:
    helper = _load_helper()
    target = tmp_path / "base-python"
    target.write_text("python", encoding="utf-8")
    launcher = tmp_path / "venv" / "bin" / "python"
    launcher.parent.mkdir(parents=True)
    launcher.symlink_to(target)

    assert helper._runtime_executable(tmp_path / "venv", "python") == launcher.absolute()


def test_wheel_smoke_verifies_packaged_frontend_and_deferred_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _load_helper()
    project = tmp_path / "PIHC3"
    project.mkdir()

    def fake_http(_base_url: str, path: str, **_kwargs: object):
        if path == "/":
            return 200, {}, b'<script src="/paradev-runtime-config.js"></script><script src="/assets/app.js"></script>'
        if path == "/assets/app.js":
            return 200, {"content-type": "text/javascript"}, b"console.log('ParaDev')"
        if path == "/paradev-runtime-config.js":
            return 200, {"cache-control": "no-store"}, b"window.location.origin"
        raise AssertionError(path)

    monkeypatch.setattr(helper, "_http", fake_http)
    monkeypatch.setattr(
        helper,
        "_json_response",
        lambda _base_url, _path: {
            "schema": helper.DESKTOP_STATE_SCHEMA,
            "active_project": {
                "project_id": "PIHC3",
                "root": str(project),
                "output_root": str(project / "build" / "mod"),
            },
            "browser": None,
        },
    )

    assert helper._verify_frontend("http://127.0.0.1:4817") == {
        "asset_count": 1,
        "probed_asset": "/assets/app.js",
        "same_origin_runtime": True,
    }
    assert helper._verify_project_state("http://127.0.0.1:4817", project, "PIHC3") == {
        "project_id": "PIHC3",
        "project_root": str(project),
        "browser_deferred": True,
        "_output_root": str(project / "build" / "mod"),
    }


def test_wheel_smoke_runs_and_validates_desktop_build(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _load_helper()
    output = tmp_path / "tmp" / "paradev-build" / "result.json"
    output.parent.mkdir(parents=True)
    output.write_text(
        '{"schema":"paradev.build.summary.v1","summary":{"module_count":1,'
        '"collection_count":0,"artifact_count":4,"diagnostic_count":0,'
        '"error_count":0,"blocked":false}}',
        encoding="utf-8",
    )
    calls: list[tuple[str, str, object]] = []

    def fake_json(_base_url: str, path: str, *, method: str = "GET", payload=None, **_kwargs):
        calls.append((method, path, payload))
        if path == "/desktop/builds":
            return {"schema": helper.BUILD_RUN_SCHEMA, "status": "running", "runId": "build-1"}
        return {
            "schema": helper.BUILD_RUN_SCHEMA,
            "status": "completed",
            "runId": "build-1",
            "exitCode": 0,
            "outputPath": str(output),
        }

    monkeypatch.setattr(helper, "_json_response", fake_json)

    result = helper._run_build(
        "http://127.0.0.1:4817",
        tmp_path / "PIHC3",
        helper.BuildSpec("module smoke", "cached", {"kind": "module", "id": "idea/test"}),
        runtime_root=tmp_path,
        workers=4,
        strict_metadata=False,
        timeout_seconds=10,
        poll_seconds=0.05,
    )

    assert result["summary"] == {
        "module_count": 1,
        "collection_count": 0,
        "artifact_count": 4,
        "diagnostic_count": 0,
        "error_count": 0,
        "blocked": False,
    }
    assert calls[0] == (
        "POST",
        "/desktop/builds",
        {
            "projectRoot": str(tmp_path / "PIHC3"),
            "mode": "cached",
            "strictMetadata": False,
            "parallelism": 4,
            "target": {"kind": "module", "id": "idea/test"},
        },
    )
    assert calls[1][0:2] == ("GET", "/desktop/builds/status?run_id=build-1")


def test_wheel_smoke_output_snapshot_tracks_paths_and_exact_bytes(tmp_path: Path) -> None:
    helper = _load_helper()
    mod_root = tmp_path / "mod"
    (mod_root / "PIHC3/common").mkdir(parents=True)
    source = mod_root / "PIHC3/common/ideas.txt"
    source.write_bytes(b"ideas = {}\n")
    control = mod_root / "PIHC3/.paradev-publication.json"
    control.write_text('{"path":"first"}\n', encoding="utf-8")

    first = helper._output_snapshot(mod_root)
    control.write_text('{"path":"other"}\n', encoding="utf-8")
    second = helper._output_snapshot(mod_root)
    source.write_bytes(b"ideas = { changed = yes }\n")
    changed = helper._output_snapshot(mod_root)

    assert first == second
    assert first["schema"] == "paradev.output-snapshot.v1"
    assert first["file_count"] == 1
    assert first["byte_count"] == 11
    assert first["control_file_count"] == 1
    assert first["control_byte_count"] == 17
    assert second["control_byte_count"] == 17
    assert changed["sha256"] != first["sha256"]


def test_wheel_smoke_rejects_ambiguous_publication_roots(tmp_path: Path) -> None:
    helper = _load_helper()
    mod_root = tmp_path / "mod"
    for name in ("PIHC3", "other"):
        claimed = mod_root / name
        claimed.mkdir(parents=True)
        (claimed / ".paradev-publication.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(
        helper.SmokeError,
        match="multiple ParaDev publication roots",
    ):
        helper._output_snapshot(mod_root)


def test_wheel_smoke_requires_partial_output_to_match_clean_baseline(
    tmp_path: Path,
) -> None:
    helper = _load_helper()
    mod_root = tmp_path / "mod"
    mod_root.mkdir()
    output = mod_root / "PIHC3.txt"
    output.write_text("clean\n", encoding="utf-8")
    clean, baseline = helper._publication_evidence(
        mod_root,
        clean_baseline=None,
        establish_baseline=True,
    )

    unchanged, _ = helper._publication_evidence(
        mod_root,
        clean_baseline=baseline,
        establish_baseline=False,
    )
    output.write_text("partial changed output\n", encoding="utf-8")

    assert clean["matches_clean_baseline"] is True
    assert unchanged == clean
    with pytest.raises(helper.SmokeError, match="differs from the clean whole-project baseline"):
        helper._publication_evidence(
            mod_root,
            clean_baseline=baseline,
            establish_baseline=False,
        )


def test_wheel_smoke_interrupts_failed_or_timed_out_build(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = _load_helper()
    calls: list[tuple[str, str, object]] = []

    def fake_json(_base_url: str, path: str, *, method: str = "GET", payload=None, **_kwargs):
        calls.append((method, path, payload))
        if path == "/desktop/builds":
            return {"schema": helper.BUILD_RUN_SCHEMA, "status": "running", "runId": "build-2"}
        if path == "/desktop/builds/interrupt":
            return {"schema": helper.BUILD_RUN_SCHEMA, "status": "failed", "runId": "build-2"}
        return {
            "schema": helper.BUILD_RUN_SCHEMA,
            "status": "failed",
            "runId": "build-2",
            "exitCode": 1,
            "errorSummary": "compiler failed",
        }

    monkeypatch.setattr(helper, "_json_response", fake_json)

    with pytest.raises(helper.SmokeError, match="module smoke finished as failed: compiler failed"):
        helper._run_build(
            "http://127.0.0.1:4817",
            tmp_path / "PIHC3",
            helper.BuildSpec("module smoke", "cached", {"kind": "module", "id": "idea/test"}),
            runtime_root=tmp_path,
            workers=None,
            strict_metadata=False,
            timeout_seconds=10,
            poll_seconds=0.05,
        )

    assert calls[-1] == ("POST", "/desktop/builds/interrupt", {"runId": "build-2"})


def test_wheel_smoke_rejects_build_output_outside_disposable_runtime(tmp_path: Path) -> None:
    helper = _load_helper()
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")
    runtime = tmp_path / "runtime"
    runtime.mkdir()

    with pytest.raises(helper.SmokeError, match="escaped the disposable runtime"):
        helper._load_build_summary(str(outside), runtime_root=runtime)


def test_release_workflow_builds_and_smokes_verified_gui_wheel() -> None:
    workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")

    assert "actions/setup-node@v4" in workflow
    assert 'node-version: "22"' in workflow
    assert "uv sync --all-extras --frozen" in workflow
    assert "bash scripts/sync-env.bash --check --no-heavenbase" in workflow
    assert "bash scripts/flake.bash --ci" in workflow
    assert "bash scripts/test.bash" in workflow
    assert "npm --prefix apps/desktop test" in workflow
    assert 'cd "${RUNNER_TEMP}"' in workflow
    assert 'SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"' in workflow
    assert "export SOURCE_DATE_EPOCH" in workflow
    assert 'python -m build --sdist --outdir "${PROJECT_ROOT}/dist" "${PROJECT_ROOT}"' in workflow
    assert workflow.count('bash "${PROJECT_ROOT}/scripts/build-wheel.bash"') == 2
    assert 'cmp "${PRIMARY_WHEEL}" "${REPRO_WHEEL}"' in workflow
    assert "python -m build --sdist --wheel" not in workflow
    assert "paradev dashboard --help" in workflow
    assert workflow.count("bash scripts/smoke-wheel-gui.bash") == 2
    assert "python scripts/verify_wheel_inventory.py" in workflow
    assert "--project demos/assets/projects/minimal" in workflow
    assert "--copy-project" in workflow
    assert "--expect-project-id minimal_hoi4" in workflow
    assert "--clean" in workflow
    assert "--cached" in workflow
    assert "--family focus" in workflow
    assert "--module focus/GER_sample" in workflow
