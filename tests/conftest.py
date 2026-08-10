from __future__ import annotations

import os
import sys
import tempfile
from collections.abc import Iterator
from dataclasses import replace
from pathlib import Path

import pytest
from click import unstyle
from heavenbase import DEFAULT_CONTEXT
from heavenbase.backends.inmem.backend import InMemBackend
from heavenbase.context.reset import reset_default_local_state
from heavenbase.utils import CM_HVNB
from typer.testing import Result as TyperResult

_CLI_COLOR_ENV_BEFORE_TESTS = {
    "CLICOLOR_FORCE": os.environ.get("CLICOLOR_FORCE"),
    "FORCE_COLOR": os.environ.get("FORCE_COLOR"),
    "NO_COLOR": os.environ.get("NO_COLOR"),
}
os.environ.pop("CLICOLOR_FORCE", None)
os.environ.pop("FORCE_COLOR", None)
os.environ["NO_COLOR"] = "1"
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
sys.dont_write_bytecode = True

_TYPER_RESULT_OUTPUT_BEFORE_TESTS = TyperResult.output


def _plain_cli_test_output(result: TyperResult) -> str:
    output = result.output_bytes.decode(result.runner.charset, "replace")
    return unstyle(output.replace("\r\n", "\n"))


TyperResult.output = property(_plain_cli_test_output)

if os.name == "nt":
    import msvcrt
else:
    import fcntl


_PARADEV_ROOT_BEFORE_TESTS = os.environ.get("PARADEV_ROOT")
_PARADEV_TEST_ROOT = tempfile.TemporaryDirectory(prefix="paradev-pytest-")
os.environ["PARADEV_ROOT"] = _PARADEV_TEST_ROOT.name
_PIHC3_ROOT = Path(os.environ.get("PARADEV_PIHC3_ROOT", "projects/PIHC3")).expanduser().resolve()
_PIHC3_AVAILABLE = (_PIHC3_ROOT / "paradev.yaml").is_file()

# ParaDev resolves HeavenBase-backed type limits while pytest collects some
# test modules, before session fixtures run. Isolate the globals eagerly so
# collection cannot open the user's persistent HeavenBase backend.
_HEAVENBASE_TEST_ROOT = tempfile.TemporaryDirectory(prefix="heavenbase-pytest-")
CM_HVNB.root = _HEAVENBASE_TEST_ROOT.name
DEFAULT_CONTEXT.root = _HEAVENBASE_TEST_ROOT.name
DEFAULT_CONTEXT.bootstrap = replace(
    DEFAULT_CONTEXT.bootstrap,
    root=_HEAVENBASE_TEST_ROOT.name,
)
reset_default_local_state(DEFAULT_CONTEXT)
DEFAULT_CONTEXT._backend = InMemBackend(
    "system",
    ws_id="default",
    config=CM_HVNB,
)
DEFAULT_CONTEXT._owns_backend = False
CM_HVNB._bind_registry_factory(lambda: DEFAULT_CONTEXT.registry("system-config"))
CM_HVNB._clear_caches()
CM_HVNB.setup(reset=True)
DEFAULT_CONTEXT._setup_modules(force=True)
CM_HVNB.set("heavenbase.llm.default_preset", "mock")


def pytest_ignore_collect(collection_path: Path, config: pytest.Config) -> bool | None:
    """Avoid importing PIHC3-only modules without the companion project."""

    del config
    if not _PIHC3_AVAILABLE and collection_path.name.startswith("test_pihc3_"):
        return True
    return None


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip individual PIHC3 contracts in otherwise portable test modules."""

    del config
    if _PIHC3_AVAILABLE:
        return
    unavailable = pytest.mark.skip(reason=f"PIHC3 checkout not available at {_PIHC3_ROOT}")
    for item in items:
        if item.get_closest_marker("pihc3") is not None or "pihc3" in item.nodeid.casefold():
            item.add_marker(unavailable)


@pytest.fixture(autouse=True, scope="session")
def _isolate_heavenbase_config() -> Iterator[None]:
    try:
        yield
    finally:
        reset_default_local_state(DEFAULT_CONTEXT)
        CM_HVNB._clear_caches()
        _HEAVENBASE_TEST_ROOT.cleanup()


@pytest.fixture(autouse=True, scope="session")
def _paradev_test_config_root() -> Iterator[None]:
    try:
        yield
    finally:
        from paradev.config import _CONTEXT_PARADEV

        _CONTEXT_PARADEV.close()
        if _PARADEV_ROOT_BEFORE_TESTS is None:
            os.environ.pop("PARADEV_ROOT", None)
        else:
            os.environ["PARADEV_ROOT"] = _PARADEV_ROOT_BEFORE_TESTS
        TyperResult.output = _TYPER_RESULT_OUTPUT_BEFORE_TESTS
        for name, value in _CLI_COLOR_ENV_BEFORE_TESTS.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
        _PARADEV_TEST_ROOT.cleanup()


@pytest.fixture(autouse=True)
def _paradev_test_hoi4_mod_root(
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Give every test an isolated launcher root and publication owner."""

    mod_root = tmp_path_factory.mktemp("hoi4-mod-root")
    monkeypatch.setenv("PARADEV_HOI4_MOD_ROOT", str(mod_root))


@pytest.fixture
def cm_paradev_lock() -> Iterator[None]:
    path = Path(tempfile.gettempdir()) / "paradev-cm-paradev-test.lock"
    with path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
