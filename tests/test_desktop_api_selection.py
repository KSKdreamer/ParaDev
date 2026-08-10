import base64
import os
import signal
import subprocess
import sys
import textwrap
import time
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from types import MappingProxyType, SimpleNamespace

import heavenbase as hb
import paradev.desktop as desktop
import pytest
from heavenbase.utils import dget, dump_json, load_txt

from api_selection_contracts import (
    assert_api_selection_projection,
    assert_api_selection_rejects_invalid_selectors,
)
from paradev.desktop import (
    BUILD_RUNS_SCHEMA,
    DESKTOP_CONFIG_KEYS,
    DesktopBuildRegistry,
    desktop_build_runs,
    desktop_build_status,
    desktop_chat_profiles,
    desktop_config_rows,
    desktop_binary_source,
    desktop_browser_cache_path,
    desktop_interrupt_build,
    desktop_read_config_value,
    desktop_hoi4_launch_command,
    desktop_open_path,
    desktop_open_path_command,
    desktop_path_status,
    desktop_project_build_command,
    desktop_read_app_config,
    desktop_read_binary_source,
    desktop_read_text_source,
    desktop_reset_chat_profile,
    desktop_read_thumbnail_cache,
    desktop_run_hoi4,
    desktop_source_path,
    desktop_start_build,
    desktop_thumbnail_cache_path,
    desktop_write_app_config,
    desktop_write_browser_cache,
    desktop_write_config_value,
    desktop_write_thumbnail_cache,
    get_desktop_api_selection,
    get_desktop_api_table,
    render_desktop_typescript,
    render_desktop_api_reference_markdown,
)
from paradev.config import CM_PARADEV, DEFAULT_CONFIG
from paradev.desktop import local as desktop_local
from paradev.desktop.shell import desktop_hoi4_launch_readiness
from paradev.sdk import Project

_THUMBNAIL_PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk" "+A8AAQUBAScY42YAAAAASUVORK5CYII=")


class FakeBuildProcess:
    def __init__(self) -> None:
        self.returncode: int | None = None
        self.killed = False
        self.terminated = False

    def poll(self) -> int | None:
        return self.returncode

    def terminate(self) -> None:
        self.terminated = True
        self.returncode = -15

    def kill(self) -> None:
        self.killed = True
        self.returncode = -9

    def wait(self, timeout: float | None = None) -> int:
        if self.returncode is None:
            self.returncode = 0
        return self.returncode


def _restore_cm_paradev_value(key: str, value: object) -> None:
    if value is None or (isinstance(value, Mapping) and value.get("__HB_REMOVE__") is True):
        CM_PARADEV.unset(key)
    else:
        CM_PARADEV.set(key, value)


@contextmanager
def _temporary_unset_cm_paradev_value(key: str) -> Iterator[None]:
    previous = CM_PARADEV.get(key, default=None)
    try:
        CM_PARADEV.unset(key)
        yield
    finally:
        _restore_cm_paradev_value(key, previous)


def _fake_heavenbase(llm_type: type) -> SimpleNamespace:
    class FakeLLMEngine:
        def apply(self, spec: object) -> dict[str, object]:
            assert spec is llm_type.spec
            runtime = getattr(spec, "runtime")
            return dict(runtime())

    return SimpleNamespace(LLM=llm_type, LLMEngine=FakeLLMEngine)


def test_heavenbase_llm_engine_applies_resolved_route_offline() -> None:
    engine = hb.LLMEngine(context=hb.DEFAULT_CONTEXT)
    spec = engine.resolve(
        {
            "preset": "chat",
            "model": "deepseek-v4-flash",
            "provider": "deepseek",
            "gateway": "openai",
            "api_key": "not-a-real-key",
            "base_url": "https://proxy.example/v1",
            "temperature": 0,
            "max_tokens": 8,
        }
    )

    runtime = engine.apply(spec)

    assert isinstance(spec, hb.LLMSpec)
    assert spec.data["model"] == "deepseek-v4-flash"
    assert runtime["gateway"] == "openai"
    assert runtime["model"] == "deepseek-chat"
    assert runtime["base_url"] == "https://proxy.example/v1"
    assert runtime["args"]["max_tokens"] == 8


def test_desktop_project_build_command_matches_desktop_build_flags(tmp_path: Path, cm_paradev_lock) -> None:
    progress_path = tmp_path / "progress.jsonl"

    with _temporary_unset_cm_paradev_value("paradev.build.strict_metadata"):
        assert desktop_project_build_command(
            "/tmp/PIHC3",
            mode="cached",
            profile="hoi4",
            strict_metadata=True,
            progress_jsonl=progress_path,
        ) == [
            "uv",
            "run",
            "paradev",
            "build",
            "/tmp/PIHC3",
            "--profile",
            "hoi4",
            "--strict-metadata",
            "--emit-artifacts",
            "--emit-manifests",
            "--no-sync-launcher-descriptor",
            "--progress-jsonl",
            str(progress_path),
            "--summary",
            "--json",
        ]
        assert "--no-strict-metadata" in desktop_project_build_command("/tmp/PIHC3", strict_metadata=False)
        assert desktop_project_build_command("/tmp/PIHC3", mode="full") == [
            "uv",
            "run",
            "paradev",
            "build",
            "/tmp/PIHC3",
            "--emit-artifacts",
            "--emit-manifests",
            "--no-sync-launcher-descriptor",
            "--full-rebuild",
            "--summary",
            "--json",
        ]
        assert desktop_project_build_command(
            "/tmp/PIHC3",
            target={"kind": "family", "id": "entity", "family": "entity"},
        ) == [
            "uv",
            "run",
            "paradev",
            "build",
            "/tmp/PIHC3",
            "--family",
            "entity",
            "--emit-artifacts",
            "--emit-manifests",
            "--no-sync-launcher-descriptor",
            "--summary",
            "--json",
        ]
        assert desktop_project_build_command(
            "/tmp/PIHC3",
            target={"kind": "collection", "id": "GER", "family": "country"},
            parallelism=4,
        ) == [
            "uv",
            "run",
            "paradev",
            "build",
            "/tmp/PIHC3",
            "--collection",
            "GER",
            "--family",
            "country",
            "--parallelism",
            "4",
            "--emit-artifacts",
            "--emit-manifests",
            "--no-sync-launcher-descriptor",
            "--summary",
            "--json",
        ]


def test_desktop_project_build_command_uses_configured_strict_metadata(tmp_path: Path, cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.build.strict_metadata", default=None)
    try:
        CM_PARADEV.set("paradev.build.strict_metadata", True)

        configured = desktop_project_build_command(tmp_path, mode="cached")
        explicit_loose = desktop_project_build_command(tmp_path, mode="cached", strict_metadata=False)
    finally:
        if previous is None or isinstance(previous, MappingProxyType):
            CM_PARADEV.unset("paradev.build.strict_metadata")
        else:
            CM_PARADEV.set("paradev.build.strict_metadata", previous)

    assert "--strict-metadata" in configured
    assert "--no-strict-metadata" not in configured
    assert "--strict-metadata" not in explicit_loose
    assert "--no-strict-metadata" in explicit_loose


def test_desktop_project_build_command_rejects_invalid_requests() -> None:
    with pytest.raises(ValueError, match="project root cannot be empty"):
        desktop_project_build_command(" ")
    with pytest.raises(ValueError, match="Unsupported build mode: incremental"):
        desktop_project_build_command("/tmp/PIHC3", mode="incremental")
    with pytest.raises(ValueError, match="Unsupported build target kind: source"):
        desktop_project_build_command("/tmp/PIHC3", target={"kind": "source", "id": "focuses.txt"})
    with pytest.raises(ValueError, match="A full rebuild cannot be combined"):
        desktop_project_build_command(
            "/tmp/PIHC3",
            mode="full",
            target={"kind": "module", "id": "focus_tree/GER_main"},
        )
    with pytest.raises(ValueError, match="build parallelism must be at least 1"):
        desktop_project_build_command("/tmp/PIHC3", parallelism=0)


def test_desktop_build_lifecycle_exposes_python_facade(monkeypatch) -> None:
    import paradev.desktop.builds as desktop_builds

    processes: list[FakeBuildProcess] = []
    popen_calls: list[dict[str, object]] = []

    def fake_popen(command, cwd=None, stdout=None, stderr=None, start_new_session=False):
        process = FakeBuildProcess()
        processes.append(process)
        popen_calls.append(
            {
                "command": list(command),
                "cwd": str(cwd),
                "start_new_session": start_new_session,
            }
        )
        return process

    monkeypatch.setattr(desktop_builds.subprocess, "Popen", fake_popen)

    started = desktop_start_build(
        "/tmp/PIHC3",
        mode="cached",
        profile="hoi4",
        strict_metadata=True,
        parallelism=3,
        target={"kind": "module", "id": "focus_tree/GER_main", "family": "focus_tree"},
    )

    assert started["schema"] == "paradev.desktop.build-run.v1"
    assert started["status"] == "running"
    assert started["mode"] == "cached"
    assert started["target"] == {
        "kind": "module",
        "id": "focus_tree/GER_main",
        "family": "focus_tree",
    }
    assert "--progress-jsonl" in popen_calls[0]["command"]
    assert "--parallelism" in popen_calls[0]["command"]
    assert popen_calls[0]["command"][:4] == [sys.executable, "-m", "paradev", "build"]
    assert Path(str(popen_calls[0]["cwd"])) == Path("/tmp/PIHC3")

    running = desktop_build_status(str(started["runId"]))

    assert running["status"] == "running"
    assert running["runId"] == started["runId"]

    processes[0].returncode = 0
    completed = desktop_build_status(str(started["runId"]))

    assert completed["status"] == "completed"
    assert completed["exitCode"] == 0

    second = desktop_start_build("/tmp/PIHC3", mode="cached")
    interrupted = desktop_interrupt_build(str(second["runId"]))

    assert interrupted["status"] == "interrupted"
    assert processes[1].terminated is True


def test_desktop_build_registry_scopes_conflicting_active_builds_by_project(monkeypatch, tmp_path: Path) -> None:
    import paradev.desktop.builds as desktop_builds

    processes: list[FakeBuildProcess] = []

    def fake_popen(command, cwd=None, stdout=None, stderr=None, start_new_session=False):
        process = FakeBuildProcess()
        processes.append(process)
        return process

    monkeypatch.setattr(desktop_builds.subprocess, "Popen", fake_popen)
    registry = DesktopBuildRegistry()
    alpha_root = tmp_path / "alpha"
    beta_root = tmp_path / "beta"
    alpha_root.mkdir()
    beta_root.mkdir()
    (alpha_root / "nested").mkdir()
    shared_target = {"kind": "module", "id": "focus_tree/GER_main"}

    with pytest.raises(ValueError, match="A full rebuild cannot be combined"):
        registry.start(alpha_root, mode=" full ", target=shared_target)
    assert processes == []

    alpha_partial = registry.start(alpha_root, target=shared_target)

    with pytest.raises(ValueError, match="already running"):
        registry.start(alpha_root / "nested" / "..", target=shared_target)
    with pytest.raises(ValueError, match="already running"):
        registry.start(
            alpha_root,
            target={
                "kind": " module ",
                "id": " focus_tree/GER_main ",
                "family": " focus_tree ",
            },
        )
    alpha_collection = registry.start(alpha_root, target={"kind": "collection", "id": "shared"})
    with pytest.raises(ValueError, match="already running"):
        registry.start(
            alpha_root,
            target={"kind": "collection", "id": "shared", "family": "focus_tree"},
        )
    with pytest.raises(ValueError, match="Cannot start a full ParaDev build"):
        registry.start(alpha_root)
    assert {run["runId"] for run in registry.runs(alpha_root / "nested" / "..")["runs"]} == {
        alpha_partial["runId"],
        alpha_collection["runId"],
    }

    beta_partial = registry.start(beta_root, target=shared_target)
    assert registry.interrupt(str(beta_partial["runId"]))["status"] == "interrupted"

    beta_full = registry.start(beta_root)

    with pytest.raises(ValueError, match="Cannot start a partial ParaDev build"):
        registry.start(beta_root, target={"kind": "module", "id": "focus_tree/ITA_main"})

    assert registry.interrupt(str(beta_full["runId"]))["status"] == "interrupted"
    assert registry.interrupt(str(alpha_collection["runId"]))["status"] == "interrupted"
    assert registry.interrupt(str(alpha_partial["runId"]))["status"] == "interrupted"

    alpha_full = registry.start(alpha_root)
    beta_full = registry.start(beta_root)

    with pytest.raises(ValueError, match="Cannot start a partial ParaDev build"):
        registry.start(alpha_root, target={"kind": "module", "id": "focus_tree/ITA_main"})

    assert registry.interrupt(str(alpha_full["runId"]))["status"] == "interrupted"
    assert registry.interrupt(str(beta_full["runId"]))["status"] == "interrupted"
    assert all(process.terminated for process in processes)
    registry.close()


def test_desktop_build_registry_default_selection_uses_oldest_run_with_stable_tie_break(monkeypatch, tmp_path: Path) -> None:
    import paradev.desktop.builds as desktop_builds

    processes: list[FakeBuildProcess] = []
    run_ids = iter(["partial-oldest", "full-newer", "tie-z", "tie-a"])
    clock_ms = iter([100, 200, 300, 300, 400, 500, 600, 700])

    def fake_popen(command, cwd=None, stdout=None, stderr=None, start_new_session=False):
        process = FakeBuildProcess()
        processes.append(process)
        return process

    monkeypatch.setattr(desktop_builds, "_desktop_run_id", lambda: next(run_ids))
    monkeypatch.setattr(desktop_builds, "_desktop_build_output_path", lambda name: tmp_path / name)
    monkeypatch.setattr(desktop_builds, "_unix_time_millis", lambda: next(clock_ms))
    monkeypatch.setattr(desktop_builds.subprocess, "Popen", fake_popen)
    registry = DesktopBuildRegistry()

    partial = registry.start("/tmp/Alpha", target={"kind": "module", "id": "focus_tree/GER_main"})
    registry.start("/tmp/Beta")
    registry.start("/tmp/Gamma", target={"kind": "module", "id": "focus_tree/ITA_main"})
    tied = registry.start("/tmp/Delta")

    for invalid_run_id in ("", "   "):
        with pytest.raises(ValueError, match="build run id must be a non-empty string"):
            registry.status(invalid_run_id)
        with pytest.raises(ValueError, match="build run id must be a non-empty string"):
            registry.interrupt(invalid_run_id)
    assert registry.status()["runId"] == partial["runId"]
    assert registry.interrupt()["runId"] == partial["runId"]
    assert registry.interrupt("full-newer")["status"] == "interrupted"
    assert registry.status(f"  {tied['runId']}  ")["runId"] == tied["runId"]
    assert registry.interrupt()["runId"] == tied["runId"]
    registry.close()
    assert all(process.terminated for process in processes)


def test_desktop_build_registry_lists_and_retains_terminal_runs(monkeypatch) -> None:
    import paradev.desktop.builds as desktop_builds

    processes: list[FakeBuildProcess] = []

    def fake_popen(command, cwd=None, stdout=None, stderr=None, start_new_session=False):
        process = FakeBuildProcess()
        processes.append(process)
        return process

    monkeypatch.setattr(desktop_builds.subprocess, "Popen", fake_popen)
    registry = DesktopBuildRegistry()
    first = registry.start("/tmp/PIHC3", target={"kind": "module", "id": "focus_tree/GER_main"})
    second = registry.start("/tmp/Other", target={"kind": "module", "id": "focus_tree/GER_main"})

    listed = registry.runs("/tmp/PIHC3")

    assert listed["schema"] == BUILD_RUNS_SCHEMA
    assert [run["runId"] for run in listed["runs"]] == [first["runId"]]
    processes[0].returncode = 0
    completed = registry.status(str(first["runId"]))
    assert completed["status"] == "completed"
    assert registry.status(str(first["runId"])) == completed
    assert registry.interrupt(str(first["runId"])) == completed

    replacement = registry.start("/tmp/PIHC3", target={"kind": "module", "id": "focus_tree/GER_main"})
    all_runs = registry.runs()
    run_order = [(run["startedAtMs"], run["runId"]) for run in all_runs["runs"]]

    assert run_order == sorted(run_order)
    assert {run["runId"] for run in all_runs["runs"]} == {
        first["runId"],
        second["runId"],
        replacement["runId"],
    }
    registry.close()
    registry.close()
    assert processes[1].terminated is True
    assert processes[2].terminated is True
    with pytest.raises(RuntimeError, match="registry is closed"):
        registry.start("/tmp/PIHC3", target={"kind": "module", "id": "idea/demo"})


def test_desktop_build_registry_removes_created_files_when_spawn_fails(monkeypatch, tmp_path: Path) -> None:
    import paradev.desktop.builds as desktop_builds

    captured_streams: list[object] = []

    def failing_popen(command, cwd=None, stdout=None, stderr=None, start_new_session=False):
        captured_streams.extend([stdout, stderr])
        raise OSError("spawn failed")

    monkeypatch.setattr(desktop_builds, "_desktop_build_output_path", lambda name: tmp_path / name)
    monkeypatch.setattr(desktop_builds.subprocess, "Popen", failing_popen)
    registry = DesktopBuildRegistry()

    with pytest.raises(OSError, match="spawn failed"):
        registry.start(tmp_path)

    assert captured_streams
    assert all(getattr(stream, "closed", False) for stream in captured_streams)
    assert list(tmp_path.iterdir()) == []
    assert registry.runs()["runs"] == []
    registry.close()


def test_desktop_build_registry_removes_output_when_error_log_open_fails(monkeypatch, tmp_path: Path) -> None:
    import paradev.desktop.builds as desktop_builds

    original_open = Path.open

    def failing_error_log_open(path: Path, *args, **kwargs):
        if path.name.endswith(".stderr.log"):
            raise OSError("error log unavailable")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(desktop_builds, "_desktop_build_output_path", lambda name: tmp_path / name)
    monkeypatch.setattr(Path, "open", failing_error_log_open)
    registry = DesktopBuildRegistry()

    with pytest.raises(OSError, match="error log unavailable"):
        registry.start(tmp_path)

    assert list(tmp_path.iterdir()) == []
    assert registry.runs()["runs"] == []
    registry.close()


def test_desktop_build_registry_successful_close_removes_session_temp_files(monkeypatch, tmp_path: Path) -> None:
    import paradev.desktop.builds as desktop_builds

    process = FakeBuildProcess()
    monkeypatch.setattr(desktop_builds, "_desktop_build_output_path", lambda name: tmp_path / name)
    monkeypatch.setattr(desktop_builds.subprocess, "Popen", lambda *args, **kwargs: process)
    registry = DesktopBuildRegistry()
    started = registry.start(tmp_path)
    temp_paths = [Path(str(started[field])) for field in ("outputPath", "errorPath", "progressPath")]
    temp_paths[2].write_text('{"phase":"emit"}\n', encoding="utf-8")

    registry.close()

    assert process.terminated is True
    assert all(not path.exists() for path in temp_paths)
    assert registry.status(str(started["runId"]))["status"] == "interrupted"


@pytest.mark.skipif(os.name == "nt", reason="requires POSIX process groups")
@pytest.mark.parametrize("action", ["interrupt", "close"])
def test_desktop_build_registry_reaps_descendants_after_group_leader_exits(
    monkeypatch,
    tmp_path: Path,
    action: str,
) -> None:
    import paradev.desktop.builds as desktop_builds

    child_marker = tmp_path / "descendant.pid"
    child_script = textwrap.dedent("""
        import os
        import signal
        import sys
        import time
        from pathlib import Path

        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        Path(sys.argv[1]).write_text(str(os.getpid()), encoding="utf-8")
        time.sleep(60)
        """)
    parent_script = textwrap.dedent("""
        import subprocess
        import sys

        child = subprocess.Popen([sys.executable, "-c", sys.argv[2], sys.argv[1]])
        child.wait()
        """)

    def build_command(project_root, **kwargs):
        return [sys.executable, "-c", parent_script, str(child_marker), child_script]

    monkeypatch.setattr(desktop_builds, "desktop_project_build_command", build_command)
    monkeypatch.setattr(desktop_builds, "_desktop_build_output_path", lambda name: tmp_path / name)
    monkeypatch.setattr(desktop_builds, "_BUILD_TERMINATION_GRACE_SECONDS", 0.1)
    monkeypatch.setattr(desktop_builds, "_BUILD_REAP_POLL_SECONDS", 0.005)
    registry = DesktopBuildRegistry()
    started = registry.start(tmp_path)
    process = registry._processes[str(started["runId"])]["process"]
    parent_pid = process.pid
    child_pid: int | None = None
    try:
        deadline = time.monotonic() + 5
        while not child_marker.is_file() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert child_marker.is_file(), "build descendant did not publish its pid"
        child_pid = int(child_marker.read_text(encoding="utf-8"))

        if action == "interrupt":
            terminal = registry.interrupt(str(started["runId"]))
        else:
            registry.close()
            terminal = registry.status(str(started["runId"]))

        assert terminal["status"] == "interrupted"
        with pytest.raises(ProcessLookupError):
            os.kill(child_pid, 0)
    finally:
        try:
            os.killpg(parent_pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        if child_pid is not None:
            try:
                os.kill(child_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        registry.close()


@pytest.mark.skipif(os.name == "nt", reason="requires POSIX process groups")
def test_desktop_build_process_group_permission_error_remains_active(
    monkeypatch,
) -> None:
    import paradev.desktop.builds as desktop_builds

    process = SimpleNamespace(pid=1234)

    def denied_killpg(pid, signal_number):
        assert pid == process.pid
        assert signal_number == 0
        raise PermissionError("process group is temporarily unsignalable")

    monkeypatch.setattr(desktop_builds.os, "killpg", denied_killpg)

    assert desktop_builds._build_process_group_active(process) is True


def test_desktop_build_terminal_sequence_survives_wall_clock_rollback(monkeypatch, tmp_path: Path) -> None:
    import paradev.desktop.builds as desktop_builds

    processes: list[FakeBuildProcess] = []
    clock = iter([10_000, 20_000, 9_000, 10_000])

    def fake_popen(*args, **kwargs):
        process = FakeBuildProcess()
        processes.append(process)
        return process

    monkeypatch.setattr(desktop_builds, "_desktop_build_output_path", lambda name: tmp_path / name)
    monkeypatch.setattr(desktop_builds, "_unix_time_millis", lambda: next(clock))
    monkeypatch.setattr(desktop_builds.subprocess, "Popen", fake_popen)
    registry = DesktopBuildRegistry()

    first = registry.start(tmp_path)
    assert first["terminalSequence"] is None
    processes[0].returncode = 0
    first_terminal = registry.status(str(first["runId"]))
    second = registry.start(tmp_path)
    processes[1].returncode = 0
    second_terminal = registry.status(str(second["runId"]))

    assert first_terminal["finishedAtMs"] == 20_000
    assert first_terminal["terminalSequence"] == 0
    assert second_terminal["finishedAtMs"] == 10_000
    assert second_terminal["terminalSequence"] == 1
    assert registry.status(str(first["runId"]))["terminalSequence"] == 0
    assert registry.interrupt(str(second["runId"]))["terminalSequence"] == 1
    listed = {str(payload["runId"]): payload for payload in registry.runs()["runs"]}
    assert listed[str(first["runId"])]["terminalSequence"] == 0
    assert listed[str(second["runId"])]["terminalSequence"] == 1
    registry.close()


def test_desktop_build_registry_caps_terminal_history_without_evicting_active_runs(monkeypatch, tmp_path: Path) -> None:
    import paradev.desktop.builds as desktop_builds

    registry = DesktopBuildRegistry()
    finished_at_ms = [0]
    monkeypatch.setattr(desktop_builds, "_unix_time_millis", lambda: finished_at_ms[0])

    def record(run_id: str, started_at_ms: int) -> dict[str, object]:
        return {
            "command": ["paradev", "build"],
            "error_path": tmp_path / f"{run_id}.stderr.log",
            "mode": "cached",
            "output_path": tmp_path / f"{run_id}.json",
            "process": FakeBuildProcess(),
            "progress_path": tmp_path / f"{run_id}.progress.jsonl",
            "project_key": (str(tmp_path), None),
            "project_root": str(tmp_path),
            "run_id": run_id,
            "started_at_ms": started_at_ms,
            "target": None,
        }

    for index in range(258):
        run_id = f"run-{index:03d}"
        finished_at_ms[0] = 10_000 - index
        if index in {0, 2}:
            current = record(run_id, index)
            for field in ("output_path", "error_path", "progress_path"):
                Path(current[field]).write_text("retained build fixture", encoding="utf-8")
            registry._processes[run_id] = current
        else:
            registry._processes[run_id] = record(run_id, index)
        registry._retain_terminal(run_id, "completed", 0)

    active_run_id = "active-258"
    registry._processes[active_run_id] = record(active_run_id, 258)
    listed = registry.runs()["runs"]

    assert len(registry._finished) == 256
    assert "run-000" not in registry._finished
    assert "run-001" not in registry._finished
    assert "run-000" not in registry._finished_project_keys
    assert "run-000" not in registry._finished_sequences
    assert "run-002" in registry._finished
    assert "run-257" in registry._finished
    assert not (tmp_path / "run-000.json").exists()
    assert not (tmp_path / "run-000.stderr.log").exists()
    assert not (tmp_path / "run-000.progress.jsonl").exists()
    assert (tmp_path / "run-002.json").exists()
    assert len(listed) == 257
    assert active_run_id in {str(payload["runId"]) for payload in listed}
    assert registry.status("run-000")["status"] == "idle"
    assert registry.status("run-257")["status"] == "completed"
    finished_at_ms[0] = 2_000
    registry.close()


@pytest.mark.skipif(
    os.name == "nt" or not hasattr(os, "fork"),
    reason="requires POSIX fork and process groups",
)
def test_module_build_registry_atexit_reaps_only_owner_process_children(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "build-child.pid"
    project_root = tmp_path / "project"
    build_temp_root = tmp_path / "build-temp"
    project_root.mkdir()
    repo_root = Path(__file__).resolve().parents[1]
    script = textwrap.dedent("""
        import os
        import sys
        import time
        from pathlib import Path

        sys.path.insert(0, str(Path.cwd() / "src"))
        import paradev.desktop.builds as builds

        marker = Path(sys.argv[1])
        project_root = Path(sys.argv[2])
        build_temp_root = Path(sys.argv[3])
        build_temp_root.mkdir()
        builds._desktop_build_output_path = lambda name: build_temp_root / name
        child_script = (
            "from pathlib import Path; import os, sys, time; "
            "Path(sys.argv[1]).write_text(str(os.getpid()), encoding='utf-8'); "
            "time.sleep(60)"
        )

        def build_command(project_root, **kwargs):
            return [sys.executable, "-c", child_script, str(marker)]

        builds.desktop_project_build_command = build_command
        started = builds.desktop_start_build(str(project_root))
        deadline = time.monotonic() + 5
        while not marker.is_file() and time.monotonic() < deadline:
            time.sleep(0.01)
        if not marker.is_file():
            raise RuntimeError("build child did not publish its pid")

        for access_registry in (False, True):
            fork_pid = os.fork()
            if fork_pid == 0:
                if access_registry and builds.desktop_build_runs()["runs"]:
                    raise SystemExit(31)
                raise SystemExit(0)
            _, wait_status = os.waitpid(fork_pid, 0)
            if os.waitstatus_to_exitcode(wait_status) != 0:
                raise RuntimeError("forked child observed inherited build registry state")
            if builds.desktop_build_status(str(started["runId"]))["status"] != "running":
                raise RuntimeError("forked child signalled the parent's build process group")
        """)

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(marker),
            str(project_root),
            str(build_temp_root),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    child_pid = int(marker.read_text(encoding="utf-8"))
    try:
        os.kill(child_pid, 0)
    except ProcessLookupError:
        pass
    else:
        os.kill(child_pid, signal.SIGKILL)
        pytest.fail("module build-registry atexit cleanup left its child running")
    assert list(build_temp_root.iterdir()) == []


def test_desktop_build_registry_retains_ownership_when_interrupt_cleanup_fails(
    monkeypatch,
) -> None:
    import paradev.desktop.builds as desktop_builds

    class UnreapableBuildProcess(FakeBuildProcess):
        def terminate(self) -> None:
            self.terminated = True

        def kill(self) -> None:
            self.killed = True

        def wait(self, timeout: float | None = None) -> int:
            raise subprocess.TimeoutExpired("paradev build", timeout)

    process = UnreapableBuildProcess()
    monkeypatch.setattr(desktop_builds.subprocess, "Popen", lambda *args, **kwargs: process)
    registry = DesktopBuildRegistry()
    started = registry.start("/tmp/PIHC3")

    with pytest.raises(subprocess.TimeoutExpired):
        registry.interrupt(str(started["runId"]))

    assert process.terminated is True
    assert process.killed is True
    assert registry.runs()["runs"][0]["runId"] == started["runId"]
    process.returncode = -9
    assert registry.status(str(started["runId"]))["status"] == "failed"
    registry.close()


def test_desktop_build_registry_close_stops_healthy_children_after_one_poll_failure(monkeypatch, tmp_path: Path) -> None:
    import paradev.desktop.builds as desktop_builds

    class PollFailureProcess(FakeBuildProcess):
        def poll(self) -> int | None:
            raise OSError("poll failed")

        def terminate(self) -> None:
            self.terminated = True

        def kill(self) -> None:
            self.killed = True

    healthy = FakeBuildProcess()
    broken = PollFailureProcess()
    processes = [healthy, broken]
    monkeypatch.setattr(desktop_builds.subprocess, "Popen", lambda *args, **kwargs: processes.pop(0))
    monkeypatch.setattr(desktop_builds, "_desktop_build_output_path", lambda name: tmp_path / name)
    monkeypatch.setattr(desktop_builds, "_BUILD_TERMINATION_GRACE_SECONDS", 0.0)
    registry = DesktopBuildRegistry()
    healthy_run = registry.start("/tmp/Healthy")
    broken_run = registry.start("/tmp/Broken")

    with pytest.raises(RuntimeError, match=str(broken_run["runId"])):
        registry.close()

    assert registry._closed is True
    assert healthy.terminated is True
    assert broken.terminated is True
    assert broken.killed is True
    assert registry._finished[str(healthy_run["runId"])]["status"] == "interrupted"
    assert str(broken_run["runId"]) in registry._processes


def test_desktop_build_runs_facade_exposes_project_filtered_history() -> None:
    payload = desktop_build_runs("/definitely/not/a/started/project")

    assert payload == {"schema": BUILD_RUNS_SCHEMA, "runs": []}


def test_desktop_hoi4_launch_payload_matches_desktop_command_rules(
    tmp_path: Path,
) -> None:
    steam_target = "steam://run/394360"
    assert desktop_run_hoi4(
        game_root="/Games/Hearts of Iron IV",
        mode="steam",
        launch=False,
        platform="macos",
    ) == {
        "schema": "paradev.desktop.game-launch.v1",
        "game": "hoi4",
        "status": "started",
        "mode": "steam",
        "gameRoot": steam_target,
        "command": ["open", steam_target],
    }
    assert desktop_hoi4_launch_command(mode="steam", platform="windows") == [
        "cmd",
        "/C",
        "start",
        "",
        steam_target,
    ]

    game_root = tmp_path / "Hearts of Iron IV"
    game_root.mkdir()
    executable = game_root / "hoi4"
    executable.write_text("#!/bin/sh\n", encoding="utf-8")
    executable.chmod(0o755)
    assert desktop_run_hoi4(game_root=game_root, mode="local", launch=False, platform="linux") == {
        "schema": "paradev.desktop.game-launch.v1",
        "game": "hoi4",
        "status": "started",
        "mode": "local",
        "gameRoot": str(executable),
        "command": [str(executable)],
    }


def test_desktop_hoi4_launch_uses_configured_default_mode(tmp_path: Path, cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.hoi4.launch_mode", default=None)
    game_root = tmp_path / "Hearts of Iron IV"
    game_root.mkdir()
    executable = game_root / "hoi4"
    executable.write_text("#!/bin/sh\n", encoding="utf-8")
    executable.chmod(0o755)

    try:
        CM_PARADEV.set("paradev.hoi4.launch_mode", "local")

        assert desktop_run_hoi4(game_root=game_root, launch=False, platform="linux")["mode"] == "local"
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.hoi4.launch_mode")
        else:
            CM_PARADEV.set("paradev.hoi4.launch_mode", previous)


def test_desktop_hoi4_launch_uses_configured_game_root(tmp_path: Path, cm_paradev_lock) -> None:
    previous_mode = CM_PARADEV.get("paradev.hoi4.launch_mode", default=None)
    previous_root = CM_PARADEV.get("paradev.hoi4.game_root", default=None)
    game_root = tmp_path / "Hearts of Iron IV"
    game_root.mkdir()
    executable = game_root / "hoi4"
    executable.write_text("#!/bin/sh\n", encoding="utf-8")
    executable.chmod(0o755)

    try:
        CM_PARADEV.set("paradev.hoi4.launch_mode", "local")
        CM_PARADEV.set("paradev.hoi4.game_root", f"  {game_root}  ")

        assert desktop_run_hoi4(launch=False, platform="linux") == {
            "schema": "paradev.desktop.game-launch.v1",
            "game": "hoi4",
            "status": "started",
            "mode": "local",
            "gameRoot": str(executable),
            "command": [str(executable)],
        }
    finally:
        if previous_mode is None:
            CM_PARADEV.unset("paradev.hoi4.launch_mode")
        else:
            CM_PARADEV.set("paradev.hoi4.launch_mode", previous_mode)
        if previous_root is None:
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous_root)


def test_desktop_hoi4_local_launch_requires_an_existing_game_root(
    tmp_path: Path,
    cm_paradev_lock,
) -> None:
    previous_root = CM_PARADEV.get("paradev.hoi4.game_root", default=None)

    try:
        CM_PARADEV.unset("paradev.hoi4.game_root")

        with pytest.raises(
            ValueError,
            match=r"required for Local app launch mode.*Settings > Projects.*Steam launcher mode",
        ):
            desktop_hoi4_launch_command(mode="local", platform="windows")

        missing_root = tmp_path / "missing-hoi4"
        with pytest.raises(
            ValueError,
            match=r"does not exist: .*missing-hoi4.*Settings > Projects.*Steam launcher mode",
        ):
            desktop_hoi4_launch_command(
                mode="local",
                game_root=missing_root,
                platform="windows",
            )

        empty_root = tmp_path / "empty-hoi4"
        empty_root.mkdir()
        with pytest.raises(
            ValueError,
            match=r"not launchable on Windows.*Expected hoi4.exe.*Settings > Projects",
        ):
            desktop_hoi4_launch_command(
                mode="local",
                game_root=empty_root,
                platform="windows",
            )
    finally:
        if previous_root is None:
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous_root)


def test_desktop_hoi4_local_launch_resolves_platform_executables(
    tmp_path: Path,
) -> None:
    windows_root = tmp_path / "windows"
    windows_root.mkdir()
    windows_executable = windows_root / "hoi4.exe"
    windows_executable.write_bytes(b"MZ")

    linux_root = tmp_path / "linux"
    linux_root.mkdir()
    linux_executable = linux_root / "hoi4"
    linux_executable.write_text("#!/bin/sh\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"not launchable on Linux.*executable named hoi4"):
        desktop_hoi4_launch_command(mode="local", game_root=linux_root, platform="linux")
    linux_executable.chmod(0o755)

    macos_root = tmp_path / "macos"
    macos_executable = macos_root / "dowser.app" / "Contents" / "MacOS" / "dowser"
    macos_executable.parent.mkdir(parents=True)
    macos_executable.write_text("#!/bin/sh\n", encoding="utf-8")
    macos_executable.chmod(0o755)

    assert desktop_hoi4_launch_command(mode="local", game_root=windows_root, platform="windows") == [
        "cmd",
        "/C",
        "start",
        "",
        str(windows_executable),
    ]
    assert desktop_hoi4_launch_command(mode="local", game_root=linux_root, platform="linux") == [str(linux_executable)]
    assert desktop_hoi4_launch_command(mode="local", game_root=macos_root, platform="macos") == [
        "open",
        str(macos_root / "dowser.app"),
    ]


def test_desktop_hoi4_steam_launch_requires_an_available_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import paradev.desktop.shell as shell

    launched: list[list[str]] = []
    monkeypatch.setattr(
        shell,
        "_steam_launch_problem",
        lambda platform: "no steam:// URL handler is registered",
    )
    monkeypatch.setattr(shell, "cmd", lambda command, **kwargs: launched.append(list(command)))

    with pytest.raises(
        ValueError,
        match=r"Steam is not available.*no steam:// URL handler.*Local app launch mode.*Settings > Projects",
    ):
        desktop_run_hoi4(mode="steam", launch=True, platform="linux")

    assert launched == []

    monkeypatch.setattr(shell, "_steam_launch_problem", lambda platform: None)
    payload = desktop_run_hoi4(mode="steam", launch=True, platform="linux")

    assert payload["status"] == "started"
    assert launched == [["xdg-open", "steam://run/394360"]]


def test_desktop_hoi4_steam_availability_checks_platform_handlers(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import paradev.desktop.shell as shell

    monkeypatch.setattr(
        shell.shutil,
        "which",
        lambda command: (f"/usr/bin/{command}" if command in {"open", "xdg-open", "xdg-mime"} else None),
    )
    monkeypatch.setattr(shell, "cmd", lambda command, **kwargs: False)
    assert shell._steam_launch_problem("macos") == "the Steam application is not registered with macOS"

    monkeypatch.setattr(
        shell,
        "cmd",
        lambda command, **kwargs: {"ok": True, "out": "steam.desktop"},
    )
    assert shell._steam_launch_problem("linux") is None

    steam_executable = tmp_path / "steam.exe"
    steam_executable.write_bytes(b"MZ")

    class FakeRegistryKey:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

    fake_winreg = SimpleNamespace(
        HKEY_CLASSES_ROOT=object(),
        OpenKey=lambda root, name: FakeRegistryKey(),
        QueryValueEx=lambda key, name: (f'"{steam_executable}" "%1"', None),
    )
    monkeypatch.setitem(sys.modules, "winreg", fake_winreg)

    assert shell._steam_launch_problem("windows") is None


def test_desktop_hoi4_project_launch_requires_current_generated_descriptors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mod_root = tmp_path / "hoi4-mod"
    project_root = tmp_path / "PIHC3"
    (project_root / "src").mkdir(parents=True)
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: PIHC3",
                "title: The Pony In The High Castle",
                "game: hoi4",
                "source_roots: [src]",
                "build_root: .paradev/.cache/build",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("PARADEV_HOI4_MOD_ROOT", str(mod_root))

    assert desktop_hoi4_launch_readiness(project_root)["code"] == "generated_descriptor_missing"
    with pytest.raises(ValueError, match=r"generated descriptor is missing.*full or cached build"):
        desktop_run_hoi4(project_root=project_root, mode="steam", launch=False, platform="windows")

    output_root = mod_root / "PIHC3"
    output_root.mkdir(parents=True)
    (output_root / "descriptor.mod").write_text('name="PIHC3"\n', encoding="utf-8")

    assert desktop_hoi4_launch_readiness(project_root)["code"] == "launcher_descriptor_missing"
    with pytest.raises(ValueError, match=r"not registered with the HOI4 launcher.*full or cached build"):
        desktop_run_hoi4(project_root=project_root, mode="steam", launch=False, platform="windows")

    launcher_descriptor = mod_root / "PIHC3.mod"
    launcher_descriptor.write_text(f'path="{output_root}"\n', encoding="utf-8")

    assert desktop_hoi4_launch_readiness(project_root)["code"] == "publication_incomplete"
    with pytest.raises(ValueError, match=r"complete whole-project publication.*Clean/Full or Cached"):
        desktop_run_hoi4(project_root=project_root, mode="steam", launch=False, platform="windows")

    launcher_descriptor.unlink()
    (output_root / "descriptor.mod").unlink()
    output_root.rmdir()
    Project.load(project_root).build(emit_artifacts=True, emit_manifests=True)

    payload = desktop_run_hoi4(project_root=project_root, mode="steam", launch=False, platform="windows")
    readiness = desktop_hoi4_launch_readiness(project_root)

    assert payload["status"] == "started"
    assert payload["gameRoot"] == "steam://run/394360"
    assert readiness["code"] == "ready"
    assert readiness["ready"] is True

    launcher_descriptor.write_text(f'path="{tmp_path / "stale-output"}"\n', encoding="utf-8")
    mismatch = desktop_hoi4_launch_readiness(project_root)
    assert mismatch["code"] == "launcher_path_mismatch"
    assert mismatch["ready"] is False
    with pytest.raises(ValueError, match=r"not the current output folder.*Rebuild"):
        desktop_run_hoi4(project_root=project_root, mode="steam", launch=False, platform="windows")


def test_desktop_hoi4_project_launch_rejects_a_partial_only_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mod_root = tmp_path / "hoi4-mod"
    project_root = tmp_path / "PIHC3"
    module_root = project_root / "src/modules/focus/GER_sample"
    module_root.mkdir(parents=True)
    (module_root / "def.txt").write_text("focus = { id = GER_sample }\n", encoding="utf-8")
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: PIHC3",
                "title: The Pony In The High Castle",
                "game: hoi4",
                "source_roots: [src]",
                "build_root: .paradev/.cache/build",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("PARADEV_HOI4_MOD_ROOT", str(mod_root))
    project = Project.load(project_root)
    project.build(family="focus", emit_artifacts=True, emit_manifests=True)

    partial_readiness = desktop_hoi4_launch_readiness(project_root)
    assert partial_readiness["code"] == "whole_project_baseline_missing"
    assert partial_readiness["ready"] is False
    with pytest.raises(ValueError, match=r"complete whole-project publication.*Clean/Full or Cached"):
        desktop_run_hoi4(project_root=project_root, mode="steam", launch=False, platform="windows")

    project.build(emit_artifacts=True, emit_manifests=True)

    payload = desktop_run_hoi4(project_root=project_root, mode="steam", launch=False, platform="windows")

    assert payload["status"] == "started"


def test_desktop_hoi4_launch_readiness_rejects_stale_publication_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mod_root = tmp_path / "hoi4-mod"
    project_root = tmp_path / "PIHC3"
    (project_root / "src").mkdir(parents=True)
    (project_root / "paradev.yaml").write_text(
        "\n".join(
            [
                "project_id: PIHC3",
                "title: The Pony In The High Castle",
                "game: hoi4",
                "source_roots: [src]",
                "build_root: .paradev/.cache/build",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("PARADEV_HOI4_MOD_ROOT", str(mod_root))
    project = Project.load(project_root)
    project.build(emit_artifacts=True, emit_manifests=True)
    descriptor_text = (project.output_root / "descriptor.mod").read_text(encoding="utf-8")

    stale_output = tmp_path / "stale-output"
    project.output_root.rename(stale_output)
    project.output_root.mkdir()
    (project.output_root / "descriptor.mod").write_text(descriptor_text, encoding="utf-8")

    readiness = desktop_hoi4_launch_readiness(project_root)

    assert readiness["code"] == "publication_incomplete"
    assert readiness["ready"] is False
    assert "current build and output folders" in str(readiness["reason"])


def test_desktop_open_path_command_matches_desktop_targets(tmp_path: Path) -> None:
    path = str(tmp_path)

    assert desktop_open_path_command(path, "finder", platform="macos") == ["open", path]
    assert desktop_open_path_command(path, "sublimeText", platform="macos") == [
        "open",
        "-a",
        "Sublime Text",
        path,
    ]
    assert desktop_open_path_command(path, "terminal", platform="macos") == [
        "open",
        "-a",
        "Terminal",
        path,
    ]
    assert desktop_open_path_command(path, "iterm2", platform="macos") == [
        "open",
        "-a",
        "iTerm",
        path,
    ]
    assert desktop_open_path_command(path, "vscode", platform="linux") == [
        "code",
        "-r",
        path,
    ]
    assert desktop_open_path_command(path, "cursor", platform="linux") == [
        "cursor",
        "-r",
        path,
    ]
    assert desktop_open_path_command(path, "explorer", platform="windows") == [
        "explorer",
        path,
    ]
    assert desktop_open_path_command(path, "cmd", platform="windows") == [
        "cmd",
        "/C",
        "start",
        "",
        "/D",
        path,
        "cmd",
    ]
    assert desktop_open_path(path, "vscode", launch=False, platform="linux") == [
        "code",
        "-r",
        path,
    ]

    with pytest.raises(ValueError, match="Command Prompt opener is only available on Windows"):
        desktop_open_path_command(path, "cmd", platform="macos")
    with pytest.raises(ValueError, match="Open path does not exist"):
        desktop_open_path_command(str(tmp_path / "missing"), "vscode", platform="linux")


def test_desktop_open_path_default_target_matches_gui_platform_defaults(
    tmp_path: Path,
) -> None:
    path = str(tmp_path)

    assert desktop_open_path_command(path, None, platform="macos") == ["open", path]
    assert desktop_open_path_command(path, "default", platform="macos") == [
        "open",
        path,
    ]
    assert desktop_open_path_command(path, None, platform="windows") == [
        "explorer",
        path,
    ]
    assert desktop_open_path_command(path, "default", platform="windows") == [
        "explorer",
        path,
    ]
    assert desktop_open_path_command(path, None, platform="linux") == [
        "cursor",
        "-r",
        path,
    ]
    assert desktop_open_path_command(path, "default", platform="linux") == [
        "cursor",
        "-r",
        path,
    ]
    assert desktop_open_path_command(path, None, platform="dragonfly") == [
        "cursor",
        "-r",
        path,
    ]
    assert desktop_open_path_command(path, "default", platform="dragonfly") == [
        "cursor",
        "-r",
        path,
    ]


def test_desktop_open_path_targets_catalog_matches_gui_platform_contract() -> None:
    assert hasattr(desktop, "desktop_open_path_targets")

    catalog = desktop.desktop_open_path_targets(platform="linux")

    assert catalog == {
        "schema": "paradev.desktop.open-path-targets.v1",
        "platform": "linux",
        "defaultTarget": "cursor",
        "availableTargetIds": ["cursor", "vscode", "sublimeText"],
        "targets": [
            {"id": "finder", "labelKey": "openTarget.finder", "platforms": ["macos"]},
            {
                "id": "explorer",
                "labelKey": "openTarget.explorer",
                "platforms": ["windows"],
            },
            {
                "id": "cursor",
                "labelKey": "openTarget.cursor",
                "platforms": ["macos", "windows", "linux", "unknown"],
            },
            {
                "id": "vscode",
                "labelKey": "openTarget.vscode",
                "platforms": ["macos", "windows", "linux", "unknown"],
            },
            {
                "id": "sublimeText",
                "labelKey": "openTarget.sublimeText",
                "platforms": ["macos", "windows", "linux", "unknown"],
            },
            {
                "id": "terminal",
                "labelKey": "openTarget.terminal",
                "platforms": ["macos"],
            },
            {"id": "iterm2", "labelKey": "openTarget.iterm2", "platforms": ["macos"]},
            {"id": "cmd", "labelKey": "openTarget.cmd", "platforms": ["windows"]},
            {
                "id": "powershell",
                "labelKey": "openTarget.powershell",
                "platforms": ["windows"],
            },
        ],
    }
    assert desktop.desktop_open_path_targets(platform="dragonfly")["platform"] == "unknown"
    assert desktop.desktop_open_path_targets(platform="dragonfly")["defaultTarget"] == "cursor"


def test_desktop_path_status_describes_existing_and_missing_paths(
    tmp_path: Path,
) -> None:
    source = tmp_path / "common" / "ideas" / "sample.txt"
    source.parent.mkdir(parents=True)
    source.write_text("ideas = {}\n", encoding="utf-8")
    missing = tmp_path / "build" / "mod"

    root_status = desktop_path_status(f"  {tmp_path}  ")
    file_status = desktop_path_status(source)
    missing_status = desktop_path_status(missing)

    assert root_status == {
        "schema": "paradev.desktop.path-status.v1",
        "inputPath": str(tmp_path),
        "path": str(tmp_path.resolve()),
        "exists": True,
        "kind": "directory",
        "readable": True,
        "openable": True,
    }
    assert file_status["path"] == str(source.resolve())
    assert file_status["exists"] is True
    assert file_status["kind"] == "file"
    assert file_status["readable"] is True
    assert file_status["openable"] is True
    assert missing_status == {
        "schema": "paradev.desktop.path-status.v1",
        "inputPath": str(missing),
        "path": str(missing.resolve()),
        "exists": False,
        "kind": "missing",
        "readable": False,
        "openable": False,
    }

    with pytest.raises(ValueError, match="Path status path is required"):
        desktop_path_status("  ")


def test_desktop_source_path_rejects_files_outside_project(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    inside = project_root / "src" / "idea.txt"
    inside.parent.mkdir()
    inside.write_text("idea = {}", encoding="utf-8")
    outside = tmp_path / "outside.txt"
    outside.write_text("nope", encoding="utf-8")

    assert desktop_source_path(project_root, "src/idea.txt") == inside.resolve()

    try:
        desktop_source_path(project_root, outside)
    except ValueError as error:
        assert "outside the active project root" in str(error)
    else:  # pragma: no cover - defensive assertion shape
        raise AssertionError("outside source path should be rejected")


def test_desktop_read_text_and_binary_source_payloads(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    Project.create(project_root, title="Desktop Source Project")
    text_source = project_root / "src" / "idea.txt"
    binary_source = project_root / "src" / "icon.png"
    text_source.write_text("idea = {}\n", encoding="utf-8")
    binary_source.write_bytes(b"\x89PNG\r\n")

    assert desktop_read_text_source(project_root, "src/idea.txt") == "idea = {}\n"
    payload = desktop_read_binary_source(project_root, "src/icon.png")

    assert payload == {
        "schema": "paradev.desktop.binary-source.v1",
        "path": str(binary_source.resolve()),
        "mimeType": "image/png",
        "bytes": [137, 80, 78, 71, 13, 10],
    }


def test_desktop_thumbnail_cache_matches_desktop_path_and_payload(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    cache_path = desktop_thumbnail_cache_path(project_root, "C01/icon.png")

    assert cache_path == project_root.resolve() / ".paradev" / ".cache" / "instance-thumbnails" / "d4e7ba7e62f6976a.png"
    assert desktop_read_thumbnail_cache(project_root, "C01/icon.png") is None

    payload = desktop_write_thumbnail_cache(project_root, "C01/icon.png", _THUMBNAIL_PNG)

    assert payload["path"] == str(cache_path)
    assert payload["mimeType"] == "image/png"
    assert payload["bytes"] == list(_THUMBNAIL_PNG)
    assert desktop_read_thumbnail_cache(project_root, "C01/icon.png") == payload


def test_desktop_thumbnail_cache_miss_does_not_hide_invalid_entries(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()

    with pytest.raises(ValueError, match="thumbnail cache key cannot be empty"):
        desktop_read_thumbnail_cache(project_root, " ")
    with pytest.raises(ValueError, match="Cannot resolve project root"):
        desktop_read_thumbnail_cache(tmp_path / "missing", "icon.png")
    file_root = tmp_path / "file-root"
    file_root.write_text("not a project", encoding="utf-8")
    with pytest.raises(ValueError, match="project root is not a directory"):
        desktop_read_thumbnail_cache(file_root, "icon.png")

    directory_entry = desktop_thumbnail_cache_path(project_root, "directory")
    directory_entry.mkdir(parents=True)
    with pytest.raises(ValueError, match="Thumbnail cache path is not a file"):
        desktop_read_thumbnail_cache(project_root, "directory")

    corrupt_entry = desktop_thumbnail_cache_path(project_root, "corrupt")
    corrupt_png = bytearray(_THUMBNAIL_PNG)
    corrupt_png[45] ^= 1
    corrupt_entry.write_bytes(corrupt_png)
    assert desktop_read_thumbnail_cache(project_root, "corrupt") is None
    assert not corrupt_entry.exists()

    monkeypatch.setattr(desktop_local, "_thumbnail_cache_max_bytes", lambda: len(_THUMBNAIL_PNG))
    oversized_entry = desktop_thumbnail_cache_path(project_root, "oversized")
    oversized_entry.write_bytes(_THUMBNAIL_PNG + b"x")
    with pytest.raises(ValueError, match=f"larger than {len(_THUMBNAIL_PNG)} bytes"):
        desktop_read_thumbnail_cache(project_root, "oversized")


def test_desktop_thumbnail_cache_rejects_invalid_png_before_mutation(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    rejected_path = desktop_thumbnail_cache_path(project_root, "invalid.png")

    with pytest.raises(ValueError, match="not a valid PNG"):
        desktop_write_thumbnail_cache(project_root, "invalid.png", b"not a png")

    assert not rejected_path.exists()
    assert not rejected_path.parent.exists()

    cache_key = "C01/icon.png"
    payload = desktop_write_thumbnail_cache(project_root, cache_key, _THUMBNAIL_PNG)
    cache_path = Path(str(payload["path"]))

    with pytest.raises(ValueError, match="not a valid PNG"):
        desktop_write_thumbnail_cache(project_root, cache_key, b"not a png")

    assert cache_path.read_bytes() == _THUMBNAIL_PNG
    assert desktop_read_thumbnail_cache(project_root, cache_key) == payload


def test_desktop_thumbnail_cache_surfaces_stale_entry_cleanup_failures(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    cache_path = desktop_thumbnail_cache_path(project_root, "stale")
    cache_path.parent.mkdir(parents=True)
    cache_path.write_bytes(b"not a png")
    original_unlink = Path.unlink

    def deny_stale_unlink(path: Path, *args, **kwargs) -> None:
        if path == cache_path:
            raise PermissionError("cache is read-only")
        original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", deny_stale_unlink)

    with pytest.raises(PermissionError, match="cache is read-only"):
        desktop_read_thumbnail_cache(project_root, "stale")


def test_desktop_thumbnail_cache_uses_configured_size_limit(tmp_path: Path, cm_paradev_lock) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    previous = CM_PARADEV.get("paradev.desktop.thumbnail_cache.max_kb", default=None)

    try:
        CM_PARADEV.set("paradev.desktop.thumbnail_cache.max_kb", 1)

        payload = desktop_write_thumbnail_cache(project_root, "C01/icon.png", _THUMBNAIL_PNG)

        assert payload["bytes"] == list(_THUMBNAIL_PNG)
        with pytest.raises(ValueError, match="larger than 1024 bytes"):
            desktop_write_thumbnail_cache(project_root, "C01/large-icon.png", b"x" * 1025)
    finally:
        if previous is None or isinstance(previous, MappingProxyType):
            CM_PARADEV.unset("paradev.desktop.thumbnail_cache.max_kb")
        else:
            CM_PARADEV.set("paradev.desktop.thumbnail_cache.max_kb", previous)


def test_desktop_browser_cache_validates_project_root(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    other_root = tmp_path / "other"
    project_root.mkdir()
    other_root.mkdir()
    payload = {
        "schema": "paradev.sdk.project-browser.v1",
        "project_id": "demo",
        "root": str(project_root),
        "filters": {},
        "items": [],
    }

    assert desktop_browser_cache_path(project_root) == project_root.resolve() / ".paradev" / ".cache" / "desktop" / "project-browser" / "browser.json"
    assert desktop_write_browser_cache(project_root, payload) == payload
    assert desktop.read_project_browser_cache(project_root) == payload
    assert desktop.read_project_browser_cache(other_root) is None

    scoped_payload = {**payload, "filters": {"family": "entity"}}
    with pytest.raises(ValueError, match="must be unfiltered"):
        desktop_write_browser_cache(project_root, scoped_payload)

    cache_path = desktop_browser_cache_path(project_root)
    dump_json(scoped_payload, str(cache_path))

    assert desktop.read_project_browser_cache(project_root) is None
    assert not cache_path.exists()


def test_desktop_app_config_uses_paradev_config_manager(tmp_path: Path, monkeypatch, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path))
    previous = CM_PARADEV.get("paradev.desktop.gui", default=None)
    previous_payload = plain_json(previous) if previous is not None else None
    payload = {
        "schema": "paradev.desktop.app-settings.v1",
        "theme": "dark",
        "configPage": {
            "build": {"parallelism": 2},
            "moduleDefaults": [{"familyId": "idea", "value": 10}],
        },
    }

    try:
        desktop_write_app_config(payload)

        config = desktop_read_app_config()
        assert config == payload
        assert isinstance(config, dict)
        assert isinstance(config["configPage"], dict)
        assert isinstance(config["configPage"]["moduleDefaults"], list)
        assert plain_json(CM_PARADEV.get("paradev.desktop.gui")) == payload
        with pytest.raises(ValueError, match="non-finite float"):
            desktop_write_app_config({"schema": "paradev.desktop.app-settings.v1", "scale": float("inf")})
    finally:
        if previous_payload is None:
            CM_PARADEV.unset("paradev.desktop.gui")
        else:
            CM_PARADEV.set("paradev.desktop.gui", previous_payload)


def test_desktop_config_value_round_trips_build_parallelism(tmp_path: Path, monkeypatch, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path))
    previous = CM_PARADEV.get("paradev.build.parallelism", default=None)

    try:
        payload = desktop_write_config_value("paradev.build.parallelism", "4")

        assert payload == {
            "schema": "paradev.desktop.config-value.v1",
            "key": "paradev.build.parallelism",
            "value": 4,
        }
        assert desktop_read_config_value("paradev.build.parallelism") == payload
        assert CM_PARADEV.get("paradev.build.parallelism") == 4
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.build.parallelism")
        else:
            CM_PARADEV.set("paradev.build.parallelism", previous)


def test_desktop_config_value_round_trips_strict_metadata(tmp_path: Path, monkeypatch, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path / "config-root"))
    previous = CM_PARADEV.get("paradev.build.strict_metadata", default=None)
    try:
        CM_PARADEV.unset("paradev.build.strict_metadata")

        assert desktop_read_config_value("paradev.build.strict_metadata") == {
            "schema": "paradev.desktop.config-value.v1",
            "key": "paradev.build.strict_metadata",
            "value": False,
        }
        assert desktop_write_config_value("paradev.build.strict_metadata", True) == {
            "schema": "paradev.desktop.config-value.v1",
            "key": "paradev.build.strict_metadata",
            "value": True,
        }
        assert desktop_read_config_value("paradev.build.strict_metadata")["value"] is True
        assert desktop_write_config_value("paradev.build.strict_metadata", False)["value"] is False

        with pytest.raises(ValueError, match="paradev.build.strict_metadata must be a boolean"):
            desktop_write_config_value("paradev.build.strict_metadata", "true")
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.build.strict_metadata")
        else:
            CM_PARADEV.set("paradev.build.strict_metadata", previous)


def test_desktop_config_value_round_trips_thumbnail_cache_limit(tmp_path: Path, monkeypatch, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path))
    previous = CM_PARADEV.get("paradev.desktop.thumbnail_cache.max_kb", default=None)

    try:
        payload = desktop_write_config_value("paradev.desktop.thumbnail_cache.max_kb", "512")

        assert payload == {
            "schema": "paradev.desktop.config-value.v1",
            "key": "paradev.desktop.thumbnail_cache.max_kb",
            "value": 512,
        }
        assert desktop_read_config_value("paradev.desktop.thumbnail_cache.max_kb") == payload
        assert CM_PARADEV.get("paradev.desktop.thumbnail_cache.max_kb") == 512
        with pytest.raises(ValueError, match="paradev.desktop.thumbnail_cache.max_kb"):
            desktop_write_config_value("paradev.desktop.thumbnail_cache.max_kb", True)
    finally:
        if previous is None or isinstance(previous, MappingProxyType):
            CM_PARADEV.unset("paradev.desktop.thumbnail_cache.max_kb")
        else:
            CM_PARADEV.set("paradev.desktop.thumbnail_cache.max_kb", previous)


def test_desktop_config_defaults_match_package_defaults() -> None:
    assert dict(desktop_local.DESKTOP_CONFIG_DEFAULTS) == {
        "paradev.project.name": DEFAULT_CONFIG["paradev"]["project"]["name"],
        "paradev.cli.output": DEFAULT_CONFIG["paradev"]["cli"]["output"],
        "paradev.build.parallelism": DEFAULT_CONFIG["paradev"]["build"]["parallelism"],
        "paradev.build.strict_metadata": DEFAULT_CONFIG["paradev"]["build"]["strict_metadata"],
        "paradev.desktop.thumbnail_cache.max_kb": DEFAULT_CONFIG["paradev"]["desktop"]["thumbnail_cache"]["max_kb"],
        "paradev.hoi4.launch_mode": DEFAULT_CONFIG["paradev"]["hoi4"]["launch_mode"],
        "paradev.hoi4.game_root": DEFAULT_CONFIG["paradev"]["hoi4"]["game_root"],
        "paradev.ai.preset": DEFAULT_CONFIG["paradev"]["ai"]["preset"],
        "paradev.ai.provider": DEFAULT_CONFIG["paradev"]["ai"]["provider"],
        "paradev.ai.gateway": DEFAULT_CONFIG["paradev"]["ai"]["gateway"],
        "paradev.ai.model": DEFAULT_CONFIG["paradev"]["ai"]["model"],
        "paradev.ai.key_env": DEFAULT_CONFIG["paradev"]["ai"]["key_env"],
        "paradev.ai.base_url": DEFAULT_CONFIG["paradev"]["ai"]["base_url"],
        "paradev.ai.chat.default_role": DEFAULT_CONFIG["paradev"]["ai"]["chat"]["default_role"],
    }


def test_desktop_config_defaults_are_derived_from_exposed_key_list() -> None:
    assert DESKTOP_CONFIG_KEYS == desktop_local.DESKTOP_CONFIG_KEYS
    assert tuple(desktop_local.DESKTOP_CONFIG_KEYS) == tuple(desktop_local.DESKTOP_CONFIG_DEFAULTS)
    assert dict(desktop_local.DESKTOP_CONFIG_DEFAULTS) == {key: dget(DEFAULT_CONFIG, key) for key in desktop_local.DESKTOP_CONFIG_KEYS}


def test_desktop_config_rows_define_defaults_and_ordered_choices() -> None:
    rows = desktop_local.DESKTOP_CONFIG_ROWS
    row_by_key = {str(row["key"]): row for row in rows}

    assert tuple(str(row["key"]) for row in rows) == desktop_local.DESKTOP_CONFIG_KEYS
    assert {key: row["default"] for key, row in row_by_key.items()} == dict(desktop_local.DESKTOP_CONFIG_DEFAULTS)
    assert row_by_key["paradev.cli.output"]["choices"] == ["yaml", "json"]
    assert row_by_key["paradev.hoi4.launch_mode"]["choices"] == ["steam", "local"]
    assert row_by_key["paradev.ai.preset"]["choices"] == [
        "system",
        "chat",
        "reason",
        "coder",
    ]
    assert row_by_key["paradev.build.parallelism"]["minimum"] == 1
    assert row_by_key["paradev.desktop.thumbnail_cache.max_kb"]["minimum"] == 1
    assert "choices" not in row_by_key["paradev.ai.chat.default_role"]


def test_desktop_config_rows_exposes_detached_sdk_metadata() -> None:
    rows = desktop_config_rows()
    row_by_key = {str(row["key"]): row for row in rows}

    assert rows == [dict(row) for row in desktop_local.DESKTOP_CONFIG_ROWS]
    assert tuple(str(row["key"]) for row in rows) == DESKTOP_CONFIG_KEYS
    assert row_by_key["paradev.cli.output"]["choices"] == ["yaml", "json"]

    rows[1]["default"] = "xml"
    row_by_key["paradev.cli.output"]["choices"].append("xml")

    fresh_row_by_key = {str(row["key"]): row for row in desktop_config_rows()}
    assert fresh_row_by_key["paradev.cli.output"]["default"] == DEFAULT_CONFIG["paradev"]["cli"]["output"]
    assert fresh_row_by_key["paradev.cli.output"]["choices"] == ["yaml", "json"]


def test_desktop_typescript_matches_generated_file() -> None:
    assert load_txt("apps/desktop/src/generated/desktopContract.ts") == render_desktop_typescript()


def test_desktop_typescript_contract_uses_general_renderer_and_artifact() -> None:
    assert hasattr(desktop, "render_desktop_typescript")
    assert not hasattr(desktop, "render_desktop_config_keys_typescript")

    source = desktop.render_desktop_typescript()

    assert load_txt("apps/desktop/src/generated/desktopContract.ts") == source
    assert not Path("apps/desktop/src/generated/desktopConfigKeys.ts").exists()
    assert "export const PARADEV_DESKTOP_CONFIG_ROWS = " in source
    assert "export const PARADEV_DESKTOP_CONFIG_DEFAULTS = " in source
    assert '"valueType": "choice"' in source
    assert '"choices": [' in source


def test_desktop_typescript_contract_exports_open_path_catalog() -> None:
    source = render_desktop_typescript()

    assert load_txt("apps/desktop/src/generated/desktopContract.ts") == source
    assert "export const PARADEV_DESKTOP_OPEN_PATH_TARGETS = " in source
    assert "export const PARADEV_DESKTOP_OPEN_PATH_DEFAULT_TARGETS = " in source
    assert 'id: "cursor"' in source
    assert '"linux": "cursor"' in source


def test_desktop_typescript_contract_exports_ai_chat_profile_catalog() -> None:
    source = render_desktop_typescript()

    assert load_txt("apps/desktop/src/generated/desktopContract.ts") == source
    assert "export const PARADEV_DESKTOP_AI_CHAT_SOURCE_KINDS = " in source
    assert "export const PARADEV_DESKTOP_AI_CHAT_SOURCE_KIND_ROWS = " in source
    assert "export const PARADEV_DESKTOP_AI_CHAT_PROFILE_SOURCE_KIND_FRONTEND_KINDS = " in source
    assert '"frontendKinds": [' in source
    assert '"workspace"' in source
    assert '"source"' in source
    assert "export const PARADEV_DESKTOP_AI_CHAT_PROFILES = " in source
    assert '"id": "create-module"' in source
    assert '"operationIds": [' in source
    assert '"operationCards": [' in source
    assert '"module.draft"' in source
    assert '"module.create_batch"' in source
    assert '"build.plan"' in source
    assert '"build.start"' in source
    assert '"Project.create_module_draft"' in source
    assert '"desktop_start_build"' in source
    assert '"promptKey": "chat.profile.createModule.prompt"' in source
    assert "Project.templates()" in source
    assert "Project.create_modules(..., write=False)" in source
    assert "Project.build(...)" in source
    assert "desktop_project_build_command(...)" in source


def test_desktop_config_value_normalizes_numeric_parallelism(tmp_path: Path, monkeypatch, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path))
    previous = CM_PARADEV.get("paradev.build.parallelism", default=None)

    try:
        assert desktop_write_config_value("paradev.build.parallelism", 2.6)["value"] == 3
        with pytest.raises(ValueError, match="positive integer"):
            desktop_write_config_value("paradev.build.parallelism", True)
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.build.parallelism")
        else:
            CM_PARADEV.set("paradev.build.parallelism", previous)


def test_desktop_config_value_round_trips_cli_output(tmp_path: Path, monkeypatch, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path))
    previous = CM_PARADEV.get("paradev.cli.output", default=None)

    try:
        payload = desktop_write_config_value("paradev.cli.output", "json")

        assert payload == {
            "schema": "paradev.desktop.config-value.v1",
            "key": "paradev.cli.output",
            "value": "json",
        }
        assert desktop_read_config_value("paradev.cli.output") == payload
        assert CM_PARADEV.get("paradev.cli.output") == "json"
        with pytest.raises(ValueError, match="paradev.cli.output"):
            desktop_write_config_value("paradev.cli.output", "toml")
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.cli.output")
        else:
            CM_PARADEV.set("paradev.cli.output", previous)


def test_desktop_config_value_round_trips_project_name(tmp_path: Path, monkeypatch, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path))
    previous = CM_PARADEV.get("paradev.project.name", default=None)

    try:
        payload = desktop_write_config_value("paradev.project.name", "  PIHC3 Workbench  ")

        assert payload == {
            "schema": "paradev.desktop.config-value.v1",
            "key": "paradev.project.name",
            "value": "PIHC3 Workbench",
        }
        assert desktop_read_config_value("paradev.project.name") == payload
        assert CM_PARADEV.get("paradev.project.name") == "PIHC3 Workbench"
        with pytest.raises(ValueError, match="paradev.project.name"):
            desktop_write_config_value("paradev.project.name", "")
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.project.name")
        else:
            CM_PARADEV.set("paradev.project.name", previous)


def test_desktop_config_value_round_trips_ai_route(tmp_path: Path, monkeypatch, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path))
    keys = {
        "paradev.ai.preset": "coder",
        "paradev.ai.provider": "deepseek",
        "paradev.ai.gateway": "openai",
        "paradev.ai.model": "deepseek-v4-flash",
        "paradev.ai.key_env": "DEEPSEEK_API_KEY",
        "paradev.ai.base_url": "https://api.deepseek.com/v1",
    }
    previous = {key: CM_PARADEV.get(key, default=None) for key in keys}

    try:
        for key, value in keys.items():
            payload = desktop_write_config_value(key, f"  {value}  ")

            assert payload == {
                "schema": "paradev.desktop.config-value.v1",
                "key": key,
                "value": value,
            }
            assert desktop_read_config_value(key) == payload
            assert CM_PARADEV.get(key) == value
        with pytest.raises(ValueError, match="paradev.ai.model"):
            desktop_write_config_value("paradev.ai.model", "")
        with pytest.raises(ValueError, match="paradev.ai.preset"):
            desktop_write_config_value("paradev.ai.preset", "creative")
        assert desktop_write_config_value("paradev.ai.base_url", "   ")["value"] == ""
    finally:
        for key, value in previous.items():
            if value is None:
                CM_PARADEV.unset(key)
            else:
                CM_PARADEV.set(key, value)


def test_desktop_llm_route_uses_configured_base_url(monkeypatch, cm_paradev_lock) -> None:
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": str(captured["kwargs"]["base_url"])}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **kwargs) -> None:
            captured["kwargs"] = kwargs

        def chat(self, _prompt: str) -> str:
            return "hb-ok"

    previous_base_url = CM_PARADEV.get("paradev.ai.base_url", default=None)
    previous_key_env = CM_PARADEV.get("paradev.ai.key_env", default=None)
    try:
        desktop_write_config_value("paradev.ai.base_url", " https://proxy.example/v1 ")
        CM_PARADEV.unset("paradev.ai.key_env")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "present")
        monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

        payload = desktop_local.desktop_test_llm_route("deepseek", "deepseek-v4-flash", "openai", preset="chat")

        assert payload["baseUrl"] == "https://proxy.example/v1"
        assert payload["preset"] == "chat"
        assert payload["status"] == "ready"
        assert captured["kwargs"] == {
            "api_key": "present",
            "base_url": "https://proxy.example/v1",
            "cache": False,
            "gateway": "openai",
            "max_tokens": 8,
            "model": "deepseek-v4-flash",
            "preset": "chat",
            "provider": "deepseek",
            "temperature": 0,
        }
    finally:
        _restore_cm_paradev_value("paradev.ai.base_url", previous_base_url)
        _restore_cm_paradev_value("paradev.ai.key_env", previous_key_env)


def test_desktop_config_value_round_trips_hoi4_launch_mode(tmp_path: Path, monkeypatch, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path))
    previous = CM_PARADEV.get("paradev.hoi4.launch_mode", default=None)

    try:
        payload = desktop_write_config_value("paradev.hoi4.launch_mode", " local ")

        assert payload == {
            "schema": "paradev.desktop.config-value.v1",
            "key": "paradev.hoi4.launch_mode",
            "value": "local",
        }
        assert desktop_read_config_value("paradev.hoi4.launch_mode") == payload
        assert CM_PARADEV.get("paradev.hoi4.launch_mode") == "local"
        assert desktop_write_config_value("paradev.hoi4.launch_mode", "steam")["value"] == "steam"
        with pytest.raises(ValueError, match="paradev.hoi4.launch_mode"):
            desktop_write_config_value("paradev.hoi4.launch_mode", "baseGame")
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.hoi4.launch_mode")
        else:
            CM_PARADEV.set("paradev.hoi4.launch_mode", previous)


def test_desktop_config_value_round_trips_hoi4_game_root(tmp_path: Path, monkeypatch, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path))
    previous = CM_PARADEV.get("paradev.hoi4.game_root", default=None)

    try:
        payload = desktop_write_config_value("paradev.hoi4.game_root", "  /Games/Hearts of Iron IV  ")

        assert payload == {
            "schema": "paradev.desktop.config-value.v1",
            "key": "paradev.hoi4.game_root",
            "value": "/Games/Hearts of Iron IV",
        }
        assert desktop_read_config_value("paradev.hoi4.game_root") == payload
        assert CM_PARADEV.get("paradev.hoi4.game_root") == "/Games/Hearts of Iron IV"
        assert desktop_write_config_value("paradev.hoi4.game_root", "   ")["value"] == ""
        with pytest.raises(ValueError, match="paradev.hoi4.game_root"):
            desktop_write_config_value("paradev.hoi4.game_root", 394360)
    finally:
        if previous is None:
            CM_PARADEV.unset("paradev.hoi4.game_root")
        else:
            CM_PARADEV.set("paradev.hoi4.game_root", previous)


def test_desktop_config_value_rejects_unsupported_keys() -> None:
    with pytest.raises(ValueError, match="Unsupported desktop config key"):
        desktop_read_config_value("paradev.desktop.gui")


def test_desktop_dependency_status_detects_imagemagick(monkeypatch) -> None:
    def which(command: str) -> str | None:
        return {
            "brew": "/opt/homebrew/bin/brew",
            "magick": "/opt/homebrew/bin/magick",
        }.get(command)

    monkeypatch.setattr(desktop_local.shutil, "which", which)
    monkeypatch.setattr(desktop_local.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(desktop_local, "_command_version", lambda path: "ImageMagick 7.1.2")

    payload = desktop_local.desktop_dependency_status("imagemagick")

    assert payload == {
        "schema": "paradev.desktop.dependency.v1",
        "id": "imagemagick",
        "label": "ImageMagick",
        "installed": True,
        "status": "ready",
        "path": "/opt/homebrew/bin/magick",
        "version": "ImageMagick 7.1.2",
        "installCommand": ["brew", "install", "imagemagick"],
        "installSupported": True,
        "detail": "Required for asset inspection, conversion, and DDS/TGA/image workflows.",
    }


def test_desktop_llm_route_reports_route_specific_empty_response(monkeypatch, cm_paradev_lock) -> None:
    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://openrouter.ai/api/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **_kwargs) -> None:
            pass

        def chat(self, _prompt: str) -> str:
            return ""

    with (
        _temporary_unset_cm_paradev_value("paradev.ai.base_url"),
        _temporary_unset_cm_paradev_value("paradev.ai.key_env"),
    ):
        monkeypatch.setenv("OPENROUTER_API_KEY", "present")
        monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

        payload = desktop_local.desktop_test_llm_route(
            "openrouter",
            "deepseek-reasoner",
            "openai",
            key_env="OPENROUTER_API_KEY",
            base_url="https://openrouter.ai/api/v1",
            preset="reason",
        )

    assert payload["schema"] == "paradev.desktop.llm-test.v1"
    assert payload["provider"] == "openrouter"
    assert payload["model"] == "deepseek-reasoner"
    assert payload["gateway"] == "openai"
    assert payload["preset"] == "reason"
    assert payload["keySource"] == "OPENROUTER_API_KEY"
    assert payload["baseUrl"] == "https://openrouter.ai/api/v1"
    assert payload["status"] == "warning"
    assert payload["resultCode"] == "empty_response"
    assert payload["detail"] == "openrouter / deepseek-reasoner route returned an empty response."
    assert str(payload["checkedAt"]).endswith("Z")


def test_desktop_llm_route_uses_configured_key_env(monkeypatch, cm_paradev_lock) -> None:
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **kwargs) -> None:
            captured["kwargs"] = kwargs

        def chat(self, _prompt: str) -> str:
            return "hb-ok"

    previous = CM_PARADEV.get("paradev.ai.key_env", default=None)
    previous_base_url = CM_PARADEV.get("paradev.ai.base_url", default=None)
    try:
        CM_PARADEV.unset("paradev.ai.base_url")
        desktop_write_config_value("paradev.ai.key_env", "CUSTOM_DEEPSEEK_KEY")
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        monkeypatch.setenv("CUSTOM_DEEPSEEK_KEY", "custom-secret")
        monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

        payload = desktop_local.desktop_test_llm_route("deepseek", "deepseek-v4-flash", "openai", preset="chat")

        assert payload["keySource"] == "CUSTOM_DEEPSEEK_KEY"
        assert payload["status"] == "ready"
        assert payload["resultCode"] == "ok"
        assert captured["kwargs"] == {
            "api_key": "custom-secret",
            "cache": False,
            "gateway": "openai",
            "max_tokens": 8,
            "model": "deepseek-v4-flash",
            "preset": "chat",
            "provider": "deepseek",
            "temperature": 0,
        }
    finally:
        _restore_cm_paradev_value("paradev.ai.key_env", previous)
        _restore_cm_paradev_value("paradev.ai.base_url", previous_base_url)


def test_desktop_llm_route_passes_configured_preset_to_heavenbase(monkeypatch, cm_paradev_lock) -> None:
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **kwargs) -> None:
            captured["kwargs"] = kwargs

        def chat(self, _prompt: str) -> str:
            return "hb-ok"

    get_config_value = desktop_local.CM_PARADEV.get

    def get_value(key: str, *args, **kwargs) -> object:
        if key == "paradev.ai.preset":
            return "reason"
        return get_config_value(key, *args, **kwargs)

    monkeypatch.setattr(desktop_local.CM_PARADEV, "get", get_value)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "present")
    monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

    payload = desktop_local.desktop_test_llm_route(
        "deepseek",
        "deepseek-v4-flash",
        "openai",
        key_env="DEEPSEEK_API_KEY",
        base_url="",
    )

    assert payload["preset"] == "reason"
    assert payload["status"] == "ready"
    assert captured["kwargs"]["preset"] == "reason"


def test_desktop_llm_route_prefers_explicit_visible_key_env(monkeypatch, cm_paradev_lock) -> None:
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **kwargs) -> None:
            captured["kwargs"] = kwargs

        def chat(self, _prompt: str) -> str:
            return "hb-ok"

    previous = CM_PARADEV.get("paradev.ai.key_env", default=None)
    previous_base_url = CM_PARADEV.get("paradev.ai.base_url", default=None)
    try:
        CM_PARADEV.unset("paradev.ai.base_url")
        desktop_write_config_value("paradev.ai.key_env", "PERSISTED_DEEPSEEK_KEY")
        monkeypatch.delenv("PERSISTED_DEEPSEEK_KEY", raising=False)
        monkeypatch.setenv("VISIBLE_DEEPSEEK_KEY", "visible-secret")
        monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

        payload = desktop_local.desktop_test_llm_route(
            "deepseek",
            "deepseek-v4-flash",
            "openai",
            key_env="VISIBLE_DEEPSEEK_KEY",
            preset="chat",
        )

        assert payload["keySource"] == "VISIBLE_DEEPSEEK_KEY"
        assert payload["status"] == "ready"
        assert payload["resultCode"] == "ok"
        assert captured["kwargs"] == {
            "api_key": "visible-secret",
            "cache": False,
            "gateway": "openai",
            "max_tokens": 8,
            "model": "deepseek-v4-flash",
            "preset": "chat",
            "provider": "deepseek",
            "temperature": 0,
        }
    finally:
        _restore_cm_paradev_value("paradev.ai.key_env", previous)
        _restore_cm_paradev_value("paradev.ai.base_url", previous_base_url)


def test_desktop_ai_chat_returns_deepseek_reply(monkeypatch, cm_paradev_lock) -> None:
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **kwargs) -> None:
            captured["kwargs"] = kwargs

        def chat(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "Focus trees are ordered sets of HoI4 goals."

    with (
        _temporary_unset_cm_paradev_value("paradev.ai.base_url"),
        _temporary_unset_cm_paradev_value("paradev.ai.key_env"),
    ):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "present")
        monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

        payload = desktop_local.desktop_chat(
            provider="deepseek",
            model="deepseek-v4-flash",
            gateway="openai",
            prompt="Explain this focus tree.",
            role="explain",
            project_root="/tmp/PIHC3",
            preset="chat",
        )

        assert payload["schema"] == "paradev.desktop.ai-chat.v1"
        assert payload["provider"] == "deepseek"
        assert payload["model"] == "deepseek-v4-flash"
        assert payload["gateway"] == "openai"
        assert payload["keySource"] == "DEEPSEEK_API_KEY"
        assert payload["baseUrl"] == "https://api.deepseek.com/v1"
        assert payload["status"] == "ready"
        assert payload["role"] == "explain"
        assert payload["projectRoot"] == "/tmp/PIHC3"
        assert payload["prompt"] == "Explain this focus tree."
        assert payload["reply"] == "Focus trees are ordered sets of HoI4 goals."
        assert payload["detail"] == ""
        assert str(payload["checkedAt"]).endswith("Z")
        assert "Explain HoI4 code" in str(captured["prompt"])
        assert "Active ParaDev project: /tmp/PIHC3" in str(captured["prompt"])
        assert "Explain this focus tree." in str(captured["prompt"])
        assert captured["kwargs"] == {
            "api_key": "present",
            "cache": False,
            "gateway": "openai",
            "max_tokens": 1024,
            "model": "deepseek-v4-flash",
            "preset": "chat",
            "provider": "deepseek",
            "temperature": 0,
        }


def test_desktop_ai_chat_passes_explicit_preset_to_heavenbase(monkeypatch, cm_paradev_lock) -> None:
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **kwargs) -> None:
            captured["kwargs"] = kwargs

        def chat(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "Use the configured reasoning route."

    with (
        _temporary_unset_cm_paradev_value("paradev.ai.base_url"),
        _temporary_unset_cm_paradev_value("paradev.ai.key_env"),
    ):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "present")
        monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

        payload = desktop_local.desktop_chat(
            provider="deepseek",
            model="deepseek-v4-flash",
            gateway="openai",
            prompt="Explain this idea.",
            role="chat",
            project_root="/tmp/PIHC3",
            preset="reason",
        )

        assert payload["preset"] == "reason"
        assert payload["reply"] == "Use the configured reasoning route."
        assert captured["kwargs"]["preset"] == "reason"
        assert "Explain this idea." in str(captured["prompt"])


def test_desktop_ai_chat_uses_configured_key_env(monkeypatch, cm_paradev_lock) -> None:
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **kwargs) -> None:
            captured["kwargs"] = kwargs

        def chat(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "The configured key env was used."

    previous = CM_PARADEV.get("paradev.ai.key_env", default=None)
    previous_base_url = CM_PARADEV.get("paradev.ai.base_url", default=None)
    try:
        CM_PARADEV.unset("paradev.ai.base_url")
        desktop_write_config_value("paradev.ai.key_env", "CUSTOM_DEEPSEEK_KEY")
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        monkeypatch.setenv("CUSTOM_DEEPSEEK_KEY", "custom-secret")
        monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

        payload = desktop_local.desktop_chat(
            provider="deepseek",
            model="deepseek-v4-flash",
            gateway="openai",
            prompt="Explain this idea.",
            role="chat",
            project_root="/tmp/PIHC3",
            preset="chat",
        )

        assert payload["keySource"] == "CUSTOM_DEEPSEEK_KEY"
        assert payload["reply"] == "The configured key env was used."
        assert captured["kwargs"] == {
            "api_key": "custom-secret",
            "cache": False,
            "gateway": "openai",
            "max_tokens": 1024,
            "model": "deepseek-v4-flash",
            "preset": "chat",
            "provider": "deepseek",
            "temperature": 0,
        }
        assert "Explain this idea." in str(captured["prompt"])
    finally:
        _restore_cm_paradev_value("paradev.ai.key_env", previous)
        _restore_cm_paradev_value("paradev.ai.base_url", previous_base_url)


def test_desktop_ai_chat_uses_configured_base_url(monkeypatch, cm_paradev_lock) -> None:
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": str(captured["kwargs"]["base_url"])}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **kwargs) -> None:
            captured["kwargs"] = kwargs

        def chat(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "The configured base URL was used."

    previous_base_url = CM_PARADEV.get("paradev.ai.base_url", default=None)
    previous_key_env = CM_PARADEV.get("paradev.ai.key_env", default=None)
    try:
        desktop_write_config_value("paradev.ai.base_url", " https://proxy.example/v1 ")
        CM_PARADEV.unset("paradev.ai.key_env")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "present")
        monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

        payload = desktop_local.desktop_chat(
            provider="deepseek",
            model="deepseek-v4-flash",
            gateway="openai",
            prompt="Explain this idea.",
            role="chat",
            project_root="/tmp/PIHC3",
            preset="chat",
        )

        assert payload["baseUrl"] == "https://proxy.example/v1"
        assert payload["reply"] == "The configured base URL was used."
        assert captured["kwargs"] == {
            "api_key": "present",
            "base_url": "https://proxy.example/v1",
            "cache": False,
            "gateway": "openai",
            "max_tokens": 1024,
            "model": "deepseek-v4-flash",
            "preset": "chat",
            "provider": "deepseek",
            "temperature": 0,
        }
        assert "Explain this idea." in str(captured["prompt"])
    finally:
        _restore_cm_paradev_value("paradev.ai.base_url", previous_base_url)
        _restore_cm_paradev_value("paradev.ai.key_env", previous_key_env)


def test_desktop_ai_chat_prefers_explicit_visible_key_env(monkeypatch, cm_paradev_lock) -> None:
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **kwargs) -> None:
            captured["kwargs"] = kwargs

        def chat(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "Use this visible key."

    previous = CM_PARADEV.get("paradev.ai.key_env", default=None)
    previous_base_url = CM_PARADEV.get("paradev.ai.base_url", default=None)
    try:
        CM_PARADEV.unset("paradev.ai.base_url")
        desktop_write_config_value("paradev.ai.key_env", "PERSISTED_DEEPSEEK_KEY")
        monkeypatch.delenv("PERSISTED_DEEPSEEK_KEY", raising=False)
        monkeypatch.setenv("VISIBLE_DEEPSEEK_KEY", "visible-secret")
        monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

        payload = desktop_local.desktop_chat(
            provider="deepseek",
            model="deepseek-v4-flash",
            gateway="openai",
            prompt="Explain this idea.",
            role="explain",
            project_root="/tmp/PIHC3",
            key_env="VISIBLE_DEEPSEEK_KEY",
            preset="chat",
        )

        assert payload["keySource"] == "VISIBLE_DEEPSEEK_KEY"
        assert payload["status"] == "ready"
        assert payload["reply"] == "Use this visible key."
        assert captured["kwargs"] == {
            "api_key": "visible-secret",
            "cache": False,
            "gateway": "openai",
            "max_tokens": 1024,
            "model": "deepseek-v4-flash",
            "preset": "chat",
            "provider": "deepseek",
            "temperature": 0,
        }
        assert "Explain this idea." in str(captured["prompt"])
    finally:
        _restore_cm_paradev_value("paradev.ai.key_env", previous)
        _restore_cm_paradev_value("paradev.ai.base_url", previous_base_url)


def test_desktop_ai_chat_includes_project_source_context(monkeypatch, tmp_path: Path) -> None:
    project_root = tmp_path / "PIHC3"
    source_path = project_root / "src" / "modules" / "focus_tree" / "C01_MAIN" / "info.json"
    source_path.parent.mkdir(parents=True)
    source_path.write_text('{"id": "C01_MAIN", "focus": "industry"}\n', encoding="utf-8")
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **_kwargs) -> None:
            pass

        def chat(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "The attached focus source defines an industry focus."

    monkeypatch.setenv("DEEPSEEK_API_KEY", "present")
    monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

    payload = desktop_local.desktop_chat(
        provider="deepseek",
        model="deepseek-v4-flash",
        gateway="openai",
        prompt="Explain the selected focus.",
        role="explain",
        project_root=str(project_root),
        sources=[
            {
                "kind": "source",
                "label": "C01 focus metadata",
                "path": "src/modules/focus_tree/C01_MAIN/info.json",
            }
        ],
    )

    effective_prompt = str(captured["prompt"])
    assert "Attached sources:" in effective_prompt
    assert "C01 focus metadata" in effective_prompt
    assert "src/modules/focus_tree/C01_MAIN/info.json" in effective_prompt
    assert '"focus": "industry"' in effective_prompt
    assert payload["sources"] == [
        {
            "kind": "source",
            "label": "C01 focus metadata",
            "path": str(source_path.resolve()),
            "relativePath": "src/modules/focus_tree/C01_MAIN/info.json",
            "contentChars": 40,
            "truncated": False,
        }
    ]


def test_desktop_ai_chat_prefers_inline_project_source_content(monkeypatch, tmp_path: Path, cm_paradev_lock) -> None:
    project_root = tmp_path / "PIHC3"
    source_path = project_root / "src" / "modules" / "focus_tree" / "C01_MAIN" / "info.json"
    source_path.parent.mkdir(parents=True)
    source_path.write_text('{"id": "C01_MAIN", "focus": "old"}\n', encoding="utf-8")
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **_kwargs) -> None:
            pass

        def chat(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "The unsaved draft changes the focus."

    monkeypatch.setenv("DEEPSEEK_API_KEY", "present")
    monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))
    previous = CM_PARADEV.get("paradev.ai.chat.profiles", default=None)
    previous_payload = plain_json(previous) if previous is not None else None

    try:
        CM_PARADEV.unset("paradev.ai.chat.profiles")
        payload = desktop_local.desktop_chat(
            provider="deepseek",
            model="deepseek-v4-flash",
            gateway="openai",
            prompt="Explain the selected focus draft.",
            role="explain",
            project_root=str(project_root),
            sources=[
                {
                    "content": '{"id": "C01_MAIN", "focus": "new"}\n',
                    "kind": "source",
                    "label": "C01 focus metadata",
                    "path": "src/modules/focus_tree/C01_MAIN/info.json",
                }
            ],
        )
    finally:
        if previous_payload is None:
            CM_PARADEV.unset("paradev.ai.chat.profiles")
        else:
            CM_PARADEV.set("paradev.ai.chat.profiles", previous_payload)

    effective_prompt = str(captured["prompt"])
    assert '"focus": "new"' in effective_prompt
    assert '"focus": "old"' not in effective_prompt
    assert payload["sources"] == [
        {
            "content": '{"id": "C01_MAIN", "focus": "new"}\n',
            "kind": "source",
            "label": "C01 focus metadata",
            "path": str(source_path.resolve()),
            "relativePath": "src/modules/focus_tree/C01_MAIN/info.json",
            "contentChars": 35,
            "truncated": False,
        }
    ]


def test_desktop_ai_chat_preserves_empty_inline_project_source_content(monkeypatch, tmp_path: Path, cm_paradev_lock) -> None:
    project_root = tmp_path / "PIHC3"
    source_path = project_root / "src" / "modules" / "focus_tree" / "C01_MAIN" / "info.json"
    source_path.parent.mkdir(parents=True)
    source_path.write_text('{"id": "C01_MAIN", "focus": "old"}\n', encoding="utf-8")
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **_kwargs) -> None:
            pass

        def chat(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "The draft is empty."

    monkeypatch.setenv("DEEPSEEK_API_KEY", "present")
    monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))
    previous = CM_PARADEV.get("paradev.ai.chat.profiles", default=None)
    previous_payload = plain_json(previous) if previous is not None else None

    try:
        CM_PARADEV.unset("paradev.ai.chat.profiles")
        payload = desktop_local.desktop_chat(
            provider="deepseek",
            model="deepseek-v4-flash",
            gateway="openai",
            prompt="Explain the selected focus draft.",
            role="explain",
            project_root=str(project_root),
            sources=[
                {
                    "content": "",
                    "kind": "source",
                    "label": "C01 focus metadata",
                    "path": "src/modules/focus_tree/C01_MAIN/info.json",
                }
            ],
        )
    finally:
        if previous_payload is None:
            CM_PARADEV.unset("paradev.ai.chat.profiles")
        else:
            CM_PARADEV.set("paradev.ai.chat.profiles", previous_payload)

    effective_prompt = str(captured["prompt"])
    assert '"focus": "old"' not in effective_prompt
    assert "```text\n\n```" in effective_prompt
    assert payload["sources"] == [
        {
            "content": "",
            "kind": "source",
            "label": "C01 focus metadata",
            "path": str(source_path.resolve()),
            "relativePath": "src/modules/focus_tree/C01_MAIN/info.json",
            "contentChars": 0,
            "truncated": False,
        }
    ]


def test_desktop_ai_chat_includes_metadata_source_content(monkeypatch, tmp_path: Path) -> None:
    project_root = tmp_path / "PIHC3"
    project_root.mkdir()
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **_kwargs) -> None:
            pass

        def chat(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "Fix the missing focus icon first."

    monkeypatch.setenv("DEEPSEEK_API_KEY", "present")
    monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

    payload = desktop_local.desktop_chat(
        provider="deepseek",
        model="deepseek-v4-flash",
        gateway="openai",
        prompt="What should I fix before building?",
        role="build",
        project_root=str(project_root),
        sources=[
            {
                "content": "1. [error] src/modules/focus_tree/C01_MAIN/info.json: Missing focus icon.",
                "kind": "diagnostics",
                "label": "Diagnostics (1)",
            }
        ],
    )

    effective_prompt = str(captured["prompt"])
    assert "Project.build(...)" in effective_prompt
    assert "desktop_project_build_command(...)" in effective_prompt
    assert "Context: diagnostics" in effective_prompt
    assert "Diagnostics (1)" in effective_prompt
    assert "Missing focus icon" in effective_prompt
    assert payload["sources"] == [
        {
            "content": "1. [error] src/modules/focus_tree/C01_MAIN/info.json: Missing focus icon.",
            "contentChars": 73,
            "kind": "diagnostics",
            "label": "Diagnostics (1)",
            "truncated": False,
        }
    ]


def test_desktop_ai_chat_rejects_sources_outside_project(monkeypatch, tmp_path: Path) -> None:
    project_root = tmp_path / "PIHC3"
    project_root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    monkeypatch.setitem(sys.modules, "heavenbase", SimpleNamespace(LLM=object))

    with pytest.raises(ValueError, match="outside the active project root"):
        desktop_local.desktop_chat(
            provider="deepseek",
            model="deepseek-v4-flash",
            gateway="openai",
            prompt="Explain this.",
            role="explain",
            project_root=str(project_root),
            sources=[{"kind": "source", "path": str(outside)}],
        )


def test_desktop_ai_chat_profiles_describe_managed_roles(cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.ai.chat.profiles", default=None)
    previous_payload = plain_json(previous) if previous is not None else None

    try:
        CM_PARADEV.unset("paradev.ai.chat.profiles")
        payload = desktop_chat_profiles(project_root="/tmp/PIHC3")

        assert payload["schema"] == "paradev.desktop.ai-chat-profiles.v1"
        assert payload["projectRoot"] == "/tmp/PIHC3"
        assert payload["defaultRole"] == "chat"
        assert payload["sourceKinds"] == [
            "project",
            "selection",
            "diagnostics",
            "templates",
        ]
        assert payload["sourceKindRows"] == [
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
        ]
        profiles = {str(profile["id"]): profile for profile in payload["profiles"]}
        assert {"chat", "explain", "create-module", "build"} <= set(profiles)
        assert profiles["chat"]["labelKey"] == "chat.profile.chat.label"
        assert profiles["chat"]["detailKey"] == "chat.profile.chat.detail"
        assert profiles["explain"]["label"] == "Explain HoI4 code"
        assert profiles["explain"]["labelKey"] == "chat.profile.explain.label"
        assert profiles["explain"]["detailKey"] == "chat.profile.explain.detail"
        assert profiles["create-module"]["sourceKinds"] == ["project", "templates"]
        assert profiles["create-module"]["operationIds"] == [
            "module.draft",
            "module.create_batch",
            "collection.scaffold",
        ]
        assert profiles["create-module"]["operationCards"] == [
            {
                "id": "module.draft",
                "title": "Module Draft",
                "summary": "Plan or write a source-module draft from a frontend browser family id.",
                "mutates": True,
                "sdk": "Project.create_module_draft",
                "rest": "POST /projects/{project_id}/modules/{family_id}/drafts",
            },
            {
                "id": "module.create_batch",
                "title": "Module Create Batch",
                "summary": "Plan or atomically create several source modules from one guarded plan.",
                "mutates": True,
                "sdk": "Project.create_modules",
                "rest": "POST /projects/modules/create-batch",
            },
            {
                "id": "collection.scaffold",
                "title": "Collection Scaffold",
                "summary": "Plan or transactionally write a collection from a Registry-backed template.",
                "mutates": True,
                "sdk": "Project.scaffold_collection",
                "rest": "POST /projects/collections/scaffold",
            },
        ]
        assert profiles["build"]["operationIds"] == ["build.plan", "build.start"]
        assert [card["id"] for card in profiles["build"]["operationCards"]] == [
            "build.plan",
            "build.start",
        ]
        assert "ParaDev SDK" in str(profiles["build"]["prompt"])
    finally:
        if previous_payload is None:
            CM_PARADEV.unset("paradev.ai.chat.profiles")
        else:
            CM_PARADEV.set("paradev.ai.chat.profiles", previous_payload)


def test_desktop_ai_chat_profile_operation_ids_resolve_to_sdk_owned_frontend_rows(
    cm_paradev_lock,
) -> None:
    from paradev.sdk import get_frontend_api_contract

    previous = CM_PARADEV.get("paradev.ai.chat.profiles", default=None)
    previous_payload = plain_json(previous) if previous is not None else None

    try:
        CM_PARADEV.unset("paradev.ai.chat.profiles")
        operation_rows = {str(row["id"]): row for row in get_frontend_api_contract()["operations"]}
        payload = desktop_chat_profiles(project_root="/tmp/PIHC3")

        operation_ids = [str(operation_id) for profile in payload["profiles"] for operation_id in profile.get("operationIds", [])]

        assert operation_ids == [
            "module.draft",
            "module.create_batch",
            "collection.scaffold",
            "build.plan",
            "build.start",
        ]
        for operation_id in operation_ids:
            row = operation_rows[operation_id]
            assert row["status"] == "implemented"
            assert row["status"] != "frontend-local"
            assert row["sdk"]
        for profile in payload["profiles"]:
            for card in profile.get("operationCards", []):
                row = operation_rows[str(card["id"])]
                assert card["summary"] == row["summary"]
                assert card["mutates"] is (row.get("mutates") is True)
    finally:
        if previous_payload is None:
            CM_PARADEV.unset("paradev.ai.chat.profiles")
        else:
            CM_PARADEV.set("paradev.ai.chat.profiles", previous_payload)


def test_desktop_ai_chat_default_role_is_sdk_configured(cm_paradev_lock) -> None:
    previous = CM_PARADEV.get("paradev.ai.chat.default_role", default=None)

    try:
        CM_PARADEV.unset("paradev.ai.chat.default_role")
        assert desktop_read_config_value("paradev.ai.chat.default_role") == {
            "schema": "paradev.desktop.config-value.v1",
            "key": "paradev.ai.chat.default_role",
            "value": "chat",
        }

        assert desktop_write_config_value("paradev.ai.chat.default_role", "build") == {
            "schema": "paradev.desktop.config-value.v1",
            "key": "paradev.ai.chat.default_role",
            "value": "build",
        }
        assert desktop_chat_profiles(project_root="/tmp/PIHC3")["defaultRole"] == "build"

        with pytest.raises(ValueError, match="Unsupported AI chat role"):
            desktop_write_config_value("paradev.ai.chat.default_role", "missing")
    finally:
        _restore_cm_paradev_value("paradev.ai.chat.default_role", previous)


def test_desktop_ai_chat_uses_managed_role_prompt(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **_kwargs) -> None:
            pass

        def chat(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "This focus grants a national spirit."

    monkeypatch.setenv("DEEPSEEK_API_KEY", "present")
    monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))

    payload = desktop_local.desktop_chat(
        provider="deepseek",
        model="deepseek-v4-flash",
        gateway="openai",
        prompt="What does this focus do?",
        role="explain",
        project_root="/tmp/PIHC3",
    )

    effective_prompt = str(captured["prompt"])
    assert "Explain HoI4 code" in effective_prompt
    assert "Active ParaDev project: /tmp/PIHC3" in effective_prompt
    assert "What does this focus do?" in effective_prompt
    assert payload["role"] == "explain"
    assert payload["prompt"] == "What does this focus do?"


def test_desktop_ai_chat_profile_overrides_persist_and_feed_chat(monkeypatch, tmp_path: Path, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path))
    previous = CM_PARADEV.get("paradev.ai.chat.profiles", default=None)
    previous_payload = plain_json(previous) if previous is not None else None
    captured: dict[str, object] = {}

    class FakeSpec:
        def runtime(self) -> dict[str, str]:
            return {"base_url": "https://api.deepseek.com/v1"}

    class FakeLLM:
        spec = FakeSpec()

        def __init__(self, **_kwargs) -> None:
            pass

        def chat(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "Use the edited explanation profile."

    try:
        payload = desktop_local.desktop_write_chat_profile(
            "explain",
            {
                "label": "Explain HoI4 code",
                "detail": "Custom PIHC3 source explanation.",
                "prompt": "Prefer PIHC3 source files and name the SDK operation that should make changes.",
                "sourceKinds": ["project", "selection", "diagnostics"],
            },
            project_root="/tmp/PIHC3",
        )

        profiles = {str(profile["id"]): profile for profile in payload["profiles"]}
        assert payload["schema"] == "paradev.desktop.ai-chat-profiles.v1"
        assert payload["projectRoot"] == "/tmp/PIHC3"
        assert profiles["explain"]["prompt"] == "Prefer PIHC3 source files and name the SDK operation that should make changes."
        assert profiles["explain"]["sourceKinds"] == [
            "project",
            "selection",
            "diagnostics",
        ]
        stored = plain_json(CM_PARADEV.get("paradev.ai.chat.profiles"))
        assert stored["projects"]["/tmp/PIHC3"]["profiles"]["explain"]["prompt"] == profiles["explain"]["prompt"]
        assert desktop_chat_profiles(project_root="/tmp/PIHC3")["profiles"][1]["prompt"] == profiles["explain"]["prompt"]

        monkeypatch.setenv("DEEPSEEK_API_KEY", "present")
        monkeypatch.setitem(sys.modules, "heavenbase", _fake_heavenbase(FakeLLM))
        chat_payload = desktop_local.desktop_chat(
            provider="deepseek",
            model="deepseek-v4-flash",
            gateway="openai",
            prompt="Explain this selected idea.",
            role="explain",
            project_root="/tmp/PIHC3",
        )

        assert chat_payload["reply"] == "Use the edited explanation profile."
        assert "Prefer PIHC3 source files" in str(captured["prompt"])
        assert "Explain this selected idea." in str(captured["prompt"])
    finally:
        if previous_payload is None:
            CM_PARADEV.unset("paradev.ai.chat.profiles")
        else:
            CM_PARADEV.set("paradev.ai.chat.profiles", previous_payload)


def test_desktop_ai_chat_profile_overrides_are_project_scoped(monkeypatch, tmp_path: Path, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path))
    previous = CM_PARADEV.get("paradev.ai.chat.profiles", default=None)
    previous_payload = plain_json(previous) if previous is not None else None

    try:
        CM_PARADEV.unset("paradev.ai.chat.profiles")

        pihc3_payload = desktop_local.desktop_write_chat_profile(
            "explain",
            {
                "label": "Explain HoI4 code",
                "detail": "PIHC3 source explanation.",
                "prompt": "Prefer PIHC3 source files.",
                "sourceKinds": ["project", "selection", "templates"],
            },
            project_root="/tmp/PIHC3",
        )
        demo_payload = desktop_local.desktop_write_chat_profile(
            "explain",
            {
                "label": "Explain HoI4 code",
                "detail": "Demo source explanation.",
                "prompt": "Prefer demo source files.",
                "sourceKinds": ["project", "diagnostics"],
            },
            project_root="/tmp/Demo",
        )

        pihc3_profiles = {str(profile["id"]): profile for profile in desktop_chat_profiles(project_root="/tmp/PIHC3")["profiles"]}
        demo_profiles = {str(profile["id"]): profile for profile in desktop_chat_profiles(project_root="/tmp/Demo")["profiles"]}
        stored = plain_json(CM_PARADEV.get("paradev.ai.chat.profiles"))

        assert pihc3_payload["projectRoot"] == "/tmp/PIHC3"
        assert demo_payload["projectRoot"] == "/tmp/Demo"
        assert pihc3_profiles["explain"]["prompt"] == "Prefer PIHC3 source files."
        assert pihc3_profiles["explain"]["sourceKinds"] == [
            "project",
            "selection",
            "templates",
        ]
        assert demo_profiles["explain"]["prompt"] == "Prefer demo source files."
        assert demo_profiles["explain"]["sourceKinds"] == ["project", "diagnostics"]
        assert stored["projects"]["/tmp/PIHC3"]["profiles"]["explain"]["prompt"] == "Prefer PIHC3 source files."
        assert stored["projects"]["/tmp/Demo"]["profiles"]["explain"]["prompt"] == "Prefer demo source files."
    finally:
        if previous_payload is None:
            CM_PARADEV.unset("paradev.ai.chat.profiles")
        else:
            CM_PARADEV.set("paradev.ai.chat.profiles", previous_payload)


def test_desktop_ai_chat_profile_reset_removes_one_override(monkeypatch, tmp_path: Path, cm_paradev_lock) -> None:
    monkeypatch.setenv("PARADEV_ROOT", str(tmp_path))
    previous = CM_PARADEV.get("paradev.ai.chat.profiles", default=None)
    previous_payload = plain_json(previous) if previous is not None else None

    try:
        desktop_local.desktop_write_chat_profile(
            "explain",
            {
                "label": "Explain HoI4 code",
                "detail": "Custom PIHC3 source explanation.",
                "prompt": "Prefer PIHC3 source files and name the SDK operation that should make changes.",
                "sourceKinds": ["project", "selection", "diagnostics"],
            },
        )
        desktop_local.desktop_write_chat_profile(
            "build",
            {
                "label": "Build/debug project",
                "detail": "Keep this build override.",
                "prompt": "Use PIHC3 build logs before suggesting actions.",
                "sourceKinds": ["project", "diagnostics"],
            },
        )

        payload = desktop_reset_chat_profile("explain")
        profiles = {str(profile["id"]): profile for profile in payload["profiles"]}
        stored = plain_json(CM_PARADEV.get("paradev.ai.chat.profiles"))

        assert payload["schema"] == "paradev.desktop.ai-chat-profiles.v1"
        assert payload["projectRoot"] == ""
        assert (
            profiles["explain"]["prompt"]
            == "Explain HoI4 code and ParaDev source files for a modder. Name the relevant file roles, likely game effect, and any SDK-backed next action."
        )
        assert profiles["explain"]["sourceKinds"] == ["project", "selection"]
        assert profiles["build"]["prompt"] == "Use PIHC3 build logs before suggesting actions."
        assert "explain" not in stored["profiles"]
        assert stored["profiles"]["build"]["prompt"] == "Use PIHC3 build logs before suggesting actions."
    finally:
        if previous_payload is None:
            CM_PARADEV.unset("paradev.ai.chat.profiles")
        else:
            CM_PARADEV.set("paradev.ai.chat.profiles", previous_payload)


def test_desktop_ai_chat_profile_write_rejects_unknown_roles() -> None:
    with pytest.raises(ValueError, match="Unsupported AI chat role"):
        desktop_local.desktop_write_chat_profile("new-role", {"prompt": "Custom prompt."})
    with pytest.raises(ValueError, match="sourceKinds"):
        desktop_local.desktop_write_chat_profile("explain", {"sourceKinds": "project"})
    with pytest.raises(ValueError, match="Unsupported AI chat source kind"):
        desktop_local.desktop_write_chat_profile("explain", {"sourceKinds": ["project", "unknown"]})


def test_desktop_config_rest_routes_forward_dependency_and_llm_requests(
    monkeypatch,
) -> None:
    testclient = pytest.importorskip("fastapi.testclient")
    from paradev.surfaces import rest

    dependency_payload = {
        "schema": "paradev.desktop.dependency.v1",
        "id": "imagemagick",
        "label": "ImageMagick",
        "installed": True,
        "status": "ready",
        "path": "/opt/homebrew/bin/magick",
        "version": "ImageMagick 7.1.2",
        "installCommand": ["brew", "install", "imagemagick"],
        "installSupported": True,
    }
    llm_payload = {
        "schema": "paradev.desktop.llm-test.v1",
        "provider": "deepseek",
        "model": "deepseek-v4-flash",
        "gateway": "openai",
        "preset": "chat",
        "keySource": "DEEPSEEK_API_KEY",
        "baseUrl": "https://api.deepseek.com/v1",
        "status": "ready",
        "resultCode": "ok",
        "detail": "Received hb-ok.",
        "checkedAt": "2026-06-28T00:00:00Z",
    }
    chat_payload = {
        "schema": "paradev.desktop.ai-chat.v1",
        "provider": "deepseek",
        "model": "deepseek-v4-flash",
        "gateway": "openai",
        "preset": "chat",
        "keySource": "DEEPSEEK_API_KEY",
        "baseUrl": "https://api.deepseek.com/v1",
        "status": "ready",
        "role": "explain",
        "projectRoot": "/tmp/PIHC3",
        "prompt": "Explain this idea.",
        "reply": "This idea grants a national spirit.",
        "detail": "",
        "checkedAt": "2026-06-28T00:00:00Z",
    }
    profiles_payload = {
        "schema": "paradev.desktop.ai-chat-profiles.v1",
        "defaultRole": "chat",
        "projectRoot": "/tmp/PIHC3",
        "profiles": [
            {
                "id": "chat",
                "label": "Chat",
                "detail": "General help",
                "prompt": "Help with ParaDev.",
                "sourceKinds": ["project"],
            }
        ],
    }
    written_profiles: list[dict[str, object]] = []
    reset_profiles: list[dict[str, object]] = []

    monkeypatch.setattr(
        rest,
        "desktop_dependency_status",
        lambda dependency_id: {**dependency_payload, "id": dependency_id},
    )
    monkeypatch.setattr(
        rest,
        "desktop_install_dependency",
        lambda dependency_id: {**dependency_payload, "id": dependency_id},
    )
    monkeypatch.setattr(
        rest,
        "desktop_test_llm_route",
        lambda provider, model, gateway, key_env=None, base_url=None, preset=None: {
            **llm_payload,
            "provider": provider,
            "model": model,
            "gateway": gateway,
            "preset": preset or llm_payload["preset"],
            "keySource": key_env or llm_payload["keySource"],
            "baseUrl": base_url or llm_payload["baseUrl"],
        },
    )
    monkeypatch.setattr(
        rest,
        "desktop_chat",
        lambda provider, model, gateway, prompt, role, project_root, sources, key_env=None, base_url=None, preset=None: {
            **chat_payload,
            "provider": provider,
            "model": model,
            "gateway": gateway,
            "preset": preset or chat_payload["preset"],
            "keySource": key_env or chat_payload["keySource"],
            "baseUrl": base_url or chat_payload["baseUrl"],
            "prompt": prompt,
            "role": role,
            "projectRoot": project_root,
            "sources": sources,
        },
    )
    monkeypatch.setattr(
        rest,
        "desktop_chat_profiles",
        lambda project_root="": {**profiles_payload, "projectRoot": project_root},
    )
    monkeypatch.setattr(
        rest,
        "desktop_write_chat_profile",
        lambda profile_id, profile, project_root="": (
            written_profiles.append(
                {
                    "profile_id": profile_id,
                    "profile": profile,
                    "project_root": project_root,
                }
            )
            or {
                **profiles_payload,
                "projectRoot": project_root,
                "profiles": [{**profiles_payload["profiles"][0], **profile, "id": profile_id}],
            }
        ),
    )
    monkeypatch.setattr(
        rest,
        "desktop_reset_chat_profile",
        lambda profile_id, project_root="": (
            reset_profiles.append({"profile_id": profile_id, "project_root": project_root})
            or {
                **profiles_payload,
                "projectRoot": project_root,
                "profiles": [{**profiles_payload["profiles"][0], "id": profile_id}],
            }
        ),
    )

    client = testclient.TestClient(rest.build_app())

    status_response = client.get("/desktop/dependencies/imagemagick")
    install_response = client.post("/desktop/dependencies/imagemagick/install")
    llm_response = client.post(
        "/desktop/llm/test",
        json={
            "provider": "deepseek",
            "model": "deepseek-v4-flash",
            "gateway": "openai",
            "preset": "reason",
            "keyEnv": "VISIBLE_DEEPSEEK_KEY",
        },
    )
    chat_response = client.post(
        "/desktop/ai/chat",
        json={
            "provider": "deepseek",
            "model": "deepseek-v4-flash",
            "gateway": "openai",
            "preset": "reason",
            "prompt": "Explain this idea.",
            "role": "explain",
            "projectRoot": "/tmp/PIHC3",
            "keyEnv": "VISIBLE_DEEPSEEK_KEY",
            "sources": [{"kind": "workspace", "label": "Ideas", "familyId": "idea"}],
        },
    )
    profiles_response = client.get("/desktop/ai/profiles", params={"project_root": "/tmp/PIHC3"})
    write_profile_response = client.put(
        "/desktop/ai/profiles/explain",
        json={
            "label": "Explain HoI4 code",
            "detail": "Custom PIHC3 explanation.",
            "prompt": "Prefer editable SDK prompts.",
            "sourceKinds": ["project", "selection"],
            "projectRoot": "/tmp/PIHC3",
        },
    )
    write_planned_profile_response = client.put(
        "/desktop/ai/profiles/explain",
        json={
            "profile": {
                "label": "Explain HoI4 code",
                "detail": "SDK-planned profile body.",
                "prompt": "Prefer editable SDK prompts.",
                "sourceKinds": ["project", "selection"],
            },
            "project_root": "/tmp/PIHC3",
        },
    )
    invalid_planned_profile_response = client.put(
        "/desktop/ai/profiles/explain",
        json={"profile": "bad", "project_root": "/tmp/PIHC3"},
    )
    reset_profile_response = client.delete("/desktop/ai/profiles/explain", params={"project_root": "/tmp/PIHC3"})

    assert status_response.status_code == 200, status_response.text
    assert status_response.json()["path"] == "/opt/homebrew/bin/magick"
    assert install_response.status_code == 200, install_response.text
    assert install_response.json()["installCommand"] == [
        "brew",
        "install",
        "imagemagick",
    ]
    assert llm_response.status_code == 200, llm_response.text
    assert llm_response.json()["model"] == "deepseek-v4-flash"
    assert llm_response.json()["preset"] == "reason"
    assert llm_response.json()["keySource"] == "VISIBLE_DEEPSEEK_KEY"
    assert llm_response.json()["resultCode"] == "ok"
    assert chat_response.status_code == 200, chat_response.text
    assert chat_response.json()["prompt"] == "Explain this idea."
    assert chat_response.json()["preset"] == "reason"
    assert chat_response.json()["projectRoot"] == "/tmp/PIHC3"
    assert chat_response.json()["keySource"] == "VISIBLE_DEEPSEEK_KEY"
    assert chat_response.json()["sources"] == [{"kind": "workspace", "label": "Ideas", "familyId": "idea"}]
    assert chat_response.json()["reply"] == "This idea grants a national spirit."
    assert profiles_response.status_code == 200, profiles_response.text
    assert profiles_response.json()["projectRoot"] == "/tmp/PIHC3"
    assert profiles_response.json()["profiles"][0]["id"] == "chat"
    assert write_profile_response.status_code == 200, write_profile_response.text
    assert write_profile_response.json()["profiles"][0]["id"] == "explain"
    assert write_planned_profile_response.status_code == 200, write_planned_profile_response.text
    assert write_planned_profile_response.json()["profiles"][0]["detail"] == "SDK-planned profile body."
    assert invalid_planned_profile_response.status_code == 400
    assert invalid_planned_profile_response.json()["detail"] == "AI chat profile override must be a JSON object."
    assert reset_profile_response.status_code == 200, reset_profile_response.text
    assert reset_profile_response.json()["projectRoot"] == "/tmp/PIHC3"
    assert written_profiles == [
        {
            "profile_id": "explain",
            "profile": {
                "label": "Explain HoI4 code",
                "detail": "Custom PIHC3 explanation.",
                "prompt": "Prefer editable SDK prompts.",
                "sourceKinds": ["project", "selection"],
            },
            "project_root": "/tmp/PIHC3",
        },
        {
            "profile_id": "explain",
            "profile": {
                "label": "Explain HoI4 code",
                "detail": "SDK-planned profile body.",
                "prompt": "Prefer editable SDK prompts.",
                "sourceKinds": ["project", "selection"],
            },
            "project_root": "/tmp/PIHC3",
        },
    ]
    assert reset_profiles == [{"profile_id": "explain", "project_root": "/tmp/PIHC3"}]


def test_desktop_binary_source_accepts_bytes_and_ints(tmp_path: Path) -> None:
    path = tmp_path / "asset.dds"

    assert desktop_binary_source(path, b"\x01\x02")["bytes"] == [1, 2]
    assert desktop_binary_source(path, [3, 4])["mimeType"] == "image/vnd.ms-dds"


def plain_json(value):
    if isinstance(value, (Mapping, MappingProxyType)):
        return {key: plain_json(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [plain_json(item) for item in value]
    return value


def test_desktop_api_selection_returns_table_row_and_index_projection() -> None:
    table = get_desktop_api_table()
    assert_api_selection_projection(
        get_desktop_api_selection,
        table,
        symbol="desktop_state",
        index_cases=(
            ("module_index", "desktop.api"),
            ("feature_index", "state"),
            ("kind_index", "function"),
        ),
    )


def test_desktop_api_selection_rejects_invalid_selectors() -> None:
    assert_api_selection_rejects_invalid_selectors(
        get_desktop_api_selection,
        symbol="desktop_state",
        index_name="module_index",
        key="desktop.api",
    )


def test_desktop_api_table_lists_selection_helper() -> None:
    table = get_desktop_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert table["row_count"] == len(desktop.__all__)
    assert table["module_index"]["desktop.api"] == [
        "DESKTOP_API_TABLE_SCHEMA",
        "DesktopApiRow",
        "DesktopApiTable",
        "get_desktop_api_selection",
        "get_desktop_api_table",
        "render_desktop_api_reference_markdown",
    ]
    assert table["feature_index"]["desktop-api"] == table["module_index"]["desktop.api"]
    assert row_by_symbol["get_desktop_api_selection"]["returns"] == "DesktopApiTable | DesktopApiRow | list[str]"
    assert row_by_symbol["get_desktop_api_selection"]["registry_seam"] == "desktop facade API table"


def test_desktop_api_table_lists_dependency_and_llm_route_helpers() -> None:
    from paradev.desktop import (
        desktop_dependency_status,
        desktop_install_dependency,
        desktop_test_llm_route,
    )

    table = get_desktop_api_table()
    row_by_symbol = {row["symbol"]: row for row in table["rows"]}

    assert callable(desktop_dependency_status)
    assert callable(desktop_install_dependency)
    assert callable(desktop_test_llm_route)
    assert table["feature_index"]["dependencies"] == [
        "desktop_dependency_status",
        "desktop_install_dependency",
    ]
    assert "desktop_test_llm_route" in table["feature_index"]["ai-chat"]
    assert row_by_symbol["desktop_dependency_status"]["registry_seam"] == "desktop dependency manager"
    assert row_by_symbol["desktop_install_dependency"]["registry_seam"] == "desktop dependency manager"
    assert row_by_symbol["desktop_test_llm_route"]["registry_seam"] == "HeavenBase desktop AI chat"


def test_desktop_api_reference_documents_selection_helper() -> None:
    reference = render_desktop_api_reference_markdown()

    assert "`get_desktop_api_selection`" in reference
    assert load_txt("docs/user-manual/desktop-api-reference.md") == reference
